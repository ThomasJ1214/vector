"""Build CE TI-BASIC files and audit actual executable tokens for OS 5.8.

A token round trip alone cannot detect a command encoded as ordinary letters.
"""
from pathlib import Path
import warnings
from tivars import TIProgram
from tivars.models import TI_84PCE
try:
    from tools.ti_syntax import audit_program
except ModuleNotFoundError:
    from ti_syntax import audit_program

ROOT = Path(__file__).resolve().parents[1]
TARGET_OS = TI_84PCE.OS('5.8')
# tivars' spellings include a space for commands with optional arguments.
# Keep that invisible tokenizer detail out of the human-readable source.
BARE_COMMANDS = {'Pause': b'\xd8', 'FnOff': b'\x97', 'PlotsOff': b'\xea'}


def tokenize_source(source, name='UNNAMED'):
    lines = source.strip().splitlines()
    if not all(line == line.strip() for line in lines):
        raise ValueError(f'{name}: unexpected leading/trailing source whitespace')
    normalized = '\n'.join(line + ' ' if line in BARE_COMMANDS else line for line in lines) + '\n'
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        program = TIProgram(name=name)
        program.load_string(normalized, model=TI_84PCE)
    validate_tokens(program, name)
    # Check the expected opcode at the exact source line, not just its presence.
    encoded = token_lines(program)
    if len(encoded) != len(lines):
        raise ValueError(f'{name}: source/token line count differs')
    for line_number, (source_line, data) in enumerate(zip(lines, encoded), 1):
        if source_line in BARE_COMMANDS and data != BARE_COMMANDS[source_line]:
            raise ValueError(f'{name}:{line_number}: {source_line} is not its command token')
    return program


def token_lines(program):
    lines = []
    current = bytearray()
    for token in program:
        if token.bits == b'\x3f':
            lines.append(bytes(current))
            current.clear()
        else:
            current.extend(token.bits)
    if current:
        lines.append(bytes(current))
    return lines


def supports_target_os(version):
    if version.model != TARGET_OS.model:
        # Library model ordering handles older calculator families.
        return version <= TARGET_OS
    current = tuple(int(part) for part in version.version.split('.'))
    target = tuple(int(part) for part in TARGET_OS.version.split('.'))
    width = max(len(current), len(target))
    return current + (0,) * (width-len(current)) <= target + (0,) * (width-len(target))


def validate_tokens(program, name='UNNAMED'):
    quoted = False
    line = 1
    for token in program:
        if token.bits == b'\x3f':
            if quoted:
                raise ValueError(f'{name}:{line}: unterminated string')
            line += 1
            continue
        if token.bits == b'\x2a':
            quoted = not quoted
            continue
        if not quoted:
            spelling = token.display
            if len(spelling) == 1 and ('a' <= spelling <= 'z' or spelling == ' '):
                raise ValueError(f'{name}:{line}: unexpected executable character {spelling!r}; '
                                 'a command may have been encoded as letters')
    if quoted:
        raise ValueError(f'{name}:{line}: unterminated string')
    if not supports_target_os(program.get_min_os()):
        raise ValueError(f'{name}: requires {program.get_min_os()}, newer than CE OS 5.8')


def build():
    out = ROOT / 'dist'
    out.mkdir(exist_ok=True)
    available = {p.stem for p in (ROOT / 'src').glob('*.txt')}
    for src in sorted((ROOT / 'src').glob('*.txt')):
        program = tokenize_source(src.read_text(encoding='utf-8'), src.stem)
        audit_program(program, src.stem, available)
        target = out / (src.stem + '.8xp')
        program.save(str(target), model=TI_84PCE)
        raw = target.read_bytes()
        assert raw[:8] == b'**TI83F*'
        size = int.from_bytes(raw[53:55], 'little')
        assert len(raw) == size + 57
        assert sum(raw[55:-2]) % 65536 == int.from_bytes(raw[-2:], 'little')
        # Audit the actual saved program too, rather than the source alone.
        saved = TIProgram.open(str(target))
        validate_tokens(saved, src.stem)
        audit = audit_program(saved, src.stem, available)
        assert bytes(saved.data) == bytes(program.data)
        q = TIProgram()
        q.load_string(saved.string(model=TI_84PCE), model=TI_84PCE)
        assert bytes(q.data) == bytes(program.data)
        print(f'{target.name}: {len(raw)} bytes; {audit["statements"]} lines syntax-audited; OS 5.8 tokens and checksum OK')


if __name__ == '__main__':
    build()

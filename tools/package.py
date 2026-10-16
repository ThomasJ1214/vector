"""Create a reproducible package with binaries, source, instructions and checksums."""
from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from tivars import TIProgram
try:
    from tools.build import tokenize_source, validate_tokens
    from tools.ti_syntax import audit_program
except ModuleNotFoundError:
    from build import tokenize_source, validate_tokens
    from ti_syntax import audit_program
ROOT = Path(__file__).resolve().parents[1]

def verify_programs(files):
    """Refuse stale, damaged, or unaudited calculator files before shipping."""
    available = {p.stem for p in (ROOT/'src').glob('*.txt')}
    if {p.stem for p in files} != available:
        raise ValueError('Calculator files do not match the source program names')
    for path in files:
        raw = path.read_bytes()
        if len(raw) < 57 or raw[:8] != b'**TI83F*':
            raise ValueError(f'{path.name}: invalid TI container')
        if len(raw) != int.from_bytes(raw[53:55], 'little') + 57:
            raise ValueError(f'{path.name}: incorrect container length')
        if sum(raw[55:-2]) % 65536 != int.from_bytes(raw[-2:], 'little'):
            raise ValueError(f'{path.name}: incorrect container checksum')
        expected = tokenize_source((ROOT/'src'/f'{path.stem}.txt').read_text(encoding='utf-8'), path.stem)
        saved = TIProgram.open(str(path))
        if saved.name != path.stem:
            raise ValueError(f'{path.name}: calculator program name does not match filename')
        if bytes(saved.data) != bytes(expected.data):
            raise ValueError(f'{path.name}: stale binary; rebuild from current source')
        validate_tokens(saved, path.stem)
        audit_program(saved, path.stem, available)

def package():
    out = ROOT / 'dist'
    files = sorted(out.glob('*.8xp'))
    assert len(files) == 8, 'Build all eight programs before packaging'
    verify_programs(files)
    checksums = out / 'SHA256SUMS'
    checksums.write_text(''.join(f'{sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in files),encoding='utf-8')
    included = [ROOT/'README.md', ROOT/'requirements-dev.txt', ROOT/'index.html', out/'try-vector.html', checksums, *files]
    for directory in ('src', 'docs', 'tools', 'tests', 'web'):
        included += sorted(p for p in (ROOT/directory).glob('*') if p.is_file())
    target = out / 'VECTORCE.zip'
    with ZipFile(target, 'w', compression=ZIP_DEFLATED) as z:
        for p in included:
            info = ZipInfo(str(p.relative_to(ROOT)), date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, p.read_bytes())
    for alias in ('VECTORCE-OS58.zip', 'VECTRA-CE-OS58.zip', 'VECTRA-CE-OS58-r4.zip'):
        (out / alias).write_bytes(target.read_bytes())
    print(f'{target.name}: {len(included)} files, {target.stat().st_size} bytes')

if __name__ == '__main__':
    package()

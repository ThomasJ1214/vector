"""Tokenize TI-BASIC source with the CE token table; check container checksums."""
from pathlib import Path
import warnings
from tivars import TIProgram
ROOT = Path(__file__).resolve().parents[1]

def build():
    out = ROOT / 'dist'
    out.mkdir(exist_ok=True)
    for src in sorted((ROOT / 'src').glob('*.txt')):
        text = src.read_text(encoding="utf-8").strip() + '\n'
        assert all(line == line.strip() for line in text.splitlines()), 'Unexpected leading/trailing whitespace'
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            p = TIProgram(name=src.stem)
            p.load_string(text)
            target = out / (src.stem + '.8xp')
            p.save(str(target))
        raw = target.read_bytes()
        assert raw[:8] == b'**TI83F*'
        size = int.from_bytes(raw[53:55], 'little')
        assert len(raw) == size + 57
        assert sum(raw[55:-2]) % 65536 == int.from_bytes(raw[-2:], 'little')
        # A token round trip catches dropped/unrepresentable input.
        q = TIProgram()
        q.load_string(p.string())
        assert bytes(q.data) == bytes(p.data)
        print(f'{target.name}: {len(raw)} bytes; checksum and token round trip OK')

if __name__ == '__main__':
    build()

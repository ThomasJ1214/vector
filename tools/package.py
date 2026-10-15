"""Create a reproducible package with binaries, source, instructions and checksums."""
from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
ROOT = Path(__file__).resolve().parents[1]

def package():
    out = ROOT / 'dist'
    files = sorted(out.glob('*.8xp'))
    assert len(files) == 8, 'Build all eight programs before packaging'
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
    (out / 'VECTORCE-OS58.zip').write_bytes(target.read_bytes())
    print(f'{target.name}: {len(included)} files, {target.stat().st_size} bytes')

if __name__ == '__main__':
    package()

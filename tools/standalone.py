"""Bundle the interactive demo into one HTML file for offline use."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=(ROOT/'index.html').read_text(encoding="utf-8")
for name in ('math','app'):
    s=s.replace(f'<script src="web/{name}.js"></script>','<script>\n'+(ROOT/f'web/{name}.js').read_text(encoding="utf-8")+'\n</script>')
s=s.replace('href="dist/VECTORCE.zip"','href="VECTORCE.zip"').replace('href="README.md"','href="../README.md"')
p=ROOT/'dist/try-vector.html';p.write_text(s,encoding="utf-8");print(f'{p.name}: standalone interactive demo, {p.stat().st_size} bytes')

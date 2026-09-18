"""Make a portable ZIP without environment, cache or Git files."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
ROOT = Path(__file__).resolve().parent
output = ROOT.parent / 'SIT720_8_1D_submission.zip'
excluded = {'.git', '.venv', '__pycache__', '.ipynb_checkpoints', 'node_modules'}
files = sorted(p for p in ROOT.rglob('*') if p.is_file()
               and not any(part in excluded for part in p.relative_to(ROOT).parts)
               and p.suffix not in {'.pyc', '.zip'}
               and not p.name.startswith('.env'))
with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
    for path in files:
        archive.write(path, Path('SIT720_8_1D') / path.relative_to(ROOT))
with ZipFile(output) as archive:
    assert archive.testzip() is None
print(f'Created {output} with {len(files)} files.')

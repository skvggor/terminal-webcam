"""Build the landing page: minify HTML/CSS/JS from web/ into docs/."""

import shutil
from pathlib import Path

import minify_html
import rcssmin
import rjsmin

ROOT = Path(__file__).parent
SOURCE = ROOT / 'web'
OUTPUT = ROOT / 'docs'

MINIFIERS = {
    '.css': rcssmin.cssmin,
    '.js': rjsmin.jsmin,
}


def build(source=SOURCE, output=OUTPUT):
    """Minify text assets from `source` into `output`, copying everything else verbatim."""
    source = Path(source)
    output = Path(output)

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    total_before = 0
    total_after = 0

    for path in sorted(source.rglob('*')):
        if path.is_dir():
            continue

        target = output / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)

        if path.name == 'index.html':
            minified = minify_html.minify(path.read_text(), minify_css=False, minify_js=False)
            target.write_text(minified)
        elif path.suffix in MINIFIERS:
            target.write_text(MINIFIERS[path.suffix](path.read_text()))
        else:
            shutil.copy2(path, target)

        before = path.stat().st_size
        after = target.stat().st_size
        total_before += before
        total_after += after
        if path.suffix in {'.html', '.css', '.js'}:
            print(f'  {path.relative_to(source)}: {before:,} -> {after:,} bytes')

    print(f'total: {total_before:,} -> {total_after:,} bytes')


if __name__ == '__main__':  # pragma: no cover
    build()

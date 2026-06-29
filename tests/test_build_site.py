import build_site


def _make_source(root):
    (root / 'css').mkdir(parents=True)
    (root / 'assets').mkdir()
    (root / 'index.html').write_text(
        '<!doctype html>\n<html>\n  <head>\n    <title>Hi</title>\n  </head>\n'
        '  <body>\n    <h1>Hi</h1>\n  </body>\n</html>\n'
    )
    (root / 'css' / 'style.css').write_text('body {\n  color: red;\n}\n')
    (root / 'app.js').write_text('const value = 1;\nconsole.log(value);\n')
    (root / 'assets' / 'data.bin').write_bytes(b'\x00\x01\x02')


def test_build_minifies_text_and_copies_assets(tmp_path):
    source = tmp_path / 'web'
    output = tmp_path / 'docs'
    _make_source(source)

    build_site.build(source, output)

    css = (output / 'css' / 'style.css').read_text()
    assert 'color:red' in css.replace(' ', '')
    assert len(css) < len((source / 'css' / 'style.css').read_text())

    js = (output / 'app.js').read_text()
    assert 'console.log' in js
    assert len(js) < len((source / 'app.js').read_text())

    html = (output / 'index.html').read_text()
    assert '<h1>Hi</h1>' in html
    assert len(html) < len((source / 'index.html').read_text())

    assert (output / 'assets' / 'data.bin').read_bytes() == b'\x00\x01\x02'


def test_build_clears_previous_output(tmp_path):
    source = tmp_path / 'web'
    output = tmp_path / 'docs'
    _make_source(source)
    output.mkdir()
    (output / 'stale.txt').write_text('old')

    build_site.build(source, output)

    assert not (output / 'stale.txt').exists()
    assert (output / 'index.html').exists()

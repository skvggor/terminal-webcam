# Terminal Webcam

This project captures images from your webcam and displays them in the terminal. There are two versions of the script: `capture.py` which displays monochrome webcam output, and `color.py` which displays colored webcam output.

<!-- image 500x500 -->
<img src="./monochrome_example.png" alt="Monochrome Example" width="500"/>
<!-- ![Monochrome Example](./monochrome_example.png) -->

**Monochrome Example**

<img src="./colored_example.png" alt="Colored Example" width="500"/>
<!-- ![Colored Example](./colored_example.png) -->

**Colored Example**

## Running the project

This project is meant to be run on Linux and uses [uv](https://docs.astral.sh/uv/) for dependency management.

1. First, clone the repository:

```
git clone https://github.com/skvggor/terminal-webcam.git
```

2. Navigate into the project directory:

```
cd terminal-webcam
```

3. Install the dependencies (uv creates the virtual environment automatically):

```
uv sync
```

4. Run the scripts:

For monochrome webcam output:

```
uv run capture.py
```

For colored webcam output:

```
uv run color.py
```

List the available webcams and the detected terminal aspect ratio with
`-l`/`--list`:

```
uv run capture.py --list
```

```
Webcams:
  [0] Integrated Camera (1280x720)
  [2] Logitech BRIO (4096x2160)

Detected terminal cell aspect ratio: 2.00
Run with --device <index>; if the image looks squished, tune --aspect.
```

If more than one webcam is connected, you'll also be asked which one to use. You
can pick it directly with the `-d`/`--device` flag:

```
uv run capture.py --device 2
```

The image is cropped to a centered square and the aspect ratio is preserved, so
it never looks stretched. The terminal cell ratio is auto-detected (shown by
`--list`); if your terminal doesn't report it and the image still looks
squished, tune it manually with `--aspect` (larger means wider):

```
uv run capture.py --aspect 2.2
```

The render loop is capped at 30 FPS to keep CPU usage low. Adjust it with
`--fps`:

```
uv run capture.py --fps 15
```

To quit the application, press `ESC` or `Ctrl + C` in the terminal.

Note: You'll need a webcam connected to your computer for this to work. Enjoy using your webcam in the terminal!

## Development

Run the tests:

```
uv run pytest
```

Lint and format the code:

```
uv run ruff check .
uv run ruff format .
```

### Landing page

The site source lives in `web/` (editable). The minified build is generated
into `docs/`, which is git-ignored: GitHub Actions builds and deploys it to
GitHub Pages on every push to `main` (see `.github/workflows/deploy-site.yml`).
Set the repository's Pages source to "GitHub Actions" once, in Settings → Pages.

Preview the readable source locally:

```
python3 -m http.server --directory web
```

Build the minified output yourself (optional, e.g. to inspect it):

```
uv run python build_site.py
```

This minifies the HTML/CSS/JS into `docs/` and copies the assets verbatim.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

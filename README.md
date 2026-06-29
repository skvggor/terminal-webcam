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

If more than one webcam is connected, you'll be asked which one to use. You can
also pick it directly with the `-d`/`--device` flag:

```
uv run capture.py --device 1
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

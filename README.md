# Summer Code Jam 2021

### For our Code Jam project, we decided to make a retro style console, with 3 games, that could be opened.
* Games:
    * Pong
    * Snake
    * MineSweeper

## Frameworks
- [Curses](https://pypi.org/project/windows-curses/)
- [Nurses](https://github.com/salt-die/nurses)
- [NumPy](https://pypi.org/project/numpy/)
- Developed and tested on Windows 10

## How to Run:
 1) Install all dependences `poetry install`
    - Make sure poetry is installed with `pip install poetry`
    - On windows, use `poetry install -E windows`
 2) Run `gameboy.py` with the command `poetry run python gameboy.py`
 3) Keybinds:
    * Open Games
        * 1 -> Snake
        * 2 -> Pong
        * 3-> MineSweeper
    * Escape -> Exit
### N.-B.
MineSweeper requires the [nurses](https://github.com/salt-die/nurses) library, and is developed and tested with the `nurses` code from this [commit](https://github.com/salt-die/nurses/commit/7090280fd48e3b9503f96b3b30b45d12fc6f4033).

## Troubleshoot:
### `gameboy.py` failed to start:
`gameboy.py` requires a big screen (with at least 1080p) to render the images with `curses`. Usually this means *fullscreening the terminal window*.

### `nurses` dependencies are broken:
The `nurses` library was not included in this repo, because the pre-commit hooks (specifically ISort) messed up the code in that library. After the deadline (but too late), we figured out that adding `exclude: nurses` to [.pre-commit-config.yaml](.pre-commit-config.yaml) will prevent the pre-commit hooks to change the library code.

Download the `nurses` library, and place the `nurses/nurses` directory (whose content are [here](https://github.com/salt-die/nurses/tree/master/nurses)) in the same directory as [mine.py](mine.py).

In case where the damage has already been done to `nurses/`, simply replace the `nurses/` folder with the original files.

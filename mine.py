import numpy as np

from nurses import ScreenManager, Widget, colors
from nurses.widgets import ArrayWin
from nurses.widgets.behaviors import Movable

# Keybindings
SPACE, RESET = ord(' '), ord('r')
FORFEIT_KEY = ord('g')
FLAG_KEY = ord('f')
OFFSET_TOP, OFFSET_LEFT = 5, 25
DELTA = .1

# Symbols
UNTOUCHED_SYMBOL = '❑'
EMPTY_SYMBOL = '⯀'
MINE_SYMBOL = '☠'
FLAG_SYMBOL = '☢'
HAPPYFACE_SYMBOL = '☺'
SADFACE_SYMBOL = '☹'
CURSOR_SYMBOL = 'ᐁ'
BOXEDCHECK_SYMBOL = '☑'
BOXEDCROSS_SYMBOL = '☒'

# States
UNVISITED = 0
VISITED = 1
FLAGGED = 2


class Cursor(Widget, Movable):
    """Movable cursor to point to a land location."""

    offset_top = OFFSET_TOP
    offset_left = OFFSET_LEFT

    def __init__(self, wrap_height: int, wrap_width: int, *args, **kwargs):
        self.wrap_height = wrap_height
        self.wrap_width = wrap_width
        super().__init__(*args, **kwargs)


class Lawn(ArrayWin):
    """MineSweeper Game Board."""

    def __init__(self, rows: int, cols: int, num_mines: int, *args, **kwargs) -> None:

        # Initialize display from ArrayWin
        super().__init__(OFFSET_TOP, OFFSET_LEFT, rows, cols, *args, **kwargs)

        self.shape = rows, cols
        self.num_mines = num_mines

        # Game board records the state of each cell
        self.board_map = np.zeros((rows, cols)).astype(int)

        # Initialize with given mine amount
        self.mine_map = np.r_[np.full(rows * cols - num_mines, False), np.full(num_mines, True)]
        self.solution_map = np.zeros((rows, cols)).astype(int)

        # Scoreboard display scores and shoutout banner
        self.scoreboard = gsm.root.new_widget(OFFSET_TOP + rows + 2, OFFSET_LEFT, 2, max(8, cols),
                                              color=colors.YELLOW_ON_BLACK, create_with="ArrayWin")

    def marching_scoreboard(self) -> None:
        """Animate scoreboard with marching texts."""
        head = self.scoreboard[1, 0]
        tail = self.scoreboard[1, 1:]
        self.scoreboard[1, :-1] = tail
        self.scoreboard[1, -1] = head

    def init_lawn(self) -> None:
        """Initialize game board for the next game."""
        self[:, :] = UNTOUCHED_SYMBOL

        # Display the game board
        self.revealed = False

        # Clear the game board
        self.board_map[:, :] = UNVISITED

        # Randomize mine locations
        self.mine_map = self.mine_map.reshape(-1)
        np.random.shuffle(self.mine_map)
        self.mine_map = self.mine_map.reshape(self.shape)

        self.solution_map = self.build_solution()

        # Erase shoutout text
        self.scoreboard[:, :] = ' '
        self.scoreboard[1, :8] = "Welcome!"

        self.marching = gsm.schedule(self.marching_scoreboard, delay=.3, n=120)

        # Unset timer
        self.timer = None

    def build_solution(self) -> np.ndarray:
        """Count mines near each land in adjacent lands."""
        rows, cols = self.shape
        solution_map = np.zeros((rows, cols)).astype(int)

        for r in range(rows):
            for c in range(cols):
                solution_map[r, c] = self.mine_map[
                    max(0, r - 1):min(r + 2, rows),
                    max(0, c - 1):min(c + 2, cols)
                ].sum()

        solution_map = solution_map.astype(str)
        solution_map[solution_map == '0'] = EMPTY_SYMBOL
        return solution_map

    def reveal_mines(self) -> None:
        """Reveal mine locations."""
        if not self.revealed:
            self.revealed = True
            self[:, :] = np.where(self.mine_map, MINE_SYMBOL, self[:, :])

    def refresh(self) -> None:
        """Handle terminal display refresh."""
        if self.timer and not self.revealed:
            self.scoreboard[0, -3:] = str(int(self.timer)).rjust(3, '0')
            self.timer += DELTA
            self.scoreboard[0, :3] = str(self.num_mines - (self.board_map == FLAGGED).sum()).rjust(3, '0')
        return super().refresh()

    def on_press(self, key: int) -> bool:
        """Handle key press events."""
        # Initialize timer
        if not self.timer:
            self.timer = DELTA
            self.scoreboard[1, :] = ' '
            self.marching.cancel()

        if key in FORFEIT_KEY:
            self.reveal_mines()
        elif key == RESET:
            self.init_lawn()
        elif not self.revealed:
            if key == SPACE:
                self.poke()
            if key == FLAG_KEY:
                self.flag()
        else:
            return super().on_press(key)
        return True

    def flag(self) -> None:
        """Flag the location for potential mine."""
        row, col = cursor.top - OFFSET_TOP, cursor.left - OFFSET_LEFT
        if self.board_map[row, col] == UNVISITED:
            self.board_map[row, col] = FLAGGED
            self[row, col] = FLAG_SYMBOL
        elif self.board_map[row, col] == FLAGGED:
            self.board_map[row, col] = UNVISITED
            self[row, col] = UNTOUCHED_SYMBOL

    def poke(self) -> None:
        """Expand the pointed location."""
        row, col = cursor.top - OFFSET_TOP, cursor.left - OFFSET_LEFT
        rows, cols = self.shape

        if self.board_map[row, col] != UNVISITED:
            return

        def expand_land(r: int, c: int) -> None:
            """Expand adjacent locations when the adjacent mine count is 0."""
            if not (0 <= r < rows and 0 <= c < cols) or expands[r, c] == VISITED:
                return
            expands[r, c] = VISITED

            # Expand the 8 adjacent locations
            if self.solution_map[r, c] == EMPTY_SYMBOL:
                for rr in range(r - 1, r + 2):
                    for cc in range(c - 1, c + 2):
                        if not (rr == r and cc == c):
                            expand_land(rr, cc)

        if self.mine_map[row, col]:
            self.lose(row, col)
        else:
            expands = self.board_map.copy()
            expand_land(row, col)
            self.board_map = expands
            self[:, :] = np.where(self.board_map == VISITED, self.solution_map, self[:, :])
            self.evaluate()

    def win(self) -> None:
        """Handle winning."""
        self[:, :] = np.where(self.mine_map,
                              BOXEDCHECK_SYMBOL, self.solution_map)

        self.scoreboard[0, len(self.scoreboard[0]) // 2] = HAPPYFACE_SYMBOL
        self.scoreboard[1, :8] = "You win!"
        self.marching = gsm.schedule(self.marching_scoreboard, delay=.1, n=120)

        self.revealed = True

    def lose(self, r: int, c: int) -> None:
        """Handle losing."""
        self[:, :] = np.where(self.mine_map,
                              np.where(self.board_map == FLAGGED, BOXEDCHECK_SYMBOL, MINE_SYMBOL),
                              np.where(self.board_map == FLAGGED, BOXEDCROSS_SYMBOL, self.solution_map))

        if r and c:
            colors_copy = np.full(self.shape, self.color)
            colors_copy[r, c] = colors.WHITE_ON_RED
            self.colors = colors_copy

        self.scoreboard[0, len(self.scoreboard[0]) // 2] = SADFACE_SYMBOL
        self.scoreboard[1, :8] = "You die!"
        self.marching = gsm.schedule(self.marching_scoreboard, delay=.8, n=120)

        self.revealed = True

    def evaluate(self) -> None:
        """Evaluate winning or losing."""
        if np.all(self.mine_map == (self.board_map != VISITED)):
            self.win()
        elif (self.board_map != VISITED).sum() == self.num_mines:
            row, col = cursor.top - OFFSET_TOP, cursor.left - OFFSET_LEFT
            self.lose(row, col)


with ScreenManager() as gsm:
    num_mines = 10
    rows, cols = 8, 8

    lawn = gsm.root.new_widget(rows=rows, cols=cols, num_mines=num_mines, create_with=Lawn)
    lawn.init_lawn()

    cursor = gsm.root.new_widget(rows, cols, OFFSET_TOP, OFFSET_LEFT, 1, 1, transparent=True, create_with=Cursor)
    cursor.window.addstr(0, 0, CURSOR_SYMBOL)

    gsm.schedule(gsm.root.refresh, delay=DELTA)
    gsm.run()

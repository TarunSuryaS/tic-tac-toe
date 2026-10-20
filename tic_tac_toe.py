"""
Tic Tac Toe - a desktop game made with Python and Tkinter.

How to run:
    python tic_tac_toe.py        (Windows - or: py tic_tac_toe.py)
    python3 tic_tac_toe.py       (macOS / Linux)

Features:
    - Two modes: play against the computer, or 2 players on one computer
    - Computer difficulty: Easy, Medium, Hard (Hard never loses)
    - Scoreboard for wins and draws
    - The winning line is drawn across the board
    - The starting player switches every round
    - Click a square, or press keys 1-9 (1 = top-left, 9 = bottom-right)

Only the Python standard library is used - there is nothing to pip install.
"""

import random
import tkinter as tk
from functools import lru_cache

# ---------------------------------------------------------------------------
# Look and feel
# ---------------------------------------------------------------------------
CELL_SIZE = 120                 # size of one square, in pixels
BOARD_SIZE = CELL_SIZE * 3
GRID_WIDTH = 4                  # thickness of the board lines
MARK_WIDTH = 10                 # thickness of the X and O strokes
MARK_PADDING = 28               # gap between a mark and the edge of its square
COMPUTER_DELAY_MS = 450         # short pause so you can see the computer move

FONT = "Helvetica"
COLORS = {
    "bg": "#1f2233",
    "board": "#2a2e45",
    "grid": "#4a5072",
    "hover": "#353a58",
    "x": "#ff6b6b",
    "o": "#4ecdc4",
    "win": "#ffd93d",
    "text": "#ecedf5",
    "muted": "#9aa0bf",
}

# The 8 ways to get three in a row.
# Squares are numbered 0-8: left to right, top to bottom.
WIN_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # columns
    (0, 4, 8), (2, 4, 6),              # diagonals
)


# ---------------------------------------------------------------------------
# Game logic (no Tkinter in this part, so it is easy to test on its own)
# ---------------------------------------------------------------------------
def other_player(player):
    """Return the opponent of 'X' or 'O'."""
    return "O" if player == "X" else "X"


def find_winner(board):
    """Check the board.

    Returns (result, line):
        result is 'X' or 'O' (someone won), 'Draw', or None (game still on)
        line is the three winning squares, or None
    """
    for a, b, c in WIN_LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a], (a, b, c)
    if all(board):
        return "Draw", None
    return None, None


def empty_squares(board):
    """List of the square numbers that are still free."""
    return [i for i, mark in enumerate(board) if not mark]


@lru_cache(maxsize=None)
def minimax(board, to_move, me):
    """Score a position for player `me`, with `to_move` playing next.

    This tries every possible future move (the minimax algorithm).
    Positive score = good for `me`, negative = bad, 0 = draw.
    Faster wins score higher, so the computer finishes the game quickly.
    `board` must be a tuple so results can be cached with lru_cache.
    """
    result, _ = find_winner(board)
    if result == "Draw":
        return 0
    if result is not None:
        bonus = len(empty_squares(board)) + 1
        return bonus if result == me else -bonus

    scores = []
    for square in empty_squares(board):
        next_board = board[:square] + (to_move,) + board[square + 1:]
        scores.append(minimax(next_board, other_player(to_move), me))
    return max(scores) if to_move == me else min(scores)


def best_move(board, player):
    """Return the strongest square for `player` (random pick among ties)."""
    board = tuple(board)
    best_score = None
    best_squares = []
    for square in empty_squares(board):
        next_board = board[:square] + (player,) + board[square + 1:]
        score = minimax(next_board, other_player(player), player)
        if best_score is None or score > best_score:
            best_score, best_squares = score, [square]
        elif score == best_score:
            best_squares.append(square)
    return random.choice(best_squares)


def choose_computer_move(board, player, difficulty):
    """Pick the computer's move based on the difficulty level."""
    free = empty_squares(board)
    if difficulty == "Easy":
        return random.choice(free)                  # always random
    if difficulty == "Medium" and random.random() < 0.4:
        return random.choice(free)                  # sometimes makes mistakes
    return best_move(board, player)                 # Hard: perfect play


# ---------------------------------------------------------------------------
# The window (Tkinter user interface)
# ---------------------------------------------------------------------------
class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(False, False)

        # Settings chosen with the radio buttons
        self.mode = tk.StringVar(value="computer")      # "computer" or "pvp"
        self.difficulty = tk.StringVar(value="Hard")    # "Easy", "Medium", "Hard"
        self.human, self.computer = "X", "O"            # used in vs-computer mode

        # Game state
        self.scores = {"X": 0, "O": 0, "Draw": 0}
        self.board = [""] * 9
        self.current = "X"          # whose turn it is
        self.round_starter = "X"    # who started this round
        self.game_over = False
        self.win_line = None
        self.hover_square = None
        self.pending_move = None    # the computer's scheduled move (root.after id)

        self.build_ui()
        self.update_score_names()
        self.new_round(switch_starter=False)
        self.center_window()

    # ----- building the window -------------------------------------------
    def build_ui(self):
        bg = COLORS["bg"]

        tk.Label(self.root, text="Tic Tac Toe", font=(FONT, 26, "bold"),
                 fg=COLORS["text"], bg=bg).pack(pady=(18, 6))

        # Mode and difficulty choices
        self.make_radio_row("Mode:", self.mode,
                            [("vs Computer", "computer"), ("2 Players", "pvp")])
        self.difficulty_buttons = self.make_radio_row(
            "Level:", self.difficulty,
            [("Easy", "Easy"), ("Medium", "Medium"), ("Hard", "Hard")])

        # Scoreboard
        score_frame = tk.Frame(self.root, bg=bg)
        score_frame.pack(pady=(12, 2))
        score_colors = {"X": COLORS["x"], "Draw": COLORS["muted"], "O": COLORS["o"]}
        self.score_names = {}
        self.score_values = {}
        for column, key in enumerate(("X", "Draw", "O")):
            name = tk.Label(score_frame, font=(FONT, 11, "bold"),
                            fg=score_colors[key], bg=bg, width=13)
            name.grid(row=0, column=column)
            value = tk.Label(score_frame, text="0", font=(FONT, 24, "bold"),
                             fg=COLORS["text"], bg=bg)
            value.grid(row=1, column=column)
            self.score_names[key] = name
            self.score_values[key] = value

        # Status line ("Your turn", "Player O wins!", ...)
        self.status = tk.Label(self.root, font=(FONT, 15, "bold"), bg=bg)
        self.status.pack(pady=(6, 10))

        # The board is drawn on a Canvas
        self.canvas = tk.Canvas(self.root, width=BOARD_SIZE, height=BOARD_SIZE,
                                bg=COLORS["board"], highlightthickness=0,
                                cursor="hand2")
        self.canvas.pack(padx=28)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Leave>", lambda event: self.set_hover(None))

        # Buttons
        buttons = tk.Frame(self.root, bg=bg)
        buttons.pack(pady=(16, 6))
        tk.Button(buttons, text="New Round", width=12, font=(FONT, 11),
                  command=self.new_round).pack(side="left", padx=6)
        tk.Button(buttons, text="Reset Scores", width=12, font=(FONT, 11),
                  command=self.reset_scores).pack(side="left", padx=6)

        self.hint = tk.Label(self.root, font=(FONT, 10),
                             fg=COLORS["muted"], bg=bg)
        self.hint.pack(pady=(4, 16))

        # Keyboard shortcuts: 1-9 place a mark, N starts a new round
        for number in range(1, 10):
            self.root.bind(str(number),
                           lambda event, square=number - 1: self.human_move(square))
        self.root.bind("n", lambda event: self.new_round())
        self.root.bind("N", lambda event: self.new_round())

    def make_radio_row(self, label, variable, choices):
        """Create a row of radio buttons and return them as a list."""
        row = tk.Frame(self.root, bg=COLORS["bg"])
        row.pack(pady=2)
        tk.Label(row, text=label, width=6, anchor="e", font=(FONT, 11),
                 fg=COLORS["muted"], bg=COLORS["bg"]).pack(side="left")
        radios = []
        for text, value in choices:
            radio = tk.Radiobutton(
                row, text=text, value=value, variable=variable,
                command=self.on_settings_changed, font=(FONT, 11),
                fg=COLORS["text"], bg=COLORS["bg"],
                activeforeground=COLORS["text"], activebackground=COLORS["bg"],
                selectcolor=COLORS["board"], disabledforeground=COLORS["grid"],
                highlightthickness=0)
            radio.pack(side="left", padx=6)
            radios.append(radio)
        return radios

    def center_window(self):
        self.root.update_idletasks()
        width, height = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 3
        self.root.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    # ----- drawing the board ---------------------------------------------
    def square_box(self, square):
        """Pixel corners (x0, y0, x1, y1) of a square."""
        row, column = divmod(square, 3)
        x0, y0 = column * CELL_SIZE, row * CELL_SIZE
        return x0, y0, x0 + CELL_SIZE, y0 + CELL_SIZE

    def square_center(self, square):
        x0, y0, x1, y1 = self.square_box(square)
        return (x0 + x1) / 2, (y0 + y1) / 2

    def draw_board(self):
        canvas = self.canvas
        canvas.delete("all")

        # Highlight the square under the mouse
        if self.hover_square is not None:
            x0, y0, x1, y1 = self.square_box(self.hover_square)
            canvas.create_rectangle(x0 + 6, y0 + 6, x1 - 6, y1 - 6,
                                    fill=COLORS["hover"], outline="")

        # Grid lines
        margin = 14
        for k in (1, 2):
            p = k * CELL_SIZE
            canvas.create_line(p, margin, p, BOARD_SIZE - margin,
                               fill=COLORS["grid"], width=GRID_WIDTH, capstyle=tk.ROUND)
            canvas.create_line(margin, p, BOARD_SIZE - margin, p,
                               fill=COLORS["grid"], width=GRID_WIDTH, capstyle=tk.ROUND)

        # X and O marks (winning marks turn yellow)
        winning = self.win_line or ()
        for square, mark in enumerate(self.board):
            if not mark:
                continue
            color = COLORS["win"] if square in winning else COLORS[mark.lower()]
            if mark == "X":
                self.draw_x(square, color)
            else:
                self.draw_o(square, color)

        if self.win_line:
            self.draw_win_line(self.win_line)

    def draw_x(self, square, color):
        x0, y0, x1, y1 = self.square_box(square)
        p = MARK_PADDING
        self.canvas.create_line(x0 + p, y0 + p, x1 - p, y1 - p,
                                fill=color, width=MARK_WIDTH, capstyle=tk.ROUND)
        self.canvas.create_line(x0 + p, y1 - p, x1 - p, y0 + p,
                                fill=color, width=MARK_WIDTH, capstyle=tk.ROUND)

    def draw_o(self, square, color):
        x0, y0, x1, y1 = self.square_box(square)
        p = MARK_PADDING
        self.canvas.create_oval(x0 + p, y0 + p, x1 - p, y1 - p,
                                outline=color, width=MARK_WIDTH)

    def draw_win_line(self, line):
        (xa, ya), (xc, yc) = self.square_center(line[0]), self.square_center(line[2])
        dx, dy = xc - xa, yc - ya
        length = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / length, dy / length
        extra = CELL_SIZE * 0.35          # stretch the line a bit past the marks
        self.canvas.create_line(xa - ux * extra, ya - uy * extra,
                                xc + ux * extra, yc + uy * extra,
                                fill=COLORS["win"], width=6, capstyle=tk.ROUND)

    # ----- text on screen --------------------------------------------------
    def update_score_names(self):
        if self.mode.get() == "computer":
            self.score_names["X"].config(text="You (X)")
            self.score_names["O"].config(text="Computer (O)")
        else:
            self.score_names["X"].config(text="Player X")
            self.score_names["O"].config(text="Player O")
        self.score_names["Draw"].config(text="Draws")

    def update_status(self):
        if self.mode.get() == "computer":
            text = "Your turn (X)" if self.current == self.human else "Computer is thinking..."
        else:
            text = f"Player {self.current}'s turn"
        color = COLORS["x"] if self.current == "X" else COLORS["o"]
        self.status.config(text=text, fg=color)

    # ----- mouse and keyboard ----------------------------------------------
    def square_at(self, x, y):
        """Which square (0-8) is at pixel (x, y), or None."""
        column, row = x // CELL_SIZE, y // CELL_SIZE
        if 0 <= column < 3 and 0 <= row < 3:
            return row * 3 + column
        return None

    def on_click(self, event):
        if self.game_over:              # click after a finished game = play again
            self.new_round()
            return
        square = self.square_at(event.x, event.y)
        if square is not None:
            self.human_move(square)

    def on_mouse_move(self, event):
        self.set_hover(self.square_at(event.x, event.y))

    def set_hover(self, square):
        if square is not None and (self.game_over or self.board[square]
                                   or self.is_computer_turn()):
            square = None
        if square != self.hover_square:
            self.hover_square = square
            self.draw_board()

    # ----- playing ----------------------------------------------------------
    def is_computer_turn(self):
        return self.mode.get() == "computer" and self.current == self.computer

    def human_move(self, square):
        if self.game_over or self.is_computer_turn() or self.board[square]:
            return
        self.place_mark(square)

    def computer_turn(self):
        self.pending_move = None
        if self.game_over or not self.is_computer_turn():
            return
        square = choose_computer_move(self.board, self.computer, self.difficulty.get())
        self.place_mark(square)

    def schedule_computer_turn(self):
        self.pending_move = self.root.after(COMPUTER_DELAY_MS, self.computer_turn)

    def place_mark(self, square):
        self.board[square] = self.current
        self.hover_square = None
        result, line = find_winner(self.board)
        if result:
            self.end_round(result, line)
        else:
            self.current = other_player(self.current)
            self.update_status()
            if self.is_computer_turn():
                self.schedule_computer_turn()
        self.draw_board()

    def end_round(self, result, line):
        self.game_over = True
        self.win_line = line
        self.scores[result] += 1
        self.score_values[result].config(text=str(self.scores[result]))

        if result == "Draw":
            text, color = "It's a draw!", COLORS["muted"]
        elif self.mode.get() == "computer":
            text = "You win!" if result == self.human else "Computer wins!"
            color = COLORS["win"]
        else:
            text, color = f"Player {result} wins!", COLORS["win"]
        self.status.config(text=text, fg=color)
        self.hint.config(text="Click the board or press N to play again")

    def new_round(self, switch_starter=True):
        if self.pending_move is not None:       # cancel a computer move in progress
            self.root.after_cancel(self.pending_move)
            self.pending_move = None
        if switch_starter:
            self.round_starter = other_player(self.round_starter)

        self.board = [""] * 9
        self.current = self.round_starter
        self.game_over = False
        self.win_line = None
        self.hover_square = None
        self.hint.config(text="Click a square or press 1-9   |   N = new round")
        self.update_status()
        self.draw_board()
        if self.is_computer_turn():
            self.schedule_computer_turn()

    def reset_scores(self):
        self.scores = {"X": 0, "O": 0, "Draw": 0}
        for label in self.score_values.values():
            label.config(text="0")
        self.round_starter = "X"
        self.new_round(switch_starter=False)

    def on_settings_changed(self):
        """Mode or difficulty changed: update labels and start fresh."""
        state = "normal" if self.mode.get() == "computer" else "disabled"
        for radio in self.difficulty_buttons:
            radio.config(state=state)
        self.update_score_names()
        self.reset_scores()


def main():
    root = tk.Tk()
    TicTacToeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

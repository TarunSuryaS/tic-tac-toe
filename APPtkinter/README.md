# Tic Tac Toe (Python + Tkinter)

A desktop Tic Tac Toe game written in Python using the built-in Tkinter GUI library.

## Features

- **Two modes:** vs Computer, or 2 Players on the same computer
- **Three difficulty levels:** Easy (random), Medium (makes mistakes), Hard (unbeatable, uses the minimax algorithm)
- **Scoreboard** for wins and draws
- **Winning line** drawn across the board
- Starting player **alternates** every round
- Play with the **mouse** or the **keyboard** (keys 1–9)

## What you need to download

Only **Python 3** (version 3.8 or newer). Tkinter comes with Python, so there is
**nothing to install with pip**.

| System | What to do |
|---|---|
| Windows | Install Python from https://www.python.org/downloads/ — Tkinter is included. If using the classic installer, tick **"Add python.exe to PATH"**. |
| macOS | Install Python from https://www.python.org/downloads/ — Tkinter is included. (If you use Homebrew Python instead, also run `brew install python-tk`.) |
| Linux (Ubuntu/Debian) | `sudo apt install python3 python3-tk` |
| Linux (Fedora) | `sudo dnf install python3 python3-tkinter` |

Check Tkinter works by running `python -m tkinter` (or `python3 -m tkinter`). A small test window should open.

## How to run

1. Put `tic_tac_toe.py` in a folder.
2. Open a terminal (Command Prompt / PowerShell on Windows) in that folder.
3. Run:

   ```bash
   # Windows
   python tic_tac_toe.py        # or: py tic_tac_toe.py

   # macOS / Linux
   python3 tic_tac_toe.py
   ```

**Or** open the file in **IDLE** (comes with Python) and press **F5**, or open it in VS Code / PyCharm and click **Run**.

## How to play

- Choose a **Mode** (vs Computer or 2 Players) and, against the computer, a **Level**.
- Click a square to place your mark. Against the computer you are **X**.
- Keyboard: keys **1–9** place a mark (1 = top-left, 9 = bottom-right), **N** starts a new round.
- Get three in a row (across, down, or diagonally) to win.
- When a round ends, click the board or press **New Round** to play again.
- Changing the mode or level resets the scores.

## Project structure

```
tic_tac_toe.py   # the whole game: game logic (top) + Tkinter window (TicTacToeApp class)
README.md        # this file
```

How the code is organised:

- `find_winner()` checks the 8 winning lines for three in a row, or a full board (draw).
- `minimax()` / `best_move()` let the computer look ahead at every possible move so it never loses on Hard.
- `TicTacToeApp` builds the window (labels, radio buttons, buttons, and a `Canvas` for the board) and handles clicks, turns and scores.

## Troubleshooting

- **`ModuleNotFoundError: No module named 'tkinter'`** — Tkinter isn't installed with your Python. On Linux run `sudo apt install python3-tk`; on macOS with Homebrew run `brew install python-tk`; on Windows reinstall Python from python.org.
- **`'python' is not recognized`** (Windows) — try `py tic_tac_toe.py`, or reinstall Python with "Add python.exe to PATH" ticked.

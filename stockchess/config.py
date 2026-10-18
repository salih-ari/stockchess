"""Configuration defaults for stockchess."""

import os
import shutil

# Default engine binary search paths
DEFAULT_ENGINE_PATHS = [
    "/usr/games/stockfish",
    "/usr/bin/stockfish",
    "/usr/local/bin/stockfish",
    os.path.expanduser("~/.local/bin/stockfish"),
    "stockfish",
]

def find_default_engine():
    """Find a usable stockfish binary on PATH."""
    for p in DEFAULT_ENGINE_PATHS:
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p
    found = shutil.which("stockfish")
    return found if found else None

DEFAULT_ENGINE = find_default_engine() or "stockfish"

# Default settings
DEFAULT_MOVETIME_MS = 1000
DEFAULT_ROUNDS = 1
DEFAULT_TIME_W = 300000   # ms
DEFAULT_TIME_B = 300000   # ms
DEFAULT_INC_W = 0
DEFAULT_INC_B = 0

# TUI colors (ANSI 256)
LIGHT_SQUARE = 250   # light gray
DARK_SQUARE = 240    # dark gray
HIGHLIGHT_SQUARE = 220  # yellow
LAST_MOVE_COLOR = 226  # bright yellow
WHITE_PIECE_COLOR = 255  # white
BLACK_PIECE_COLOR = 16   # black

# --- Theme persistence ---
import json as _json
CONFIG_DIR = os.path.expanduser("~/.config/stockchess")
CONFIG_FILE = os.path.join(CONFIG_DIR, "theme.json")

COLOR_MAP = {
    "black": 0, "red": 1, "green": 2, "yellow": 3, "blue": 4,
    "magenta": 5, "cyan": 6, "white": 7,
    "gray": 8, "grey": 8, "bright_black": 8,
    "bright_red": 9, "bright_green": 10, "bright_yellow": 11,
    "bright_blue": 12, "bright_magenta": 13, "bright_cyan": 14,
    "bright_white": 15,
    "dark": 0, "light": 7,
}


def color_to_index(color):
    if color is None:
        return None
    c = str(color).strip().lower()
    if c in COLOR_MAP:
        return COLOR_MAP[c]
    try:
        n = int(c)
        if 0 <= n <= 15:
            return n
    except ValueError:
        pass
    return None


def load_theme():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            d = _json.load(f)
        li = d.get("light_sq", 3)
        di = d.get("dark_sq", 8)
        if not isinstance(li, int) or not (0 <= li <= 15):
            li = 3
        if not isinstance(di, int) or not (0 <= di <= 15):
            di = 8
        return li, di
    except Exception:
        return 3, 8


def save_theme(light=None, dark=None):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    li, di = load_theme()
    if light is not None:
        li = light
    if dark is not None:
        di = dark
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        _json.dump({"light_sq": li, "dark_sq": di}, f)
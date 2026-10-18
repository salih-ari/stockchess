"""Clean full-screen terminal chess board (no text, animated).

Uses the original Unicode chess glyphs (outlined style) as pieces.
Colors are taken from the terminal's 16-color palette.
"""

import os
import sys
import time
import math

import chess

# Original Unicode chess glyphs (outlined/white style for both sides).
PIECES = {
    (chess.WHITE, chess.PAWN):   "♙",
    (chess.WHITE, chess.KNIGHT): "♘",
    (chess.WHITE, chess.BISHOP): "♗",
    (chess.WHITE, chess.ROOK):   "♖",
    (chess.WHITE, chess.QUEEN):  "♕",
    (chess.WHITE, chess.KING):   "♔",
    (chess.BLACK, chess.PAWN):   "♙",
    (chess.BLACK, chess.KNIGHT): "♘",
    (chess.BLACK, chess.BISHOP): "♗",
    (chess.BLACK, chess.ROOK):   "♖",
    (chess.BLACK, chess.QUEEN):  "♕",
    (chess.BLACK, chess.KING):   "♔",
}

try:
    from .config import load_theme as _load_theme
except ImportError:
    from config import load_theme as _load_theme
_LIGHT_DEFAULT, _DARK_DEFAULT = _load_theme()
LIGHT_SQ = _LIGHT_DEFAULT
DARK_SQ = _DARK_DEFAULT
WHITE_PIECE = 15
BLACK_PIECE = 0
HIGHLIGHT = 11
FLASH = 9

try:
    from blessed import Terminal
except Exception:
    Terminal = None


class CleanTUI:
    def __init__(self):
        self.term = Terminal() if Terminal is not None else None
        self.last_move = None
        self.frame = 0
        self.thinking = False
        self._entered = False
        try:
            from .config import load_theme
        except ImportError:
            from config import load_theme
        self.light_sq, self.dark_sq = load_theme()

    def enter(self):
        if self.term:
            print(self.term.enter_fullscreen(), end="", flush=True)
            print(self.term.hide_cursor, end="", flush=True)
            print(self.term.clear, end="", flush=True)
        else:
            os.system("clear")
        self._entered = True

    def leave(self):
        if self.term:
            print(self.term.show_cursor, end="", flush=True)
            print(self.term.exit_fullscreen(), end="", flush=True)
        self._entered = False

    def _hl_color(self):
        if self.thinking:
            t = time.time()
            pulse = (math.sin(t * 3.0) + 1) / 2
            return HIGHLIGHT if pulse > 0.5 else 3
        return HIGHLIGHT

    def render(self, game, *a, animate_move=None, **k):
        board = game.board
        term = self.term
        if term is None:
            return
        tw, th = term.width, term.height
        # Moderate cell size: big enough for a bold glyph, not stretched huge.
        cell_w = 4
        cell_h = 2
        pad_x = (tw - cell_w * 8) // 2
        pad_y = (th - cell_h * 8) // 2

        hl = self._hl_color()
        last_from = self.last_move.from_square if self.last_move else None
        last_to = self.last_move.to_square if self.last_move else None

        lines = []
        for _ in range(pad_y):
            lines.append(" " * tw)

        for rank in range(7, -1, -1):
            for sub in range(cell_h):
                row = " " * pad_x
                for file in range(8):
                    sq = chess.square(file, rank)
                    piece = board.piece_at(sq)
                    is_light = (file + rank) % 2 == 0
                    bg = self.light_sq if is_light else self.dark_sq
                    if sq in (last_from, last_to):
                        bg = hl
                    if animate_move is not None and sq == animate_move:
                        bg = FLASH
                    if sub == cell_h // 2 and piece is not None:
                        sym = PIECES.get((piece.color, piece.piece_type), "?")
                        fg = WHITE_PIECE if piece.color == chess.WHITE else BLACK_PIECE
                        # center glyph in cell
                        left = (cell_w - 1) // 2
                        right = cell_w - 1 - left
                        if self.term:
                            glyph = self.term.bold(self.term.color(fg)(self.term.on_color(bg)(sym)))
                        else:
                            glyph = sym
                        cell = self._bg(bg, " " * left) + glyph + self._bg(bg, " " * right)
                    else:
                        cell = self._bg(bg, " " * cell_w)
                    row += cell
                row += " " * (tw - pad_x - cell_w * 8)
                lines.append(row)

        for _ in range(th - pad_y - cell_h * 8):
            lines.append(" " * tw)

        out = term.home + term.clear + "\n".join(lines[:th])
        sys.stdout.write(out)
        sys.stdout.flush()

    def animate_move(self, game, move_uci, frames=6, delay=0.04):
        import chess
        mv = chess.Move.from_uci(move_uci)
        for _ in range(frames // 2):
            self.last_move = None
            self.render(game, animate_move=mv.from_square)
            time.sleep(delay)
        for _ in range(frames // 2):
            self.last_move = None
            self.render(game, animate_move=mv.to_square)
            time.sleep(delay)
        self.last_move = mv

    def get_key(self):
        if self.term:
            return self.term.inkey(timeout=0.05)
        return None

    def _bg(self, bg, text):
        if self.term:
            return self.term.on_color(bg)(text)
        return text

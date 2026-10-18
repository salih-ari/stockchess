"""Terminal UI for stockchess using blessed."""

import os
import sys
import chess

try:
    from blessed import Terminal
except Exception:  # pragma: no cover
    Terminal = None

# Unicode chess pieces
PIECES = {
    (chess.WHITE, chess.PAWN):   "♙",
    (chess.WHITE, chess.KNIGHT): "♘",
    (chess.WHITE, chess.BISHOP): "♗",
    (chess.WHITE, chess.ROOK):   "♖",
    (chess.WHITE, chess.QUEEN):  "♕",
    (chess.WHITE, chess.KING):   "♔",
    (chess.BLACK, chess.PAWN):   "♟",
    (chess.BLACK, chess.KNIGHT): "♞",
    (chess.BLACK, chess.BISHOP): "♝",
    (chess.BLACK, chess.ROOK):   "♜",
    (chess.BLACK, chess.QUEEN):  "♛",
    (chess.BLACK, chess.KING):   "♚",
}


class TUI:
    def __init__(self):
        self.term = Terminal() if Terminal is not None else None
        self.last_move = None  # chess.Move
        self.engine_info = {}

    def clear(self):
        if self.term:
            print(self.term.clear, end="", flush=True)
        else:
            os.system("clear")

    def move_cursor_home(self):
        if self.term:
            print(self.term.home, end="", flush=True)

    def render(self, game, white_name="White", black_name="Black", status=""):
        """Render the full board + info to terminal."""
        board = game.board
        term = self.term
        out = []
        if term:
            out.append(term.clear + term.home)
        else:
            out.append("\x1b[2J\x1b[H")

        # Header
        out.append(self._color(255, 1, "  ╔══════════════════════════════════════════════╗"))
        out.append(self._color(255, 1, "  ║  STOCKCHESS  –  Two Engine Battle            ║"))
        out.append(self._color(255, 1, "  ╚══════════════════════════════════════════════╝"))
        out.append("")

        # Engine names
        wlabel = f"  ♔ White: {white_name}"
        blabel = f"  ♚ Black: {black_name}"
        out.append(self._color(255, 0, wlabel) + "     " + self._color(16, 0, blabel))
        out.append("")

        # Engine thinking info
        info = self.engine_info or {}
        if info:
            depth = info.get("depth", "?")
            score_kind = info.get("score_kind", "cp")
            score = info.get("score", 0)
            if score_kind == "mate":
                eval_str = f"M{score}"
            else:
                eval_str = f"{score/100:+.2f}"
            nodes = info.get("nodes", 0)
            nps = info.get("nps", 0)
            pv = info.get("pv", "")
            pv_short = " ".join(pv.split()[:6])
            out.append(f"  Depth: {depth}  Eval: {eval_str}  Nodes: {nodes:,}  NPS: {nps:,}")
            if pv_short:
                out.append(f"  PV: {pv_short}")
        out.append("")

        # Board
        last = self.last_move
        last_from = last.from_square if last else None
        last_to = last.to_square if last else None

        # top border
        out.append("    " + self._bg(245, "  a b c d e f g h  "))
        for rank in range(7, -1, -1):
            row = f"  {rank+1} "
            for file in range(8):
                sq = chess.square(file, rank)
                piece = board.piece_at(sq)
                # square color
                is_light = (file + rank) % 2 == 0
                bg = 250 if is_light else 240
                if sq in (last_from, last_to):
                    bg = 220
                if piece is None:
                    ch = "·" if False else " "
                    cell = self._bg(bg, " " + " " + " ")
                else:
                    sym = PIECES.get((piece.color, piece.piece_type), "?")
                    fg = 255 if piece.color == chess.WHITE else 16
                    cell = self._fgbg(fg, bg, " " + sym + " ")
                row += cell
            row += " " + str(rank + 1)
            out.append(row)
        out.append("    " + self._bg(245, "  a b c d e f g h  "))
        out.append("")

        # Status line
        turn_str = "White to move" if board.turn == chess.WHITE else "Black to move"
        out.append(f"  {turn_str}   |   Moves: {len(game.moves)}   |   {status}")
        out.append("")

        # Move history (last 20 moves)
        out.append("  Move history:")
        hist = []
        for i, (uci, san) in enumerate(game.moves):
            move_no = i // 2 + 1
            if i % 2 == 0:
                hist.append(f"{move_no}. {san}")
            else:
                hist[-1] += f" {san}"
        # show last 6 full moves
        tail = hist[-6:]
        out.append("  " + "   ".join(tail))
        out.append("")

        # Controls
        out.append(self._color(245, 0, "  [Space] Pause  [Q] Quit  [Enter] Step  [S] Save PGN"))

        sys.stdout.write("\n".join(out) + "\n")
        sys.stdout.flush()

    def _color(self, fg, bold, text):
        if self.term:
            if bold:
                return self.term.bold(self.term.color(fg)(text))
            return self.term.color(fg)(text)
        return text

    def _bg(self, bg, text):
        if self.term:
            return self.term.on_color(bg)(text)
        return text

    def _fgbg(self, fg, bg, text):
        if self.term:
            return self.term.color(fg)(self.term.on_color(bg)(text))
        return text

    def prompt(self, msg):
        if self.term:
            with self.term.location(0, self.term.height - 1):
                print(self.term.clear_eol + msg, end="", flush=True)
        else:
            print(msg, end="", flush=True)
        try:
            return input()
        except EOFError:
            return ""

    def get_key(self):
        if self.term:
            return self.term.inkey(timeout=0.1)
        return None

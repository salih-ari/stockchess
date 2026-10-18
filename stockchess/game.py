"""Game orchestration: two engines playing chess against each other."""

import chess
import time


class Game:
    def __init__(self, engine_white, engine_black, movetime_ms=None,
                 wtime=None, btime=None, winc=0, binc=0,
                 rounds=1, human_white=False, human_black=False):
        self.engine_white = engine_white
        self.engine_black = engine_black
        self.movetime_ms = movetime_ms
        self.wtime = wtime
        self.btime = btime
        self.winc = winc
        self.binc = binc
        self.rounds = rounds
        self.human_white = human_white
        self.human_black = human_black

        self.board = chess.Board()
        self.moves = []          # list of (move_uci, san)
        self.move_times = []     # ms per move
        self.result = None       # "1-0", "0-1", "1/2-1/2", "*"
        self.termination = None
        self.current_engine_info = {}

    def reset(self):
        self.board = chess.Board()
        self.moves = []
        self.move_times = []
        self.result = None
        self.termination = None
        self.current_engine_info = {}

    def is_game_over(self):
        return self.board.is_game_over(claim_draw=True)

    def outcome(self):
        return self.board.outcome(claim_draw=True)

    def side_to_move(self):
        return "white" if self.board.turn == chess.WHITE else "black"

    def current_engine(self):
        if self.board.turn == chess.WHITE:
            return self.engine_white
        return self.engine_black

    def is_human_turn(self):
        if self.board.turn == chess.WHITE:
            return self.human_white
        return self.human_black

    def legal_moves(self):
        return list(self.board.legal_moves)

    def make_engine_move(self, on_info=None):
        """Ask current engine for a move, apply it. Returns (move_uci, san, ms)."""
        engine = self.current_engine()
        fen = self.board.fen()
        engine.set_position(fen)
        t0 = time.time()
        if self.movetime_ms is not None:
            engine.go(movetime=self.movetime_ms)
        else:
            wtime = self.wtime if self.wtime is not None else 60000
            btime = self.btime if self.btime is not None else 60000
            # convert to ms for UCI
            engine.go(wtime=wtime, btime=btime, winc=self.winc, binc=self.binc)
        move_uci, ponder = engine.get_best_move(timeout=120)
        elapsed = int((time.time() - t0) * 1000)
        if on_info is not None:
            on_info(engine.last_info)
        self.current_engine_info = dict(engine.last_info)

        if move_uci is None:
            # no legal move (shouldn't happen mid-game)
            raise RuntimeError("Engine returned no move")

        move = chess.Move.from_uci(move_uci)
        if move not in self.board.legal_moves:
            # illegal -> resign
            raise RuntimeError(f"Illegal move from engine: {move_uci}")
        san = self.board.san(move)
        self.board.push(move)
        self.moves.append((move_uci, san))
        self.move_times.append(elapsed)

        # update clocks if using time control
        if self.wtime is not None and self.movetime_ms is None:
            if self.board.turn == chess.BLACK:  # white just moved
                self.wtime = max(0, self.wtime - elapsed + self.winc)
            else:
                self.btime = max(0, self.btime - elapsed + self.binc)

        return move_uci, san, elapsed

    def make_human_move(self, uci_move):
        move = chess.Move.from_uci(uci_move)
        if move not in self.board.legal_moves:
            return False
        san = self.board.san(move)
        self.board.push(move)
        self.moves.append((uci_move, san))
        self.move_times.append(0)
        return True

    def finalize(self):
        out = self.board.outcome(claim_draw=True)
        if out is None:
            self.result = "*"
            self.termination = "unfinished"
            return
        if out.winner is True:
            self.result = "1-0"
        elif out.winner is False:
            self.result = "0-1"
        else:
            self.result = "1/2-1/2"
        self.termination = str(out.termination).split(".")[-1]

    def pgn_text(self, white_name="White", black_name="Black", event="StockChess"):
        game = chess.pgn.Game()
        game.headers["Event"] = event
        game.headers["White"] = white_name
        game.headers["Black"] = black_name
        game.headers["Result"] = self.result or "*"
        node = game
        b = chess.Board()
        for uci, san in self.moves:
            move = chess.Move.from_uci(uci)
            node = node.add_variation(move)
            b.push(move)
        import io
        buf = io.StringIO()
        chess.pgn.GameExporter(game).export(buf) if False else None
        # simpler: use pgn printer
        return str(game)

"""Command-line argument parsing for stockchess."""

import argparse


def build_parser():
    p = argparse.ArgumentParser(
        prog="stockchess",
        description="Terminal chess: two engines play against each other.",
    )
    p.add_argument("--version", action="version", version="stockchess 0.1.0")
    p.add_argument("--engine1", "-e1", default=None,
                   help="Path/binary for White's engine (default: stockfish)")
    p.add_argument("--engine2", "-e2", default=None,
                   help="Path/binary for Black's engine (default: same as engine1)")
    p.add_argument("--name1", default="Stockfish (White)",
                   help="Display name for White engine")
    p.add_argument("--name2", default="Stockfish (Black)",
                   help="Display name for Black engine")
    p.add_argument("--time", "-t", type=int, default=None,
                   help="Movetime in ms per move (default: 1000)")
    p.add_argument("--wtime", type=int, default=None, help="White total time (ms)")
    p.add_argument("--btime", type=int, default=None, help="Black total time (ms)")
    p.add_argument("--winc", type=int, default=0, help="White increment (ms)")
    p.add_argument("--binc", type=int, default=0, help="Black increment (ms)")
    p.add_argument("--rounds", "-r", type=int, default=1,
                   help="Number of games to play")
    p.add_argument("--pgn", default=None, help="Export game(s) to PGN file")
    p.add_argument("--depth", type=int, default=None, help="Fixed search depth")
    p.add_argument("--nodes", type=int, default=None, help="Fixed node count")
    p.add_argument("--skill1", type=int, default=None, help="Skill level for engine1 (0-20)")
    p.add_argument("--skill2", type=int, default=None, help="Skill level for engine2 (0-20)")
    p.add_argument("--threads", type=int, default=1, help="Threads per engine")
    p.add_argument("--hash", type=int, default=64, help="Hash size MB")
    p.add_argument("--no-ui", action="store_true", help="Disable TUI, print moves only")
    p.add_argument("--clean", action="store_true", help="Clean full-screen board only, no text")
    p.add_argument("--quiet", action="store_true", help="Minimal output")
    return p


def parse_args(argv=None):
    return build_parser().parse_args(argv)

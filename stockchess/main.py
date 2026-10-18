"""Entry point for stockchess."""

import os
import sys
import time

# Allow running as script or as module
try:
    from .config import find_default_engine, DEFAULT_MOVETIME_MS
    from .engine import Engine, EngineError
    from .game import Game
    from .tui import TUI
    from .clean_tui import CleanTUI
    from .cli import parse_args
    from .pgn import game_to_pgn, save_pgn
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from config import find_default_engine, DEFAULT_MOVETIME_MS
    from engine import Engine, EngineError
    from game import Game
    from tui import TUI
    from clean_tui import CleanTUI
    from cli import parse_args
    from pgn import game_to_pgn, save_pgn


def make_engine(path, name, options):
    if path is None:
        path = find_default_engine()
    if path is None:
        raise SystemExit("No chess engine found. Install stockfish or pass --engine1/--engine2.")
    opts = dict(options)
    return Engine(path, name=name, options=opts)


def build_options(args, skill):
    opts = {}
    opts["Threads"] = args.threads
    opts["Hash"] = args.hash
    if skill is not None:
        opts["Skill Level"] = skill
    return opts


def run_game(args, game_no=1):
    opts1 = build_options(args, args.skill1)
    opts2 = build_options(args, args.skill2)

    e1 = make_engine(args.engine1, args.name1, opts1)
    e2 = make_engine(args.engine2, args.name2, opts2)

    movetime = args.time if args.time is not None else DEFAULT_MOVETIME_MS
    if args.depth is not None or args.nodes is not None:
        movetime = None  # use depth/nodes instead handled below (simplified: movetime None -> time control)
    # If user explicitly wants depth/nodes, we still need movetime; handle in loop via game override not supported -> fallback movetime
    if movetime is None and args.depth is None and args.nodes is None:
        movetime = DEFAULT_MOVETIME_MS

    game = Game(
        engine_white=e1,
        engine_black=e2,
        movetime_ms=movetime if (args.depth is None and args.nodes is None) else None,
        wtime=args.wtime,
        btime=args.btime,
        winc=args.winc,
        binc=args.binc,
        human_white=False,
        human_black=False,
    )

    if args.no_ui:
        tui = None
    elif getattr(args, "clean", False):
        tui = CleanTUI()
        tui.enter()
    else:
        tui = TUI()
        tui.clear()
    white_name = args.name1
    black_name = args.name2

    paused = False
    try:
        while not game.is_game_over():
            # handle pause key
            if tui and not args.no_ui:
                key = tui.get_key()
                if key and str(key).lower() == "q":
                    raise KeyboardInterrupt
                if key and str(key) == " ":
                    paused = not paused
            if paused:
                time.sleep(0.1)
                continue

            if game.is_human_turn():
                # not implemented in auto mode
                break

            engine = game.current_engine()
            if tui:
                if isinstance(tui, CleanTUI):
                    tui.thinking = True
                tui.engine_info = {}
                if not isinstance(tui, CleanTUI):
                    tui.last_move = None
                tui.render(game, white_name, black_name,
                           status=f"Game {game_no} | {engine.name} thinking...")

            # If depth/nodes specified, temporarily override by calling engine directly
            if args.depth is not None or args.nodes is not None:
                fen = game.board.fen()
                engine.set_position(fen)
                t0 = time.time()
                kwargs = {}
                if args.depth is not None:
                    kwargs["depth"] = args.depth
                if args.nodes is not None:
                    kwargs["nodes"] = args.nodes
                engine.go(**kwargs)
                move_uci, ponder = engine.get_best_move(timeout=120)
                elapsed = int((time.time() - t0) * 1000)
                game.current_engine_info = dict(engine.last_info)
                if tui:
                    tui.engine_info = game.current_engine_info
                if move_uci is None:
                    break
                import chess
                move = chess.Move.from_uci(move_uci)
                if move not in game.board.legal_moves:
                    raise RuntimeError(f"Illegal move: {move_uci}")
                san = game.board.san(move)
                game.board.push(move)
                game.moves.append((move_uci, san))
                game.move_times.append(elapsed)
                # update clocks
                if game.wtime is not None:
                    if game.board.turn == chess.BLACK:
                        game.wtime = max(0, game.wtime - elapsed + game.winc)
                    else:
                        game.btime = max(0, game.btime - elapsed + game.binc)
            else:
                move_uci, san, elapsed = game.make_engine_move(
                    on_info=(lambda info: setattr(tui, "engine_info", info)) if tui else None
                )
                if tui:
                    tui.engine_info = game.current_engine_info

            # update last_move for highlight
            if tui:
                import chess
                if game.moves:
                    last_uci = game.moves[-1][0]
                    if isinstance(tui, CleanTUI):
                        tui.thinking = False
                        tui.animate_move(game, last_uci)
                    else:
                        tui.last_move = chess.Move.from_uci(last_uci)
                        tui.render(game, white_name, black_name,
                                   status=f"Game {game_no} | last: {game.moves[-1][1]}")

            # small delay for readability
            time.sleep(0.3)

        game.finalize()

        if tui and not args.no_ui:
            if isinstance(tui, CleanTUI):
                tui.thinking = False
                tui.last_move = None
                tui.render(game, white_name, black_name)
                # wait for any key or 3s
                t0 = time.time()
                while time.time() - t0 < 3:
                    k = tui.get_key()
                    if k:
                        break
            else:
                tui.render(game, white_name, black_name,
                           status=f"Game {game_no} FINISHED: {game.result} ({game.termination})")
                tui.prompt(f"Game over: {game.result}. Press Enter to continue...")
    finally:
        if isinstance(tui, CleanTUI):
            tui.leave()
        e1.quit()
        e2.quit()

    if args.no_ui or args.quiet:
        print(f"Game {game_no}: {game.result} ({game.termination})  moves={len(game.moves)}")

    return game


def main(argv=None):
    args = parse_args(argv)

    if args.engine1 is None:
        args.engine1 = find_default_engine()
    if args.engine2 is None:
        args.engine2 = args.engine1

    if args.engine1 is None:
        print("ERROR: stockfish not found. Install with: sudo pacman -S stockfish")
        print("or download from https://stockfishchess.org/download/")
        sys.exit(1)

    all_games = []
    for i in range(1, args.rounds + 1):
        g = run_game(args, game_no=i)
        all_games.append(g)

    if args.pgn:
        # concatenate PGNs
        texts = [game_to_pgn(g, white_name=args.name1, black_name=args.name2) for g in all_games]
        save_pgn(args.pgn, "\n\n".join(texts))
        print(f"Saved PGN to {args.pgn}")

    return 0


def main_clean(argv=None):
    """Entry point for the clean full-screen mode."""
    if argv is None:
        argv = sys.argv[1:]
    sys.argv = [sys.argv[0]] + ["--clean"] + list(argv)
    return main()


if __name__ == "__main__":
    sys.exit(main())

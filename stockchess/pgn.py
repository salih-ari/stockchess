"""PGN export helpers."""

import chess
import chess.pgn
import io


def game_to_pgn(game, white_name="White", black_name="Black", event="StockChess",
                site="Terminal", date=None):
    import datetime
    if date is None:
        date = datetime.date.today().strftime("%Y.%m.%d")

    g = chess.pgn.Game()
    g.headers["Event"] = event
    g.headers["Site"] = site
    g.headers["Date"] = date
    g.headers["White"] = white_name
    g.headers["Black"] = black_name
    g.headers["Result"] = game.result or "*"

    node = g
    b = chess.Board()
    for uci, san in game.moves:
        move = chess.Move.from_uci(uci)
        node = node.add_variation(move)
        b.push(move)

    # Add move times as comments if available
    buf = io.StringIO()
    chess.pgn.FileExporter(buf).export(g) if False else None
    exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
    text = g.accept(exporter)
    return text


def save_pgn(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
        if not text.endswith("\n"):
            f.write("\n")
    return path

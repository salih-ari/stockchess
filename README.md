# ♟️ stockchess

**A self-playing chess display for your terminal.**

Stockchess runs two UCI-compatible chess engines against each other and renders their game in your terminal. Watch Stockfish battle itself, follow engine evaluations, or leave a clean animated chessboard running as part of your Linux rice setup.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Linux-1793D1?logo=linux&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

## Features

- **Engine vs. Engine** — Run Stockfish against itself or use different UCI engines.
- **Unicode Chessboard** — Render chess pieces with ANSI terminal colors.
- **Clean Mode** — Full-screen chessboard with animated moves and no extra text.
- **Engine Analysis** — Display search depth, evaluation, nodes, and principal variation.
- **Time Controls** — Configure move time, game clocks, increments, depth, or node limits.
- **Skill Levels** — Set different playing strengths for each engine.
- **Performance Controls** — Configure engine threads and hash memory.
- **PGN Export** — Save completed games for later analysis.
- **Multiple Games** — Run round-robin matches or play a specified number of rounds.
- **Persistent Themes** — Customize board colors with `stockchess-theme`.

## Requirements

- Linux
- Python 3.10+
- A UCI-compatible chess engine, such as Stockfish
- `python-chess`
- `blessed`

## Installation

### 1. Install Stockfish

On Arch Linux or CachyOS:

```bash
sudo pacman -S --needed git python python-pip stockfish
```

On Debian or Ubuntu:

```bash
sudo apt update
sudo apt install git python3 python3-venv python3-pip stockfish
```

You can also download Stockfish from the [official website](https://stockfishchess.org/download/).

Verify that Stockfish is available:

```bash
stockfish
```

Enter `quit` to exit the engine.

### 2. Clone the repository

```bash
git clone https://github.com/salih-ari/stockchess.git
cd stockchess
```

### 3. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies and the application

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

### 5. Start playing

```bash
stockchess
```

Keep the virtual environment activated when using the installed commands. Alternatively, use the provided `install.sh` if you prefer its installation method.

## Usage

### Start a game

Run two Stockfish engines against each other with the default settings:

```bash
stockchess
```

### Adjust the game

```bash
# Faster games: 200 milliseconds per move
stockchess --time 200

# Different engine skill levels
stockchess --skill1 0 --skill2 20

# Play five games and save them to a PGN file
stockchess --rounds 5 --pgn games.pgn

# Five-minute game with a two-second increment
stockchess --wtime 300000 --btime 300000 --winc 2000 --binc 2000

# Fixed search depth
stockchess --depth 15

# Fixed node count
stockchess --nodes 100000

# Run ten games without the interactive interface
stockchess --no-ui --time 100 --rounds 10
```

### Use different engines

```bash
stockchess --engine1 /path/to/engine1 --engine2 /path/to/engine2
```

Both executables must support the UCI protocol.

### Clean full-screen mode

For a minimal, always-running terminal display:

```bash
stockchess-clean
```

### Customize the theme

```bash
stockchess-theme cyan
stockchess-theme "light green"
stockchess-theme "dark gray"
```

Theme settings are saved between runs.

## Interactive Controls

| Key | Action |
|---|---|
| `Space` | Pause or resume the game |
| `Q` | Quit |
| `Enter` | Advance one move |
| `S` | Save the current game as PGN |

## Command-Line Options

| Option | Description |
|---|---|
| `--engine1`, `-e1` | White engine executable |
| `--engine2`, `-e2` | Black engine executable |
| `--name1` | Display name for White |
| `--name2` | Display name for Black |
| `--time`, `-t` | Thinking time per move in milliseconds |
| `--wtime` / `--btime` | White and Black clock times in milliseconds |
| `--winc` / `--binc` | Clock increments in milliseconds |
| `--rounds`, `-r` | Number of games to play |
| `--pgn` | Output PGN file |
| `--depth` | Search depth limit |
| `--nodes` | Search node limit |
| `--skill1` / `--skill2` | Engine skill levels, from 0 to 20 |
| `--threads` | Threads per engine |
| `--hash` | Hash table size in MB |
| `--no-ui` | Disable the interactive interface |
| `--clean` | Use the minimal full-screen interface |
| `--quiet` | Reduce terminal output |

Run `stockchess --help` to see the available options.

## Project Structure

```text
stockchess/
├── stockchess/
│   ├── main.py          # Application entry point and game loop
│   ├── engine.py        # UCI engine integration
│   ├── game.py          # Chess game logic
│   ├── tui.py           # Interactive terminal interface
│   ├── clean_tui.py     # Minimal full-screen interface
│   ├── cli.py           # Command-line arguments
│   ├── pgn.py           # PGN export
│   ├── config.py        # Defaults and persistent settings
│   └── theme.py         # Theme command
├── bin/                 # Launcher scripts
├── install.sh
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Contributing

Contributions, bug reports, and feature suggestions are welcome.

Feel free to open an issue or submit a pull request.

## License

Released under the [MIT License](LICENSE).

---

**Made for terminal lovers, chess enthusiasts, and Linux rice setups.** ♟️

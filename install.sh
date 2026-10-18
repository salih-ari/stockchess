#!/usr/bin/env bash
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
pip install --break-system-packages -r "$HERE/requirements.txt" 2>/dev/null || pip install -r "$HERE/requirements.txt"
mkdir -p "$HOME/.local/bin"
for cmd in stockchess stockchess-clean stockchess-theme; do
  cat > "$HOME/.local/bin/$cmd" <<EOF
#!/usr/bin/env python3
import os, sys
sys.path.insert(0, "$HERE")
from stockchess.main import main, main_clean
from stockchess.theme import main as theme_main
EOF
done
# Write correct per-command launchers
cat > "$HOME/.local/bin/stockchess" <<EOF
#!/usr/bin/env python3
import sys
sys.path.insert(0, "$HERE")
from stockchess.main import main
sys.exit(main())
EOF
cat > "$HOME/.local/bin/stockchess-clean" <<EOF
#!/usr/bin/env python3
import sys
sys.path.insert(0, "$HERE")
from stockchess.main import main_clean
sys.exit(main_clean())
EOF
cat > "$HOME/.local/bin/stockchess-theme" <<EOF
#!/usr/bin/env python3
import sys
sys.path.insert(0, "$HERE")
from stockchess.theme import main
sys.exit(main())
EOF
chmod +x "$HOME/.local/bin/stockchess" "$HOME/.local/bin/stockchess-clean" "$HOME/.local/bin/stockchess-theme"
echo "Installed stockchess, stockchess-clean, stockchess-theme"
echo "Make sure $HOME/.local/bin is on your PATH."
echo "Optional: pip install -e $HERE for a proper install."

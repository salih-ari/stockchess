"""CLI helper to set stockchess board theme colors."""

import os
import sys

try:
    from .config import color_to_index, save_theme, load_theme, COLOR_MAP
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from config import color_to_index, save_theme, load_theme, COLOR_MAP


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help"):
        print("Usage: stockchess-theme <color>            # set light-square color")
        print("       stockchess-theme light <color>     # set light-square color")
        print("       stockchess-theme dark <color>      # set dark-square color")
        print("Colors: " + ", ".join(sorted(COLOR_MAP.keys())) + " or 0-15")
        li, di = load_theme()
        print(f"Current: light={li}, dark={di}")
        return 0

    if args[0].lower() in ("light", "dark"):
        which = args[0].lower()
        if len(args) < 2:
            print("Missing color", file=sys.stderr)
            return 1
        idx = color_to_index(args[1])
        if idx is None:
            print(f"Unknown color: {args[1]}", file=sys.stderr)
            return 1
        if which == "light":
            save_theme(light=idx)
        else:
            save_theme(dark=idx)
        li, di = load_theme()
        print(f"Set {which} square color -> {idx}. Now light={li}, dark={di}")
        return 0

    # single color -> light square
    idx = color_to_index(args[0])
    if idx is None:
        print(f"Unknown color: {args[0]}", file=sys.stderr)
        return 1
    save_theme(light=idx)
    li, di = load_theme()
    print(f"Set light square color -> {idx}. Now light={li}, dark={di}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

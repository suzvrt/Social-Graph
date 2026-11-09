"""Backwards-compatible launcher. Prefer `python -m socialgraph`."""

from socialgraph.ui.app import main

if __name__ == "__main__":
    main()

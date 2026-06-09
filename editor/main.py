import sys

from PySide6TK import QtWrappers

from editor.core.client import CatenaEditor


def main() -> int:
    QtWrappers.exec_app(CatenaEditor, "CatenaEditor")
    return 0


if __name__ == "__main__":
    sys.exit(main())

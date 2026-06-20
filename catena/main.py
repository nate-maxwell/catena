import sys

from PySide6TK import QtCore
from PySide6TK import QtGui
from PySide6TK import QtWidgets

from catena import resources
from catena.client import CatenaEditor
from catena.splash import CatenaSplashScreen


def main() -> int:
    app = QtWidgets.QApplication(sys.argv)

    splash_pixmap = QtGui.QPixmap(resources.SPLASH_IMAGE)
    splash = CatenaSplashScreen(splash_pixmap)
    splash.show()
    app.processEvents()

    splash.set_texts("Catena Editor\nInitializing Graph Engine...", "Nate Maxwell")
    app.processEvents()

    window = CatenaEditor()
    window.show()

    def _close_splash() -> None:
        splash.finish(window)

    QtCore.QTimer.singleShot(1000, _close_splash)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

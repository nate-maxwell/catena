import logging
import ctypes
import platform
import sys

from PySide6TK import QtCore
from PySide6TK import QtGui
from PySide6TK import QtWidgets

from catena import output_log
from catena import resources
from catena.client import CatenaEditor
from catena.splash import CatenaSplashScreen

logger = logging.getLogger(__name__)


def _configure_application_identity() -> None:
    """Set process-level Windows identity before any top-level window is shown."""
    if platform.system() == "Windows":
        app_id = "NateMaxwell.Catena"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)


def main() -> int:
    _configure_application_identity()
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Catena")
    app_icon = QtGui.QIcon(resources.get_window_icon_path().as_posix())
    app.setWindowIcon(app_icon)

    output_log.init_log_window()
    logger.info("Application initialized")
    logger.info("-" * 30)

    splash_pixmap = QtGui.QPixmap(resources.SPLASH_IMAGE)
    splash = CatenaSplashScreen(splash_pixmap, app_icon)
    splash.show()
    app.processEvents()

    splash.set_texts("Catena Editor\nInitializing Graph Engine...", "Nate Maxwell")
    app.processEvents()

    window = CatenaEditor()
    window.setWindowIcon(app_icon)
    window.show()

    def _close_splash() -> None:
        splash.finish(window)
        logger.info("Splash screen closed")

    QtCore.QTimer.singleShot(1000, _close_splash)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

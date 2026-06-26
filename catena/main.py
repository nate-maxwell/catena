import logging
import os
import sys
from pathlib import Path

from PySide6TK import QtCore
from PySide6TK import QtGui
from PySide6TK import QtWidgets

from catena import appdata
from catena import output_log
from catena import resources
from catena.client import CatenaEditor
from catena.splash import CatenaSplashScreen

logger = logging.getLogger(__name__)


def _init_test_plugins() -> None:
    user_plugin_path = Path("C:/Users/Naet/Desktop/test/user_plugin")
    os.environ[appdata.PLUGINS_ENV_VAR] = user_plugin_path.as_posix()


def main() -> int:
    _init_test_plugins()

    app = QtWidgets.QApplication(sys.argv)
    output_log.init_log_window()
    logger.info("Application initialized")
    logger.info("-" * 30)

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
        logger.info("Splash screen closed")

    QtCore.QTimer.singleShot(1000, _close_splash)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

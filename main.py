import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),"Core"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),"ExternalPackage"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),"UI"))

from Core import *
from UI import *
from ExternalPackage import dpi_manager
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication

if __name__ == '__main__':

    # enable high dpi scale
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(max(1, dpi_manager.scale-0.25))
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    mainWin = MainWindow(app)
    mainWin.show()

    ret = app.exec_()
    Manager.OnAppEnd()
    sys.exit(ret)

# coding:utf-8
from .config import qconfig

from PySide2.QtCore import QFile
from PySide2.QtWidgets import QWidget


def getStyleSheet(file: str):
    """ getTranslation style sheet

    Parameters
    ----------
    file: str
        qss file name, without `.qss` suffix
    """
    f = QFile(f":/qfluentwidgets/qss/{qconfig.theme}/{file}.qss")
    f.open(QFile.ReadOnly)
    qss = str(f.readAll(), encoding='utf-8')
    f.close()
    return qss


def setStyleSheet(widget: QWidget, file: str):
    """ set the style sheet of widget

    Parameters
    ----------
    widget: QWidget
        the widget to set style sheet

    file: str
        qss file name, without `.qss` suffix
    """
    widget.setStyleSheet(getStyleSheet(file))
from Core.DataType import AutoTranslateWord
from .AppPage import AppPage
from typing import Union
from PySide2.QtWidgets import QFrame, QLayout

class PlayerPage(AppPage):
    def __init__(self, appWindow, parent: Union[QFrame, QLayout] = None):
        super().__init__(appWindow=appWindow, parent=parent, titleText=AutoTranslateWord("Play"))

    def onSwitchIn(self):
        pass
    def onSwitchOut(self):
        pass
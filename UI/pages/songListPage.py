from Core.DataType import AutoTranslateWord
from .AppPage import AppPage
from typing import Union
from PySide2.QtWidgets import QFrame, QLayout

class SongListPage(AppPage):
    def __init__(self, appWindow, parent: Union[QFrame, QLayout] = None):
        super().__init__(appWindow=appWindow, parent=parent, titleText=AutoTranslateWord("Song List"))

    def onSwitchIn(self):
        pass
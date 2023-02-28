from Core.DataType import AutoTranslateWord, AutoTranslateWordList
from .AppPage import AppPage
from typing import Union
from PySide2.QtWidgets import QFrame, QLayout
from components import AppSearchBar_WithDropDown, AppScrollBox

class SongListPage(AppPage):
    def __init__(self, appWindow, parent: Union[QFrame, QLayout] = None):
        super().__init__(appWindow=appWindow, parent=parent, titleText=AutoTranslateWord("Song List"))



    def onSwitchIn(self):
        pass
    def onSwitchOut(self):
        pass
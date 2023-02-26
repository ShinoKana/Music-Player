from Core.DataType import AutoTranslateWord, AutoTranslateWordList
from .AppPage import AppPage
from typing import Union
from PySide2.QtWidgets import QFrame, QLayout
from components import AppSearchBar_WithDropDown, AppScrollBox

class SongListPage(AppPage):
    def __init__(self, appWindow, parent: Union[QFrame, QLayout] = None):
        super().__init__(appWindow=appWindow, parent=parent, titleText=AutoTranslateWord("Song Library"))

        #region search bar
        self.searchBar = AppSearchBar_WithDropDown(titleText=AutoTranslateWord("Search Song"),
                                                    dropdownChoices=AutoTranslateWordList("Song Name", "Artist"),
                                                    hintText=AutoTranslateWord("enter song Name"))
        self.searchBar.dropDown.onChoiceChanged.connect(
            lambda key: self.searchBar.SetHintText({"Song Name": AutoTranslateWord('enter song Name'),
                                                    "Artist": AutoTranslateWord('enter artist name')}[key]))
        self.addComponent(self.searchBar)
        #endregion

        #region song list
        self.songListBox = AppScrollBox(height=300, titleText=AutoTranslateWord("Song List"))
        self.addComponent(self.songListBox)
        #endregion


    def onSwitchIn(self):
        pass
    def onSwitchOut(self):
        pass
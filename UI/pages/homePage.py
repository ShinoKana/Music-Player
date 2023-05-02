from Core.DataType import AutoTranslateWord, AutoTranslateWordList
from .AppPage import AppPage
from typing import Union, List, Optional, Literal
from Core import appManager, networkManager
from PySide2.QtWidgets import QFrame, QLayout, QWidget, QHBoxLayout, QVBoxLayout
from PySide2.QtCore import Qt
from PySide2.QtGui import QColor, QWheelEvent
from components import AppSearchBar_WithDropDown, AppScrollBox, AppTextLabel, AppLayoutBox
from ExternalPackage.pyqt5Custom import Spinner
import json
from functools import reduce

class HomePage(AppPage):
    def __init__(self, appWindow, parent: Union[QFrame, QLayout] = None):
        super().__init__(appWindow=appWindow, parent=parent, titleText=AutoTranslateWord("home"))

        self.pageLayoutWidget = QWidget()
        self.pageLayout = QHBoxLayout(self.pageLayoutWidget)
        self.pageLayoutWidget.setMinimumHeight(appWindow.APP_PAGE_DEFAULT_SIZE[1] - 320)
        self.addComponent(self.pageLayoutWidget)

        #region left panel
        self.leftPanel = QWidget()
        self.leftPanel.setMaximumWidth(appWindow.DEFALUT_WINDOW_SIZE[0]//2)
        self.leftPanelLayout = QVBoxLayout(self.leftPanel)
        self.leftPanelLayout.setAlignment(Qt.AlignTop|Qt.AlignCenter)
        self.pageLayout.addWidget(self.leftPanel)
        self.leftPanelLayout.addWidget(AppTextLabel(text=AutoTranslateWord("Search Resources"), fontSize=20))
        self.searchBar = AppSearchBar_WithDropDown(titleText=AutoTranslateWord("Search Song"),
                                                   dropdownChoices=AutoTranslateWordList("Song Name", "Artist",
                                                                                         "Album"),
                                                   hintText=AutoTranslateWord("enter song Name"),
                                                   searchCommand=self._searchSongResourse)
        self.searchBar.dropDown.onChoiceChanged.connect(
            lambda key: self.searchBar.SetHintText({"Song Name": AutoTranslateWord('enter song Name'),
                                                    "Artist": AutoTranslateWord('enter artist name'),
                                                    'Album': AutoTranslateWord('enter album name')}[key]))
        self.leftPanelLayout.addWidget(self.searchBar)
        self.songResourcesBox = AppScrollBox(height=100, titleText=AutoTranslateWord("All song"))
        self.leftPanelLayout.addWidget(self.songResourcesBox)
        self.searchSpinner = Spinner(width=5, color=QColor('white') if appManager.config.isDarkTheme() else QColor('black'))
        self.searchSpinner.setParent(self)
        self.searchSpinner.play=False
        self.searchSpinner.hide()
        #endregion

        #region right panel
        self.rightPanel = QWidget()
        self.rightPanelLayout = QVBoxLayout(self.rightPanel)
        self.rightPanel.setMaximumWidth(appWindow.DEFALUT_WINDOW_SIZE[0]//2)
        self.rightPanelLayout.setSpacing(15)
        self.rightPanelLayout.setAlignment(Qt.AlignTop|Qt.AlignCenter)
        self.rightPanelLayout.addWidget(self.rightPanel)
        self.pageLayout.addWidget(self.rightPanel)
        self.currentPlayListBox = AppScrollBox(height=200, titleText=AutoTranslateWord("Current Play List"))
        self.rightPanelLayout.addWidget(self.currentPlayListBox)
        self.recentHitSongListBox = AppScrollBox(height=200, titleText=AutoTranslateWord("Recent Hit Song"))
        self.rightPanelLayout.addWidget(self.recentHitSongListBox)
        #endregion

    #region methods for search song
    def _searchSongResourse(self, keywords:str, mode):
        if keywords is None or keywords == "" or keywords.replace(" ", "") == "":
            return
        self._lockSearch()
        _mode = mode.lower()
        if _mode.startswith("song"):
            _mode = "name"
        elif _mode.startswith("artist"):
            _mode = "artist"
        elif _mode.startswith("album"):
            _mode = "album"
        keywordList = keywords.split(" ")
        def onSearchFinishCallback(data):
            self._unlockSearch()
            if data is None or len(data) == 0:
                print('no song with keyword: ', keywords, ' and mode: ', mode, ' found')
                appManager.toast(keywords+":"+ AutoTranslateWord('no finding result'))
                return
            self.songResourcesBox.removeAllComponents()
            for song in data:
                targetList = data['names'] if _mode == 'name' else data['artists'] if _mode == 'artist' else data['albums']
                targetList = json.loads(targetList)
                targetIndex = None
                for i, s in enumerate(targetList):
                    if reduce(lambda a, b: a and b, map(lambda x: x in s, keywordList)):
                        targetIndex = i
                        break
                if targetIndex is None:
                    i=0
                songName = json.loads(data['names'])[targetIndex]
                songArtist = json.loads(data['artists'])[targetIndex]
                songAlbum = json.loads(data['albums'])[targetIndex]
                fileExt = data['fileExt']
                fileSize = data['fileSize']
                box = AppLayoutBox(contain=[songName, songArtist, songAlbum, fileExt, fileSize])
                def downloadSong():
                    pass
                    #TODO: download song
                box.addButton(text=AutoTranslateWord('download'), img=appManager.getUIImagePath('down_arrow.png'),command=downloadSong)
                self.songResourcesBox.addComponent(box)
        networkManager.create_async_thread(target=networkManager.findSong, args=(keywords, _mode),
                                           returnCallbacks=onSearchFinishCallback)
    def _lockSearch(self):
        self.searchSpinner.show()
        self.searchSpinner.play=True
        self.searchBar.searchButton.setEnabled(False)
        self.searchBar.inputArea.setEnabled(False)
        self.searchBar.dropDown.setEnabled(False)
        for component in self.songResourcesBox.components:
            component.setEnabled(False)
            if hasattr('components', component):
                for subComponent in component.components:
                    subComponent.setEnabled(False)
    def _unlockSearch(self):
        self.searchSpinner.hide()
        self.searchSpinner.play=False
        self.searchBar.searchButton.setEnabled(True)
        self.searchBar.inputArea.setEnabled(True)
        self.searchBar.dropDown.setEnabled(True)
        for component in self.songResourcesBox.components:
            component.setEnabled(True)
            if hasattr('components', component):
                for subComponent in component.components:
                    subComponent.setEnabled(True)
    #endregion

    def paintEvent(self, e):
        super().paintEvent(e)
        if self.searchSpinner.isVisible():
            self.searchSpinner.setGeometry(self.songResourcesBox.pos().x() + self.songResourcesBox.width()//2 ,
                                            self.songResourcesBox.pos().y() + self.songResourcesBox.height()//2 + 50 - self.verticalScrollBar().value(),
                                            100, 100)
    def onSwitchIn(self):
        pass
    def onSwitchOut(self):
        pass
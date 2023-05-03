from Core.DataType import AutoTranslateWord, AutoTranslateWordList
from .AppPage import AppPage
from typing import Union, List, Optional, Literal
from Core import appManager, networkManager, musicDataManager, musicPlayerManager, localDataManager
from PySide2.QtWidgets import QFrame, QLayout, QWidget, QHBoxLayout, QVBoxLayout
from PySide2.QtCore import Qt
from PySide2.QtGui import QColor, QWheelEvent
from components import AppSearchBar_WithDropDown, AppScrollBox, AppTextLabel, AppLayoutBox
from ExternalPackage.pyqt5Custom import Spinner
import json
from functools import reduce, partial

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

        current_playlist = musicPlayerManager.currentMusicList
        if current_playlist is not None:
            for music_id in current_playlist.musicIDs:
                music = musicDataManager.getMusic(music_id)
                self.addSongItemToCurrentPlaylist(music, self.currentPlayListBox)

    # add song item to current play list
    def addSongItemToCurrentPlaylist(self, song, playlist):
        itemBox = AppLayoutBox(height=30, align='left', fontBold=True)
        song_title = song._title
        artist = song._artist or song._albumArtist or AutoTranslateWord('Unknown')
        itemBox.addText(song_title, stretch=1)
        itemBox.addText(artist, stretch=0)

        # 添加点击事件以播放歌曲
        itemBox.addOnLeftClickCallback(partial(self.play_music_by_id, song.id, itemBox))

        playlist.addComponent(itemBox)

    def play_music_by_id(self, musicID: int, itemBox: AppLayoutBox):
        music = musicDataManager.getMusic(musicID)
        lst = musicDataManager.getMusicList(-1)  # -1表示“所有歌曲”列表
        if musicPlayerManager.currentMusic is not None:
            if musicPlayerManager.currentMusic.id == musicID:
                musicPlayerManager.pause() if musicPlayerManager.isPlaying() else musicPlayerManager.play()
                return
        if musicPlayerManager.currentMusicList.id != -1:
            musicPlayerManager.setPlaylist(lst)
        lst.setCurrentIndex(lst._musicIDs.index(musicID))
        musicPlayerManager.stop()
        musicPlayerManager.setPosition(0)
        musicPlayerManager.play()

    #region methods for search song
    def _searchSongResourse(self, keywords:str, mode):
        if not networkManager.serverConnected:
            appManager.toast(AutoTranslateWord('server not connected'))
            return
        if keywords is None or keywords == "" or keywords.replace(" ", "") == "":
            appManager.toast(AutoTranslateWord('please enter keywords'))
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
                self._unlockSearch()
                return

            print('search finished, result: ', data)
            self.songResourcesBox.removeAllComponents()
            def downloadSong(hash):
                if localDataManager.hasFile(hash):
                    appManager.toast(AutoTranslateWord(f'song already downloaded'))
                    return
                # TODO: download song
            for song in data:
                targetList = song['names'] if _mode == 'name' else song['artists'] if _mode == 'artist' else song['albums']
                targetList = json.loads(targetList)
                targetIndex = None
                for i, s in enumerate(targetList):
                    if reduce(lambda a, b: a and b, map(lambda x: x in s, keywordList)):
                        targetIndex = i
                        break
                if targetIndex is None:
                    targetIndex = 0
                songName = json.loads(song['names'])[targetIndex] if song['names'] != "" and song['names'] is not None else AutoTranslateWord('Unknown')
                if len(songName) > 30:
                    songName = songName[:27] + '...'
                songArtist = json.loads(song['artists'])[targetIndex] if song['artists'] != "" and song['artists'] is not None else AutoTranslateWord('Unknown')
                if len(songArtist) > 13:
                    songArtist = songArtist[:10] + '...'
                songAlbum = json.loads(song['albums'])[targetIndex] if song['albums'] != "" and song['albums'] is not None else AutoTranslateWord('Unknown')
                if len(songAlbum) > 13:
                    songAlbum = songAlbum[:10] + '...'
                fileExt = song['fileExt'] if song['fileExt'] != "" and song['fileExt'] is not None else AutoTranslateWord('Unknown')
                fileSize = song['fileSize'] if song['fileSize'] != "" and song['fileSize'] is not None else AutoTranslateWord('Unknown')
                box = AppLayoutBox(parent=self.songResourcesBox)
                box.addText(songName, stretch=1)
                box.addText(songArtist, stretch=0)
                box.addText(songAlbum, stretch=0)
                box.addButton(text=AutoTranslateWord('download'), img=appManager.getUIImagePath('down_arrow.png'),command=partial(downloadSong, song['hash']))
                box.adjustSize()
                self.songResourcesBox.addComponent(box)

            self._unlockSearch()
        networkManager.create_async_thread(func=networkManager.findSong, args=(keywords, _mode),
                                           returnCallbacks=onSearchFinishCallback)
    def _lockSearch(self):
        self.searchSpinner.show()
        self.searchSpinner.play=True
        self.searchBar.searchButton.setEnabled(False)
        self.searchBar.inputArea.setEnabled(False)
        self.searchBar.dropDown.setEnabled(False)
        for _component in self.songResourcesBox.components:
            _component.setEnabled(False)
            if hasattr(_component, 'components'):
                for subComponent in _component.components:
                    subComponent.setEnabled(False)
    def _unlockSearch(self):
        self.searchSpinner.hide()
        self.searchSpinner.play=False
        self.searchBar.searchButton.setEnabled(True)
        self.searchBar.inputArea.setEnabled(True)
        self.searchBar.dropDown.setEnabled(True)
        for component in self.songResourcesBox.components:
            component.setEnabled(True)
            if hasattr(component,'components'):
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

from Core.DataType import FileType, FileInfo
from .AppPage import AppPage
from typing import Union, Sequence, Dict
from PySide2.QtWidgets import QFrame, QLayout, QWidget
from components import AppUploadFileArea_WithFileBox, AppSearchBar_WithDropDown, AppScrollBox, AppTextLabel, AppLayoutBox
from Core import AutoTranslateWord, AutoTranslateWordList, musicDataManager, localDataManager, appManager

class SongManagePage(AppPage):

    _musicBoxes: Dict[int, QWidget]  = {}

    def __init__(self, appWindow, parent: Union[QFrame, QLayout] = None):
        super().__init__(appWindow=appWindow, parent=parent, titleText=AutoTranslateWord("Song Manage"))

        # region upload area
        self.addComponent(AppTextLabel(text=AutoTranslateWord("Upload Song"),backgroundColor="transparent", textAlign="left", fontSize=20, fontBold=True))

        self.uploadArea = AppUploadFileArea_WithFileBox(appWindow=self.appWindow, hintText=AutoTranslateWord("Drag or click to add your song here"),
                                                   onlyAcceptFiles=tuple(FileType.AUDIO.value))
        self.uploadArea.fileBoxShowsType = False
        self.addComponent(self.uploadArea)
        # endregion

        # region search bar
        self.searchBar = AppSearchBar_WithDropDown(titleText=AutoTranslateWord("Search Song"),
                                                   dropdownChoices=AutoTranslateWordList("Song Name", "Artist", "Album"),
                                                   hintText=AutoTranslateWord("enter song Name"),
                                                   searchCommand=self.onSearch,
                                                   onCancelButtonClicked=self.refreshSongListBox)
        self.searchBar.dropDown.onChoiceChanged.connect(
            lambda key: self.searchBar.SetHintText({"Song Name": AutoTranslateWord('enter song Name'),
                                                    "Artist": AutoTranslateWord('enter artist name'),
                                                    'Album':AutoTranslateWord('enter album name')}[key]))
        self.addComponent(self.searchBar)
        # endregion

        # region song list box
        self.songListBox = AppScrollBox(height=300, titleText=AutoTranslateWord("All song"))
        self.addComponent(self.songListBox)
        # endregion

        self.uploadArea.addUploadButtonCommand(self.uploadMusicFiles)
        self.refreshSongListBox()

    def uploadMusicFiles(self, files: Sequence[FileInfo]):
        for fileinfo in files:
            music = musicDataManager.saveMusic(fileinfo)
            if music is None:
                if localDataManager.hasFile(fileinfo.getFileHash()):
                    self.appWindow.toast(AutoTranslateWord(f"[Music]: {fileinfo.fileName} [already exists in database]"))
                else:
                    self.appWindow.toast(AutoTranslateWord(f"[Music]: {fileinfo.fileName} [is not a valid music file]"))
            else:
                self.appWindow.toast(AutoTranslateWord(f"[Music]: {fileinfo.fileName} [uploaded successfully]"))
                self.uploadArea.removeFile(fileinfo)
                self.addMusicBoxToSongListBox(music)

    def addMusicBoxToSongListBox(self, music, order:int=None):
        itemBox = AppLayoutBox(height=30, align='left', parent=self.songListBox, fontBold=True)
        _name = music._title
        if len(_name) > 30:
            _name = _name[:27] + '...'
        else:
            _name = _name.ljust(30)
        itemBox.addText(_name, stretch=1)
        artist = (music._artist or music._albumArtist or AutoTranslateWord('Unknown'))
        if len(artist) > 20:
            artist = '...' + artist[:17]
        else:
            artist = artist.ljust(20)
        album = (music._album or AutoTranslateWord('Unknown album'))
        if len(album) > 20:
            album = '...' + album[:17]
        else:
            album = album.ljust(20)
        itemBox.addText(artist, stretch=1)
        itemBox.addText(album, stretch=1)
        itemBox.addText(AutoTranslateWord('[duration]: ') + music.duration_formatted.ljust(15), stretch=1)
        def deleteMusic(_music):
            musicDataManager.deleteMusic(_music)
            self.appWindow.toast(AutoTranslateWord(f"[Music]: {_music._title} [deleted successfully]"))
        itemBox.addButton(AutoTranslateWord('delete'), appManager.getUIImagePath('cross.png'),
                          command=lambda : deleteMusic(music))

        itemBox.adjustSize()
        setattr(itemBox,'_music',music)
        self._musicBoxes[music.id] = self.songListBox.addComponent(itemBox, order=order)
        music.addOnDeletedCallback(lambda _music:self.songListBox.removeComponent(itemBox))

    def onSearch(self, text: str, dropdownKey: str):
        texts = text.lower().split(' ')
        texts.remove('') if '' in texts else None
        if texts is None or len(texts) == 0:
            return
        added=False
        for id, music in musicDataManager.allMusics.items():
            if dropdownKey == "Song Name" :
                checkText = music._title
            elif dropdownKey == "Artist":
                checkText = music._artist or music._albumArtist or AutoTranslateWord('Unknown')
            elif dropdownKey == "Album":
                checkText = music._album or AutoTranslateWord('Unknown album')
            mapped = map(lambda x: x in checkText.lower(), texts)
            if all(mapped):
                if id not in self._musicBoxes:
                    self.addMusicBoxToSongListBox(music)
                    added=True
            else:
                if id in self._musicBoxes:
                    self.songListBox.removeComponent(self._musicBoxes[id])
                    del self._musicBoxes[id]
        if added:
            self.songListBox.expandLayout._widgets.sort(key=lambda x: x._music.id)

    def refreshSongListBox(self):
        for id, music in musicDataManager.allMusics.items():
            if id not in self._musicBoxes:
                self.addMusicBoxToSongListBox(music)
        self.songListBox.expandLayout._widgets.sort(key=lambda x: x._music.id)

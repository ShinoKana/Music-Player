from Core.DataType import FileType, FileInfo
from .AppPage import AppPage
from typing import Union, Sequence
from PySide2.QtWidgets import QFrame, QLayout
from components import AppUploadFileArea_WithFileBox, AppSearchBar_WithDropDown, AppScrollBox, AppTextLabel, AppLayoutBox
from Core import AutoTranslateWord, AutoTranslateWordList, musicDataManager, localDataManager, appManager

class SongManagePage(AppPage):
    def __init__(self, appWindow, parent: Union[QFrame, QLayout] = None):
        super().__init__(appWindow=appWindow, parent=parent, titleText=AutoTranslateWord("Song Manage"))

        self.addComponent(AppTextLabel(text=AutoTranslateWord("Upload Song"),backgroundColor="transparent", textAlign="left", fontSize=20, fontBold=True))

        self.uploadArea = AppUploadFileArea_WithFileBox(appWindow=self.appWindow, hintText=AutoTranslateWord("Drag or click to add your song here"),
                                                   onlyAcceptFiles=tuple(FileType.AUDIO.value))
        self.uploadArea.fileBoxShowsType = False
        def uploadMusicFiles(files: Sequence[FileInfo]):
            addedMusic = False
            for fileinfo in files:
                music = musicDataManager.saveMusic(fileinfo)
                if music is None:
                    if localDataManager.hasFile(fileinfo.getFileHash()):
                        self.appWindow.toast(AutoTranslateWord(f"Music {fileinfo.fileName} already exists in database"))
                    else:
                        self.appWindow.toast(AutoTranslateWord(f"Music {fileinfo.fileName} is not a valid music file"))
                else:
                    self.appWindow.toast(AutoTranslateWord(f"Music {fileinfo.fileName} uploaded successfully"))
                    self.uploadArea.removeFile(fileinfo)
                    addedMusic = True
            if addedMusic:
                self.refreshSongListBox()
        self.uploadArea.addUploadButtonCommand(uploadMusicFiles)
        self.addComponent(self.uploadArea)

        # region search bar
        self.searchBar = AppSearchBar_WithDropDown(titleText=AutoTranslateWord("Search Song"),
                                                   dropdownChoices=AutoTranslateWordList("Song Name", "Artist"),
                                                   hintText=AutoTranslateWord("enter song Name"))
        self.searchBar.dropDown.onChoiceChanged.connect(
            lambda key: self.searchBar.SetHintText({"Song Name": AutoTranslateWord('enter song Name'),
                                                    "Artist": AutoTranslateWord('enter artist name')}[key]))
        self.addComponent(self.searchBar)
        # endregion

        # region song list
        self.songListBox = AppScrollBox(height=300, titleText=AutoTranslateWord("All song"))
        self.addComponent(self.songListBox)

        self.refreshSongListBox()
        # endregion
    def refreshSongListBox(self):
        self.songListBox.removeAllComponents()
        for id, music in musicDataManager.allMusics.items():
            itemBox = AppLayoutBox(height=30, align='left', parent=self.songListBox, fontBold=True)
            _name = music._title
            if len(_name) > 30:
                _name = _name[:27] + '...'
            else:
                _name = _name.ljust(30)
            itemBox.addText(_name, stretch=1)
            artist = music._artist or music._albumArtist or AutoTranslateWord('Unknown')
            if len(artist) > 30:
                artist = '...' + artist[:27]
            else:
                artist = artist.ljust(20)
            itemBox.addText(artist, stretch=1)
            itemBox.addText(AutoTranslateWord('[duration]: ')+music.duration_formatted.ljust(15), stretch=1)
            itemBox.addButton(AutoTranslateWord('delete'), appManager.getUIImagePath('cross.png'),
                              command=lambda: print("TODO: delete music"))
            itemBox.adjustSize()
            self.songListBox.addComponent(itemBox)
    def onSwitchIn(self):
        pass
    def onSwitchOut(self):
        pass
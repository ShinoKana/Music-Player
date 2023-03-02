from functools import partial
from Core.DataType import AutoTranslateWord
from Core import appManager, musicDataManager, musicPlayerManager
from .AppPage import AppPage
from typing import Union
from PySide2.QtWidgets import QFrame, QLayout
from PySide2.QtGui import QColor
from components import AppFoldBox, AppButton, AppLayoutBox

class SongListPage(AppPage):
    _unfoldingSongListBoxIDs = []
    _allSongListBox = {}
    _currentMusicItemBox = None
    _originalMusicItemBoxColor = None
    def __init__(self, appWindow, parent: Union[QFrame, QLayout] = None):
        super().__init__(appWindow=appWindow, parent=parent, titleText=AutoTranslateWord("Song List"))
        self._unfoldingSongListBoxIDs = appManager.record.unfoldingSongList.value.split(',')
        self._unfoldingSongListBoxIDs.remove('') if '' in self._unfoldingSongListBoxIDs else None
        self._unfoldingSongListBoxIDs = [int(id) for id in self._unfoldingSongListBoxIDs]

        #create song list boxes
        lastSongID = appManager.record.lastSongIndex.value
        lastSongListID = appManager.record.lastSongList.value
        for listID, list in musicDataManager.allMusicLists.items():
            listBox = AppFoldBox(titleText=list.name if listID!=-1 else AutoTranslateWord("All Songs"))
            listBox.setMinimumWidth(self.width() -80)
            self.addComponent(listBox)
            self._allSongListBox[listID] = listBox
            setattr(listBox, "_id", listID)
            listBox.addOnShowCallback(partial(self.whenSongListBoxUnfolded, self._allSongListBox[listID]))
            listBox.addOnHideCallback(partial(self.whenSongListBoxFolded, self._allSongListBox[listID]))
            for i, musicID in enumerate(list.musicIDs):
                music = musicDataManager.getMusic(musicID)
                itemBox = AppLayoutBox(height=30, align='left', fontBold=True)
                if musicID == lastSongID and listID == lastSongListID:
                    self._currentMusicItemBox = itemBox
                    self._originalMusicItemBoxColor = itemBox.backgroundColor
                    itemBox.SetBackgroundColor(QColor('blue').darker() if appManager.config.isDarkTheme() else QColor('blue').lighter())
                _name = music._title
                if len(_name) > 50:
                    _name = _name[:47] + '...'
                else:
                    _name = _name.ljust(50)
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
                itemBox.addText(artist, stretch=0)
                itemBox.addText(album, stretch=0)
                itemBox.addText(music.duration_formatted.ljust(15), stretch=0)
                def deleteFromList(music, list):
                    print("TODO: delete music from list")
                if listID!= -1:
                    itemBox.addButton(AutoTranslateWord('delete from list'), appManager.getUIImagePath('cross.png'),
                                  command=lambda: deleteFromList(music ,list))
                itemBox.adjustSize()
                setattr(itemBox, '_music', music)
                itemBox.addOnLeftClickCallback(partial(self.onclickMusicItem, musicID,listID,i))
                listBox.addComponent(itemBox)
            if listID!=-1:
                button = AppButton(text=AutoTranslateWord("TODO"), command=lambda: print("TODO: add song"), height=30)
                listBox.addComponent(button)
            listBox.adjustSize()

        #add song list button
        self.addListButton = AppButton(text=AutoTranslateWord("Add Song List"), command=lambda :print("TODO: add song list"),
                                    icon=appManager.getUIImagePath('plus.png'), height=50)
        self.addComponent(self.addListButton)

        #unfolding lists according to record
        for listID in self._unfoldingSongListBoxIDs:
            self._allSongListBox[listID].showInner(emitCallback=False)
        musicDataManager.addOnMusicAddedCallback(lambda music: self.addMusicItemBoxToListBox(music,self._allSongListBox[-1]))

    def whenSongListBoxFolded(self, songListBox: AppFoldBox):
        self._unfoldingSongListBoxIDs.remove(songListBox._id) if songListBox._id in self._unfoldingSongListBoxIDs else None
        appManager.record.unfoldingSongList.value = ','.join([str(box) for box in self._unfoldingSongListBoxIDs])
    def whenSongListBoxUnfolded(self, songListBox: AppFoldBox):
        self._unfoldingSongListBoxIDs.append(songListBox._id) if songListBox._id not in self._unfoldingSongListBoxIDs else None
        appManager.record.unfoldingSongList.value = ','.join([str(box) for box in self._unfoldingSongListBoxIDs])
    def addMusicItemBoxToListBox(self, music, listBox: AppFoldBox):
        lst = musicDataManager.getMusicList(listBox._id)
        if music.id in lst._musicIDs:
            return
        itemBox = AppLayoutBox(height=30, align='left', fontBold=True)
        _name = music._title
        if len(_name) > 50:
            _name = _name[:47] + '...'
        else:
            _name = _name.ljust(50)
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
        itemBox.addText(artist, stretch=0)
        itemBox.addText(album, stretch=0)
        itemBox.addText(music.duration_formatted.ljust(15), stretch=0)

        def deleteFromList(music, list):
            print("TODO: delete music from list")

        itemBox.adjustSize()
        setattr(itemBox, '_music', music)
        itemBox.addOnLeftClickCallback(partial(self.onclickMusicItem, music.id, lst.id, len(listBox.components)))
        listBox.addComponent(itemBox)
        listBox.adjustSize()

    def onclickMusicItem(self, musicID: int, lstID: int, itemBoxIndex):
        lst = musicDataManager.getMusicList(lstID)
        itemBox = self._allSongListBox[lst._id].getComponentByIndex(itemBoxIndex)
        if musicPlayerManager.currentMusic is not None:
            if musicPlayerManager.currentMusic.id == musicID and musicPlayerManager.currentMusicList.id == lstID:
                musicPlayerManager.pause() if musicPlayerManager.state() == musicPlayerManager.PlayingState else musicPlayerManager.play()
                return
        if musicPlayerManager.currentMusicList.id == lstID:
            musicPlayerManager.setPlaylist(lst)
        if self._currentMusicItemBox != itemBox:
            self._currentMusicItemBox.SetBackgroundColor(
                self._originalMusicItemBoxColor) if self._currentMusicItemBox is not None else None
            self._currentMusicItemBox = itemBox
            self._originalMusicItemBoxColor = itemBox.backgroundColor
            itemBox.SetBackgroundColor(
                QColor('blue').darker() if appManager.config.isDarkTheme() else QColor('blue').lighter())
        lst.setCurrentIndex(lst._musicIDs.index(musicID))
        musicPlayerManager.setPosition(0)
        musicPlayerManager.play()

    def onSwitchIn(self):
        for box in self._allSongListBox.values():
            box.adjustSize()
    def onSwitchOut(self):
        pass
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
            self.addComponent(listBox, expandWidth=True)
            self._allSongListBox[listID] = listBox

            setattr(listBox, "_id", listID) # for convenience, add listID to listBox

            listBox.addOnShowCallback(partial(self.whenSongListBoxUnfolded, self._allSongListBox[listID]))
            listBox.addOnHideCallback(partial(self.whenSongListBoxFolded, self._allSongListBox[listID]))

            for i, musicID in enumerate(list.musicIDs):
                music = musicDataManager.getMusic(musicID)
                box = self.addMusicItemBoxToListBox(music, listBox, adjustListBoxSizeAtFinal=False)
                if musicID == lastSongID and listID == lastSongListID:
                    self._currentMusicItemBox = box
                    self._originalMusicItemBoxColor = box.backgroundColor
                    box.SetBackgroundColor(QColor('blue').lighter() if appManager.config.isDarkTheme() else QColor('blue').darker())
            if listID!=-1:
                button = AppButton(text=AutoTranslateWord("TODO"), command=lambda: print("TODO: add song"), height=30)
                listBox.addComponent(button)
            listBox.adjustSize()

        # region create-new-list button
        self.addListButton = AppButton(text=AutoTranslateWord("Add Song List"), command=lambda :print("TODO: add song list"),
                                    icon=appManager.getUIImagePath('plus.png'), height=50)
        self.addComponent(self.addListButton)
        # endregion

        # unfolding lists according to record
        for listID in self._unfoldingSongListBoxIDs:
            self._allSongListBox[listID].showInner(emitCallback=False)
        musicDataManager.addOnMusicAddedCallback(lambda music: self.addMusicItemBoxToListBox(music, self._allSongListBox[-1])) #add to 'all songs' list

    def whenSongListBoxFolded(self, songListBox: AppFoldBox):
        self._unfoldingSongListBoxIDs.remove(songListBox._id) if songListBox._id in self._unfoldingSongListBoxIDs else None
        appManager.record.unfoldingSongList.value = ','.join([str(box) for box in self._unfoldingSongListBoxIDs])
    def whenSongListBoxUnfolded(self, songListBox: AppFoldBox):
        self._unfoldingSongListBoxIDs.append(songListBox._id) if songListBox._id not in self._unfoldingSongListBoxIDs else None
        appManager.record.unfoldingSongList.value = ','.join([str(box) for box in self._unfoldingSongListBoxIDs])

    def addMusicItemBoxToListBox(self, music, listBox: AppFoldBox, adjustListBoxSizeAtFinal=True) -> Union[None, AppLayoutBox]:
        listID = listBox._id
        lst = musicDataManager.getMusicList(listID)
        itemBox = AppLayoutBox(height=30, align='left', fontBold=True)

        # region text boxes
        _name = music._title
        if len(_name) > 40:
            _name = _name[:37] + '...'
        else:
            _name = _name.ljust(40)
        artist = (music._artist or music._albumArtist or AutoTranslateWord('Unknown'))
        if len(artist) > 30:
            artist = '...' + artist[:27]
        else:
            artist = artist.ljust(30)
        album = (music._album or AutoTranslateWord('Unknown album'))
        if len(album) > 20:
            album = '...' + album[:17]
        else:
            album = album.ljust(20)
        itemBox.addText(_name, stretch=1)
        itemBox.addText(artist, stretch=0)
        itemBox.addText(album, stretch=0)
        itemBox.addText(music.duration_formatted.ljust(15), stretch=0)
        # endregion

        # region delete button
        def deleteFromList(music, list):
            print("TODO: delete music from list")
        if listID != -1:
            itemBox.addButton(AutoTranslateWord('delete from list'), appManager.getUIImagePath('cross.png'),
                              command=lambda: deleteFromList(music, list))
        # endregion

        setattr(itemBox, '_music', music) #for convenience
        itemBox.addOnLeftClickCallback(partial(self._onclickMusicItem, music.id, lst.id, len(listBox.components)))
        def musicDeletedOrRemovedCallback(_music):
            if _music == itemBox._music:
                self.removeMusicItemFromListBox(_music, listBox)
                if self._currentMusicItemBox == itemBox:
                    self._currentMusicItemBox = None
        itemBox._musicDeletedOrRemovedCallback = musicDeletedOrRemovedCallback
        music.addOnDeletedCallback(itemBox._musicDeletedOrRemovedCallback)
        lst.addOnMusicRemovedCallback(itemBox._musicDeletedOrRemovedCallback)
        listBox.addComponent(itemBox)
        if adjustListBoxSizeAtFinal:
            listBox.adjustSize()
        return itemBox

    def removeMusicItemFromListBox(self, music, listBox: AppFoldBox):
        for box in listBox.components:
            if box._music.id == music.id:
                listBox.removeComponent(box)
                lst = musicDataManager.getMusicList(listBox._id)
                lst.removeOnMusicRemovedCallback(box._musicDeletedOrRemovedCallback)
                music.removeOnDeletedCallback(box._musicDeletedOrRemovedCallback)
                break

    def _onclickMusicItem(self, musicID: int, lstID: int, itemBoxIndex):
        lst = musicDataManager.getMusicList(lstID)
        itemBox = self._allSongListBox[lst._id].getComponentByIndex(itemBoxIndex)
        if musicPlayerManager.currentMusic is not None:
            if musicPlayerManager.currentMusic.id == musicID and musicPlayerManager.currentMusicList.id == lstID:
                musicPlayerManager.pause() if musicPlayerManager.isPlaying() else musicPlayerManager.play()
                return
        if musicPlayerManager.currentMusicList.id == lstID:
            musicPlayerManager.setPlaylist(lst)
        if self._currentMusicItemBox != itemBox:
            self._currentMusicItemBox.SetBackgroundColor(
                self._originalMusicItemBoxColor) if self._currentMusicItemBox is not None else None
            self._currentMusicItemBox = itemBox
            self._originalMusicItemBoxColor = itemBox.backgroundColor
            itemBox.SetBackgroundColor(
                QColor('blue').lighter() if appManager.config.isDarkTheme() else QColor('blue').darker())
        lst.setCurrentIndex(lst._musicIDs.index(musicID))
        musicPlayerManager.setPosition(0)
        musicPlayerManager.play()

    def onSwitchIn(self):
        for box in self._allSongListBox.values():
            box.adjustSize()

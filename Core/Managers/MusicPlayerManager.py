from PySide2.QtMultimedia import QMediaPlayer, QMediaPlaylist
from Core import appManager, musicDataManager, MusicList
from PySide2.QtCore import Signal
from typing import Literal
from .Manager import *
from Core.Media.EXPlayer import *


# Changed the inheritance of QMediaPlay to EXPlayer, and EXPlayer calls QMediaPlayer and WavPlayer in a combined way
class MusicPlayerManager(Manager, EXPlayer):

    _playlist: MusicList = None
    _onPlayModeChanged = []
    _onPlayListChanged = []
    _onMusicChanged = []
    _onClear = []

    def __init__(self):
        EXPlayer.__init__(self, musicDataManager.getMusicList(appManager.record.lastSongList.value), appManager.record.lastSongTime.value)
        self._currentMusic = musicDataManager.getMusic(appManager.record.lastSongIndex.value)
        #playlist
        def playlistMusicRemovedCallback(music:'Music'):
            if self._currentMusic == music:
                try:
                    self.goNextMusic()
                    self.stop()
                except:
                    self.clear()

        self.playlisyMusicRemovedCallback = playlistMusicRemovedCallback
        #TODO callback for whole playlist deleted
        self._playlist = musicDataManager.getMusicList(appManager.record.lastSongList.value)
        self._playlist.setPlaybackMode(self.QTplayMode)
        if self._currentMusic is not None:
            self._playlist.setCurrentIndex(self._playlist._musicIDs.index(self._currentMusic._id))

        self.volume = appManager.record.soundVolume.value
        self.playMode = appManager.record.musicPlayMode.value

        def onMediaChanged():
            self._currentMusic = self._playlist.currentMusic
            for func in self._onMusicChanged:
                func(self._currentMusic)
        self.currentMediaChanged.connect(lambda media: onMediaChanged())

    def __del__(self):
        appManager.record.lastSongTime.value = self.position
        appManager.record.lastSongIndex.value = self._currentMusic._id if self._currentMusic is not None else 0
        appManager.record.lastSongList.value = self._playlist._id if self._playlist is not None else -1
        self.stop() # must stop to kill the thread

    # region callbacks
    def addOnMusicChanged(self, func) -> None:
        self._onMusicChanged.append(func) if func not in self._onMusicChanged else None
    def removeOnMusicChanged(self, func) -> None:
        self._onMusicChanged.remove(func) if func in self._onMusicChanged else None
    def addOnPlayModeChanged(self, func) -> None:
        self._onPlayModeChanged.append(func) if func not in self._onPlayModeChanged else None
    def addOnPlayListChanged(self, func) -> None:
        self._onPlayListChanged.append(func) if func not in self._onPlayListChanged else None
    def removeOnPlayModeChanged(self, func) -> None:
        self._onPlayModeChanged.remove(func) if func in self._onPlayModeChanged else None
    def removeOnPlayListChanged(self, func) -> None:
        self._onPlayListChanged.remove(func) if func in self._onPlayListChanged else None
    def addOnClearCallback(self, func) -> None:
        self._onClear.append(func) if func not in self._onClear else None
    def removeOnClearCallback(self, func) -> None:
        self._onClear.remove(func) if func in self._onClear else None
    # endregion

    # region properties
    @property
    def currentMusic(self) -> 'Music':
        return self._currentMusic
    @property
    def currentMusicList(self) -> 'MusicList':
        return self._playlist
    @currentMusicList.setter
    def currentMusicList(self, playlist: MusicList) -> None:
        EXPlayer._setPlaylist(playlist)
    def setPlaylist(self, playlist: MusicList) -> None:
        EXPlayer._setPlaylist(self, playlist)
        if self._playlist:
            self._playlist.removeOnMusicRemovedCallback(self.playlisyMusicRemovedCallback)
        self._playlist = playlist
        self._playlist.addOnMusicRemovedCallback(self.playlisyMusicRemovedCallback)
        playlist.setPlaybackMode(self.QTplayMode)
        for func in self._onPlayListChanged:
            func(playlist)
    @property
    def playMode(self) -> str:
        return appManager.record.musicPlayMode.value
    @playMode.setter
    def playMode(self, mode:Literal['listLoop','random','loop']) -> None:
        appManager.record.musicPlayMode.value = mode
        for func in self._onPlayModeChanged:
            func(mode)
        if self._playlist:
            if mode == "listLoop":
                self._playlist.setPlaybackMode(QMediaPlaylist.PlaybackMode.Sequential)
            elif mode == "random":
                self._playlist.setPlaybackMode(QMediaPlaylist.PlaybackMode.Random)
            else:
                self._playlist.setPlaybackMode(QMediaPlaylist.PlaybackMode.Loop)
    @property
    def QTplayMode(self) -> QMediaPlaylist.PlaybackMode:
        if self.playMode == "listLoop":
            return QMediaPlaylist.PlaybackMode.Sequential
        elif self.playMode == "random":
            return QMediaPlaylist.PlaybackMode.Random
        elif self.playMode == "loop":
            return QMediaPlaylist.PlaybackMode.Loop
    @property
    def volume(self) -> int:
        return appManager.record.soundVolume.value
    @volume.setter
    def volume(self, volume:int) -> None:
        appManager.record.soundVolume.value = volume
        EXPlayer.setVolume(self, self.volume)
    def setVolume(self, volume:int) -> None:
        '''override QMediaPlayer.setVolume'''
        self.volume = volume
    # endregion

    # region methods
    def clear(self):
        self.stop()
        self.setPlaylist(musicDataManager.getMusicList(-1)) # -1 is the default music list
        self._currentMusic = None
        for func in self._onClear:
            func()
    def goNextMusic(self) -> None:
        if self.playMode == 'listLoop' and self._playlist.currentIndex() == self._playlist.mediaCount() - 1:
            self._playlist.setCurrentIndex(0)
        else:
            self._playlist.next()
        self.stop()
        self.play()
    def goPreviousMusic(self) -> None:
        if self.playMode == 'listLoop' and self._playlist.currentIndex() == 0:
            self._playlist.setCurrentIndex(self._playlist.mediaCount() - 1)
        else:
            self._playlist.previous()
        self.stop()
        self.play()
    # endregion

musicPlayerManager = MusicPlayerManager()
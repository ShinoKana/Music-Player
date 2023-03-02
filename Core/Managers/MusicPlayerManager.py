from PySide2.QtMultimedia import QMediaPlayer, QMediaPlaylist
from Core import appManager, musicDataManager, MusicList
from typing import Literal
from .Manager import *

class MusicPlayerManager(Manager, QMediaPlayer):
    _playlist: MusicList = None
    def __init__(self):
        QMediaPlayer.__init__(self)
        self._onPlayModeChanged = []
        self._onPlayListChanged = []
        self._onMusicChanged = []
        self._onClear = []
        self.playMode = appManager.record.musicPlayMode.value
        self.volume = appManager.record.soundVolume.value
        self._currentMusic = musicDataManager.getMusic(appManager.record.lastSongIndex.value)
        self._playlist = musicDataManager.getMusicList(appManager.record.lastSongList.value)
        self.setPlaylist(self._playlist)
        self._playlist.setPlaybackMode(self.QTplayMode)
        if self._currentMusic is not None:
            self._playlist.setCurrentIndex(self._playlist._musicIDs.index(self._currentMusic._id))
        self.setPosition(appManager.record.lastSongTime.value)
        def onMediaChanged():
            self._currentMusic = self._playlist.currentMusic
            for func in self._onMusicChanged:
                func(self._currentMusic)
        self.currentMediaChanged.connect(lambda media: onMediaChanged())

    def __del__(self):
        appManager.record.lastSongTime.value = self.position()
        appManager.record.lastSongIndex.value = self._currentMusic._id if self._currentMusic is not None else 0
        appManager.record.lastSongList.value = self._playlist._id if self._playlist is not None else -1

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
    def clear(self):
        self.stop()
        self.setPlaylist(musicDataManager.getMusicList(-1)) # -1 is the default music list
        self._currentMusic = None
        for func in self._onClear:
            func()
    @property
    def currentMusic(self) -> 'Music':
        return self._currentMusic
    @property
    def currentMusicList(self) -> 'MusicList':
        return self._playlist
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
        QMediaPlayer.setVolume(self, self.volume)
    def setVolume(self, volume:int) -> None:
        '''override QMediaPlayer.setVolume'''
        self.volume = volume

    def setPlaylist(self, playlist: MusicList) -> None:
        QMediaPlayer.setPlaylist(self, playlist)
        self._playlist = playlist
        playlist.setPlaybackMode(self.QTplayMode)
        for func in self._onPlayListChanged:
            func(playlist)

    def goNextMusic(self) -> None:
        if self.playMode == 'listLoop' and self._playlist.currentIndex() == self._playlist.mediaCount() - 1:
            self._playlist.setCurrentIndex(0)
        else:
            self._playlist.next()
    def goPreviousMusic(self) -> None:
        if self.playMode == 'listLoop' and self._playlist.currentIndex() == 0:
            self._playlist.setCurrentIndex(self._playlist.mediaCount() - 1)
        else:
            self._playlist.previous()


musicPlayerManager = MusicPlayerManager()
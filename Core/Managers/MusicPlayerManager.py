from PySide2.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PySide2.QtCore import QUrl
from Core import appManager
from typing import Literal
from .Manager import *

class MusicPlayerManager(QMediaPlayer, Manager):

    def __init__(self):
        QMediaPlayer.__init__(self)
        self._playlist = QMediaPlaylist()
        self.setPlaylist(self._playlist)
        self.playMode = appManager.record.musicPlayMode.value
        self.volume = appManager.record.soundVolume.value

        '''testMusicPath = appManager.DATA_PATH+ "/test"
        self._playlist.addMedia(QMediaContent(QUrl.fromLocalFile(testMusicPath)))
        self._playlist.setCurrentIndex(0)
        self.play()'''

    @property
    def playMode(self) -> str:
        return appManager.record.musicPlayMode.value
    @playMode.setter
    def playMode(self, mode:Literal['listLoop','random','loop']) -> None:
        if mode == "listLoop":
            self._playlist.setPlaybackMode(QMediaPlaylist.PlaybackMode.Sequential)
        elif mode == "random":
            self._playlist.setPlaybackMode(QMediaPlaylist.PlaybackMode.Random)
        else:
            self._playlist.setPlaybackMode(QMediaPlaylist.PlaybackMode.Loop)
        appManager.record.musicPlayMode.value = mode

    @property
    def volume(self) -> int:
        return appManager.record.soundVolume.value
    @volume.setter
    def volume(self, volume:int) -> None:
        appManager.record.soundVolume.value = volume
        QMediaPlayer.setVolume(self, self.volume)


musicPlayerManager = MusicPlayerManager()
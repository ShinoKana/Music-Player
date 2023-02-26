from PySide2.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from Core import appManager

from .Manager import *
@Manager
class MusicPlayerManager(QMediaPlayer):
    def __init__(self):
        super().__init__()
        self._playlist = QMediaPlaylist()
        playMode = appManager.record.musicPlayMode.value
        if playMode == "listLoop":
            playMode = QMediaPlaylist.PlaybackMode.Sequential
        elif playMode == "random":
            playMode = QMediaPlaylist.PlaybackMode.Random
        else:
            playMode = QMediaPlaylist.PlaybackMode.Loop
        self._playlist.setPlaybackMode(playMode)
        self.setPlaylist(self._playlist)
        super().setVolume(appManager.record.soundVolume.value)

    def setVolume(self, volume:int) -> None:
        appManager.record.soundVolume.value = volume
        super().setVolume(appManager.record.soundVolume.value) #correct value

musicPlayerManager = MusicPlayerManager()
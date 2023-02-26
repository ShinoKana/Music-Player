from PySide2.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
import Core

from .Manager import *
@Manager
class MusicPlayerManager(QMediaPlayer):
    def __init__(self):
        if not Core.localDataManager.hasTable('music'):
            Core.localDataManager.createTable('music', (
                ('id', 'TEXT PRIMARY KEY NOT NULL'),
                ('name', 'TEXT'),
                ('artist', 'TEXT'),
                ('coverHash', 'TEXT'),
                ('musicHash', 'TEXT'),
                ('lyricHash', 'TEXT'),
                ('length', 'INTEGER'),
            ))

        self._playlist = QMediaPlaylist()
        playMode = Core.appManager.record.musicPlayMode.value
        if playMode == "listLoop":
            playMode = QMediaPlaylist.PlaybackMode.Sequential
        elif playMode == "random":
            playMode = QMediaPlaylist.PlaybackMode.Random
        else:
            playMode = QMediaPlaylist.PlaybackMode.Loop
        self._playlist.setPlaybackMode(playMode)
        self.setPlaylist(self._playlist)
        super().setVolume(Core.appManager.record.soundVolume.value)
    def setVolume(self, volume:int) -> None:
        Core.appManager.record.soundVolume.value = volume
        super().setVolume(Core.appManager.record.soundVolume.value) #correct value

musicPlayerManager = MusicPlayerManager()
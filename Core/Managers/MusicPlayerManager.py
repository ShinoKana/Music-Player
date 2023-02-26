from PySide2.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from .Manager import *

@Manager
class MusicPlayerManager(QMediaPlayer):
    def __init__(self):
        self._playlist = QMediaPlaylist()
        self._playlist.setPlaybackMode(QMediaPlaylist.Loop)
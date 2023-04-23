from PySide2.QtCore import Signal, QObject 
try:
    from Core.Media import WavWriter
except Exception as e:
    #"only support Win"
    pass
from Core.Managers.Manager import *
from Core.Managers.MusicDataManager import MusicList, Music
from enum import Enum

class WavPlayer(QObject):
    class State(Enum):
        StoppedState = 0x00
        PlayingState = 0x01
        PausedState = 0x02

    _currentMusic: 'Music' = None
    _audio = None
    _volume = 50
    _position = 0
    _musicList = None
    _music = None
    positionChanged = Signal(int)
    stateChanged = Signal(State)
    def __init__(self):
        super().__init__()

    @property
    def position(self):
        return self._position
     
    def decision(self):
        return self._music is not None and self._music._fileName.endswith("wav") and OSType.CurrentOS() == OSType.win
        #return self._musicList is not None and self._musicList.currentMusic._fileName.endswith("wav") and OSType.CurrentOS() == OSType.win
    
    def setPlaylist(self, musicList : 'MusicList'):
        self._musicList = musicList 

    def setMusic(self, music : 'Music'):
        self._music = music
    
    def setPosition(self, position: int):
        self._position = position
        if self._audio is not None and self._audio.is_alive():
            self._audio.setPosition(self._position)

    def setVolume(self, volume):
        self._volume = volume
        if self._audio is not None and self._audio.is_alive():
            self._audio.setVolume(volume / 100) 
    
    def play(self) -> None:
        music = self._music
        if self._audio is not None and not self._audio.is_alive() and self._audio.isPause():
            self._audio.resume()
        else:
            if self._audio is not None and self._audio.is_alive():
                self._audio._positionChanged = []
                self._audio._stateChanged = []
                self._audio.kill()
            self._audio = WavWriter.WavWriter()
            self._audio.addPositionChangedCallBack(lambda position : self.positionChanged.emit(position))
            self._audio.addStateChangedCallBack(lambda state : self.stateChanged.emit(WavPlayer.State(state.value)))
            self._audio.open(music.filePath)
            self._audio.position = self._position
            self._audio.setVolume(self._volume / 100) 
            self._audio.start()
    
    def isPlaying(self) -> bool:
        if self._audio is None or not self._audio.is_alive() or not self._audio.isPlaying():
            return False
        return True

    def pause(self) -> None:
        if self._audio is not None and self._audio.is_alive() and self._audio.isPlaying():
            self._audio.pause()

    def stop(self) -> None:
        if self._audio is not None and self._audio.is_alive():
            self._audio.stop()
from PySide2.QtCore import Signal, QObject 
from PySide2.QtMultimedia import QMediaPlayer, QMediaPlaylist
from Core.Media.WavPlayer import WavPlayer
from Core.Managers.MusicDataManager import Music, MusicList
from enum import Enum
import types

# 对MusicPlayer所需要的接口进行了一些封装，里面的调用哪个播放器由播放器初始化顺序以及他们的decision决定
class EXPlayer(QObject):

    class State(Enum):
        StoppedState = 0
        PlayingState = 1
        PausedState = 2

    positionChanged = Signal(int)
    currentMediaChanged = Signal(Music)
    stateChanged = Signal(State)

    _audios = []
    _playList = None
    _lastPlayer = None
    _position = 0
    _userPlaying = None

    def __init__(self, playList: MusicList, position: int):
        super().__init__()
        self.wavPlayer = WavPlayer()
        self.defaultPlayer = QMediaPlayer()
        self._position = position

        # defaultPlayer Wrapper begin
        def defaultPlayerStateWrapper(state:QMediaPlayer.State):
            if state == QMediaPlayer.PlayingState:
                self.stateChanged.emit(EXPlayer.State.PlayingState)
            elif state == QMediaPlayer.StoppedState:
                self.stateChanged.emit(EXPlayer.State.StoppedState)
            else:
                self.stateChanged.emit(EXPlayer.State.PausedState)
        self.defaultPlayer.stateChanged.connect(defaultPlayerStateWrapper)
        self.defaultPlayer.isPlaying = types.MethodType(lambda self : self.state() == QMediaPlayer.State.PlayingState, self.defaultPlayer)
        self.defaultPlayer.decision = types.MethodType(lambda self : True, self.defaultPlayer)
        # defaultPlayer Wrapper end

        def wavPlayerStateWrapper(state: WavPlayer.State):
            if state == WavPlayer.State.PlayingState:
                self.stateChanged.emit(EXPlayer.State.PlayingState)
            elif state == WavPlayer.State.StoppedState:
                self.stateChanged.emit(EXPlayer.State.StoppedState)
            else:
                self.stateChanged.emit(EXPlayer.State.PausedState)
        self.wavPlayer.stateChanged.connect(wavPlayerStateWrapper)

        self._audios = [self.wavPlayer, self.defaultPlayer]

        self._setPlaylist(playList)

        #for go next playlist
        def stateChangedEffectPlayList(state: EXPlayer.State):
            if state == EXPlayer.State.StoppedState and self._userPlaying and self._playList.playbackMode() != QMediaPlaylist.CurrentItemOnce:
                if self._playList.playbackMode() == QMediaPlaylist.Sequential and self._playList.currentIndex() == self._playlist.mediaCount() - 1:
                    self._playList.setCurrentIndex(0)
                else:
                    self._playList.next()
                self.position = 0
                self.stop()
                self.play()

        self.stateChanged.connect(stateChangedEffectPlayList)

        def postionChangedCallBack(position: int) -> None:
            self.positionChanged.emit(position)
            self.position = position
        self._playList.currentMediaChanged.connect(lambda music : self.currentMediaChanged.emit(music))
        for audio in self._audios:
            if hasattr(audio, 'positionChanged'):
                audio.positionChanged.connect(lambda position : postionChangedCallBack(position)) 

    def _setPlaylist(self, playList: MusicList) -> None:
        self._playList = playList
        ## init position
        hasInit = False
        for audio in self._audios:
            # can't do that, control play by self
            # if hasattr(audio, 'setPlaylist'):
            #    audio.setPlaylist(playList)
            if not hasInit and audio.decision():
                hasInit = True
                audio.setPosition(self.position)
            else:
                audio.setPosition(0)

    def play(self) -> None:
        if self._userPlaying:
            self.position = 0
        self._userPlaying = True
        # only one audio can play 
        for audio in self._audios:
            if hasattr(audio, 'setMedia'):
                # 这里是因为如果QMediaPlayer没有playerlist的时候，当新设置了media的时候，position就会初始化为0，所以这里setMedia前先把历史的position保存起来
                if audio.media() != self._playList.currentMedia():
                    old_position = self.position
                    audio.setMedia(self._playList.currentMedia())
                    audio.setPosition(old_position)
            if hasattr(audio, 'setMusic'):
                audio.setMusic(self._playList.currentMusic)
            if audio.decision():
                if isinstance(audio, WavPlayer):
                    print('using wav player')
                elif isinstance(audio, QMediaPlayer):
                    print('using default player')
                audio.setPosition(self.position)
                audio.play()
                self._lastPlayer = audio
                break
        
    def stop(self) -> None:
        self._userPlaying = False
        self.position = 0
        if self._lastPlayer is not None:
            self._lastPlayer.stop()
    
    def pause(self) -> None:
        self._userPlaying = False
        if self._lastPlayer is not None:
            self._lastPlayer.pause()
    
    def setVolume(self, volume) -> None:
        for audio in self._audios:
            audio.setVolume(volume)
    
    def isPlaying(self) -> bool:
        #if self._lastPlayer is not None:
        #    return self._lastPlayer.isPlaying() 
        return self._userPlaying

    @property
    def position(self) -> int:
        return self._position
    @position.setter
    def position(self, position: int) -> None:
        self._position = position

    def setPosition(self, position: int) -> None:
        self.position = position
        if self._lastPlayer is not None:
            self._lastPlayer.setPosition(position)
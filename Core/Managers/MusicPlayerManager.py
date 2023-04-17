import binascii
import io
import wave
import audioop
import platform
from PySide2.QtMultimedia import QMediaPlayer, QMediaPlaylist
from Core import appManager, musicDataManager, MusicList
from typing import Literal
from .Manager import *


class MusicPlayerManager(Manager, QMediaPlayer):

    _playlist: MusicList = None
    _onPlayModeChanged = []
    _onPlayListChanged = []
    _onMusicChanged = []
    _onClear = []

    def __init__(self):
        QMediaPlayer.__init__(self)
        self.playMode = appManager.record.musicPlayMode.value
        self.volume = appManager.record.soundVolume.value
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
        self.setPlaylist(self._playlist) #playlist must not None
        self._playlist.setPlaybackMode(self.QTplayMode)
        self._playlist.currentIndexChanged.connect(self.onMediaChanged)

        if self._currentMusic is not None:
            self._playlist.setCurrentIndex(self._playlist._musicIDs.index(self._currentMusic._id))
        self.setPosition(appManager.record.lastSongTime.value)
        
        def onMediaChanged(self):
            QMediaPlayer.stop(self)
            self._currentMusic = self._playlist.currentMusic
            wav_info = self.get_wav_info(self._currentMusic.filepath)
            self.play_wav_data(wav_info["data"], wav_info["SampleRate"], wav_info["NumChannels"], wav_info["BitsPerSample"])
        self.currentMediaChanged.connect(lambda media: onMediaChanged())

    def __del__(self):
        appManager.record.lastSongTime.value = self.position()
        appManager.record.lastSongIndex.value = self._currentMusic._id if self._currentMusic is not None else 0
        appManager.record.lastSongList.value = self._playlist._id if self._playlist is not None else -1

    def hex2dec(self, hex, rev=True):
        if rev:
            hex = str(hex)[2:-1]
            new_hex = ''.join(reversed([hex[i:i+2] for i in range(0, len(hex), 2)]))
            new_hex = "0X" + new_hex
        else:
            new_hex = hex
        result_dec = int(new_hex, 16)
        return result_dec

    def get_wav_info(self, filename):
        info = dict()
        with open(filename, mode="rb") as f:
            info["ChunkID"] = f.read(4)
            if info["ChunkID"] != b'RIFF':
                raise ValueError("Invalid WAV file: file does not start with RIFF id")
            info["ChunkSize"] = self.hex2dec(binascii.hexlify(f.read(4)))
            info["Format"] = f.read(4)
            info["Subchunk1ID"] = f.read(4)
            info["Subchunk1Size"] = self.hex2dec(binascii.hexlify(f.read(4)))
            info["AudioFormat"] = self.hex2dec(binascii.hexlify(f.read(2)))
            info["NumChannels"] = self.hex2dec(binascii.hexlify(f.read(2)))
            info["SampleRate"] = self.hex2dec(binascii.hexlify(f.read(4)))
            info["ByteRate"] = self.hex2dec(binascii.hexlify(f.read(4)))
            info["BlockAlign"] = self.hex2dec(binascii.hexlify(f.read(2)))
            info["BitsPerSample"] = self.hex2dec(binascii.hexlify(f.read(2)))
            info["Subchunk2ID"] = f.read(4)
            info["Subchunk2Size"] = self.hex2dec(binascii.hexlify(f.read(4)))
            info["data"] = f.read(info["Subchunk2Size"])
        return info

    def onMediaChanged(self):
        self._currentMusic = self._playlist.currentMusic
        wav_info = self.get_wav_info(self._currentMusic.filePath)
        self.play_wav_data(wav_info["data"], wav_info["SampleRate"], wav_info["NumChannels"], wav_info["BitsPerSample"])

    
    def play_wav_data(self, wav_data, sample_rate, num_channels, bits_per_sample):
        with io.BytesIO(wav_data) as wf:
            wav_file = wave.open(wf, 'rb')

            if platform.system() == 'Windows':
                import winsound
                winsound.PlaySound(wf, winsound.SND_MEMORY)
            else:
                import ossaudiodev

                audio = ossaudiodev.open('w')
                audio.setparameters(ossaudiodev.AFMT_S16_NE, num_channels, sample_rate)
                audio.write(wav_file.readframes(wav_file.getnframes()))

                audio.close()

            wav_file.close()

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
        self.setPlaylist(playlist)
    def setPlaylist(self, playlist: MusicList) -> None:
        QMediaPlayer.setPlaylist(self, playlist)
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
        QMediaPlayer.setVolume(self, self.volume)
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
    def goPreviousMusic(self) -> None:
        if self.playMode == 'listLoop' and self._playlist.currentIndex() == 0:
            self._playlist.setCurrentIndex(self._playlist.mediaCount() - 1)
        else:
            self._playlist.previous()
    # endregion

musicPlayerManager = MusicPlayerManager()

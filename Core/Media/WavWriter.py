import sys
import time
import threading
import ctypes
import array
from enum import Enum
from ctypes import wintypes
import binascii

winmm = ctypes.windll.winmm

# same as WavPlayer.state
class PlayState(Enum):
    playing = 0x1
    pause = 0x2 
    stop = 0x0
    kill = 0x3


WAVE_FORMAT_PCM = 0x1
WAVE_MAPPER = -1 ## 默认可播放设备
MMSYSERR_NOERROR = 0
WAV_HEADER_SIZE = 44

## https://learn.microsoft.com/zh-tw/windows/win32/api/mmeapi/nf-mmeapi-waveoutopen 各种文档
# Define WAVEFORMATEX structure
class WAVEFORMATEX(ctypes.Structure):
  _fields_ = [
    ("wFormatTag", ctypes.c_ushort),
    ("nChannels", ctypes.c_ushort),
    ("nSamplesPerSec", ctypes.c_uint),
    ("nAvgBytesPerSec", ctypes.c_uint),
    ("nBlockAlign", ctypes.c_ushort),
    ("wBitsPerSample", ctypes.c_ushort),
    ("cbSize", ctypes.c_ushort)
  ]


PVOID = wintypes.HANDLE
WAVERR_BASE = 32
WAVERR_STILLPLAYING = WAVERR_BASE + 1

# Define WAVEHDR structure
class WAVEHDR(ctypes.Structure):
  _fields_ = [
    ("lpData", ctypes.c_char_p),
    ("dwBufferLength", ctypes.c_uint),
    ("dwBytesRecorded", ctypes.c_uint),
    ("dwUser", ctypes.c_void_p),
    ("dwFlags", ctypes.c_uint),
    ("dwLoops", ctypes.c_uint),
    ("lpNext", ctypes.c_void_p),
    ("reserved", ctypes.c_void_p)
  ]

WHDR_DONE = 0x1 

## https://www.wenjiangs.com/doc/nlvgsu4qaswv
#WHDR_DONE      = $00000001; {设备已使用完缓冲区, 并返回给程序}
#WHDR_PREPARED  = $00000002; {waveInPrepareHeader 或 waveOutPrepareHeader 已将缓冲区准备好}
#WHDR_BEGINLOOP = $00000004; {缓冲区是循环中的第一个缓冲区, 仅用于输出}
#WHDR_ENDLOOP   = $00000008; {缓冲区是循环中的最后一个缓冲区, 仅用于输出}
#WHDR_INQUEUE   = $00000010; { reserved for driver }


def hex2dec(hex, rev=True):
    if rev:
        hex = str(hex)[2:-1]
        new_hex = '0X' + \
            ''.join(reversed([hex[i:i + 2] for i in range(0, len(hex), 2)]))
    else:
        new_hex = hex
    return int(new_hex, 16)


class WavHeader():
    ChunkID: str = None
    ChunkSize: int = None
    Format: str = None
    Subchunk1ID: str = None
    Subchunk1Size: int = None
    AudioFormat: int = None
    NumChannels: int = None
    SampleRate: int = None
    ByteRate: int = None
    BlockAlign: int = None
    BitsPerSample: int = None
    Subchunk2ID: str = None
    Subchunk2Size: int = None

    @staticmethod
    def parseFromFile(filePath: str) -> 'WavHeader':
        header = WavHeader()
        with open(filePath, 'rb') as f:
            header.ChunkID = f.read(4)
            header.ChunkSize = hex2dec(binascii.hexlify(f.read(4)))
            header.Format = f.read(4)
            header.Subchunk1ID = f.read(4)
            header.Subchunk1Size = hex2dec(binascii.hexlify(f.read(4)))
            header.AudioFormat = hex2dec(binascii.hexlify(f.read(2)))
            header.NumChannels = hex2dec(binascii.hexlify(f.read(2)))
            header.SampleRate = hex2dec(binascii.hexlify(f.read(4)))
            header.ByteRate = hex2dec(binascii.hexlify(f.read(4)))
            header.BlockAlign = hex2dec(binascii.hexlify(f.read(2)))
            header.BitsPerSample = hex2dec(binascii.hexlify(f.read(2)))
            header.Subchunk2ID = f.read(4)
            header.Subchunk2Size = hex2dec(binascii.hexlify(f.read(4)))
        return header

class WavWriter(threading.Thread):
    _position = 0
    _positionChanged = []
    _stateChanged = []
    _playState : PlayState = None
    def __init__(self):
        super().__init__()
        self._playState = PlayState.stop
        self.stateLock = threading.Lock()
        self.cond = threading.Condition(self.stateLock)
        self.streamLock = threading.Lock()
        self.stream = None
        self.positionLock = threading.Lock()
        self._positionChanged = []
        self._stateChanged = []
    
    def setVolume(self, volume):
        winmm.waveOutSetVolume(self.hwaveout, int(volume * 0xFFFF) + (int(volume * 0xFFFF) << 16))
    
    @property
    def position(self) -> int:
        self.positionLock.acquire()
        position = self._position
        self.positionLock.release()
        return position
    @position.setter
    def position(self, position: int) -> None:
        self.positionLock.acquire()
        self._position = position
        self.positionLock.release()
        for func in self._positionChanged:
            func(position)
    
    @property
    def playState(self) -> PlayState:
        self.stateLock.acquire()
        playState = self._playState
        self.stateLock.release()
        return playState

    def addPositionChangedCallBack(self, func) -> None:
        self._positionChanged.append(func)
    
    def addStateChangedCallBack(self, func) -> None:
        self._stateChanged.append(func)
    

    def open(self, filePath):
        self.position = 0
        self.filePath = filePath
        self.wavHeader = WavHeader.parseFromFile(filePath)
        self.hwaveout = ctypes.c_void_p()
        self.buffSize = self.wavHeader.SampleRate * 2
        self.byteRate = self.wavHeader.ByteRate
        self.wavefx = WAVEFORMATEX(
            WAVE_FORMAT_PCM,
            self.wavHeader.NumChannels,     # nChannels
            self.wavHeader.SampleRate,  # SamplesPerSec
            # AvgBytesPerSec = 44100 *4, SamplesPerSec * one sample bytes(2*2=4)
            self.wavHeader.ByteRate,
            # nBlockAlign = 2 nChannels * 16 wBitsPerSample / 8 bits per byte
            self.wavHeader.BlockAlign,
            self.wavHeader.BitsPerSample,    # wBitsPerSample
            0
        )
        pwfx = ctypes.pointer(self.wavefx)
        ret = winmm.waveOutOpen(
            # buffer to receive a handle identifying
            ctypes.byref(self.hwaveout),
            # the open waveform-audio output device
            WAVE_MAPPER,            # constant to point to default wave device
            # identifier for data format sent for device
            pwfx,
            0,  # DWORD_PTR dwCallback - callback function
            0,  # DWORD_PTR dwCallbackInstance - user instance data for callback
            0  # DWORD fdwOpen - flag for opening the device
        )
        if ret != MMSYSERR_NOERROR:
            print('Error opening default waveform audio device (WAVE_MAPPER)')
            #sys.exit('Error opening default waveform audio device (WAVE_MAPPER)')
        self.playing()

    def isPlaying(self):
        return self.playState == PlayState.playing
    
    def setPosition(self, position: int):
        self.streamLock.acquire()
        new_position = position
        try:
            if self.stream.readable():
                self.stream.seek(WAV_HEADER_SIZE + self.byteRate * (new_position // 1000), 0)
        except Exception as e:
            print(e)
        self.streamLock.release()
        self.position = new_position

    def isPause(self):
        return self.playState == PlayState.pause

    def resume(self):
        self.cond.acquire()
        self._playState = PlayState.playing
        self.cond.notify()
        self.cond.release()
        for func in self._stateChanged:
            func(self._playState)
    
    # force kill
    def kill(self):
        self.cond.acquire()
        self._playState = PlayState.kill
        self.cond.notify()
        self.cond.release()
    
    def stop(self):
        self.cond.acquire()
        self._playState = PlayState.stop
        self.cond.notify()
        self.cond.release()
        for func in self._stateChanged:
            func(self._playState)

    def pause(self):
        self.cond.acquire()
        self._playState = PlayState.pause
        self.cond.notify()
        self.cond.release()
        for func in self._stateChanged:
            func(self._playState)
    
    def playing(self):
        self.cond.acquire()
        self._playState = PlayState.playing
        self.cond.notify()
        self.cond.release()
        for func in self._stateChanged:
            func(self._playState)
    
    def _sendBlock(self, data, header : WAVEHDR):
        header.dwBufferLength = len(data)
        header.lpData = data
        header.dwFlags = 0
        pwh = ctypes.pointer(header)
        if winmm.waveOutPrepareHeader(
             self.hwaveout, pwh, ctypes.sizeof(WAVEHDR)
           ) != MMSYSERR_NOERROR:
           print('Error: waveOutPrepareHeader failed')
           #sys.exit('Error: waveOutPrepareHeader failed')

        err = winmm.waveOutWrite(
             self.hwaveout, ctypes.byref(header), ctypes.sizeof(header)
           ) 
        if err != MMSYSERR_NOERROR:
          print('Error: wavOutWrite failed')
          #sys.exit('Error: waveOutWrite failed')

    def run(self):
        try:
            self.streamLock.acquire()
            self.stream = open(self.filePath, 'rb')
            self.stream.seek(WAV_HEADER_SIZE + self.byteRate * (self.position // 1000), 0)
            self.streamLock.release()

            # more buffer for good play
            wavehdrs = [WAVEHDR(), WAVEHDR()]
            curblock = 0
            readlen = 0
            while True:
                self.cond.acquire()
                while self._playState == PlayState.pause:
                    self.cond.wait()
                playState = self._playState
                self.cond.release()
                if playState != PlayState.playing:
                    break
                freeids = [x for x in range(len(wavehdrs))
                           if wavehdrs[x].dwFlags in (0, WHDR_DONE)]
                readlen = 0
                totalread = 0
                for i in freeids:
                    self.streamLock.acquire()
                    data = self.stream.read(self.buffSize)
                    self.streamLock.release()
                    readlen = len(data)
                    if readlen == 0:
                        break
                    self._sendBlock(data, wavehdrs[i]) 
                    totalread += readlen
                    self.position = self.position + readlen * 1000 // self.byteRate
                if readlen == 0:
                    break

                # 大约0.25s
                waitTime = totalread/float(self.byteRate) - 0.01
                waitTime = max(0.1, waitTime)
                time.sleep(waitTime)
                while True:
                    ret = winmm.waveOutUnprepareHeader(
                                    self.hwaveout,
                                    ctypes.byref(wavehdrs[curblock]),
                                    ctypes.sizeof(wavehdrs[curblock])
                                )
                    if ret == WAVERR_STILLPLAYING:
                        time.sleep(0.01)
                        continue
                    if ret != MMSYSERR_NOERROR:
                        print('Error: waveOutUnprepareHeader failed with code 0x%x' % ret)
                        #sys.exit('Error: waveOutUnprepareHeader failed with code 0x%x' % ret)
                    break
                curblock = (curblock + 1) % len(wavehdrs)
            self.position = 0
            self.streamLock.acquire()
            self.stream.close()
            self.streamLock.release()
            for cur in range(len(wavehdrs)):
                while True:
                    ret = winmm.waveOutUnprepareHeader(
                                    self.hwaveout,
                                    ctypes.byref(wavehdrs[curblock]),
                                    ctypes.sizeof(wavehdrs[curblock])
                                )
                    if ret == WAVERR_STILLPLAYING:
                        time.sleep(0.01)
                        continue
                    break
            winmm.waveOutClose(self.hwaveout)
            # 强制退出的时候不用发statechanged信号。只有readlen为0才表示自然停止
            if readlen == 0:
                self.stop()
        except Exception as e:
            print (e)


if __name__ == '__main__':
    for i in range(2):
        wav = WavWriter()
        wav.open("D:\dev\song\思想犯 - ヨルシカ.wav")
        wav.setVolume(0.5)
        wav.start()
        wav.kill()
    #wav.join()
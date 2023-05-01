from .AppWidget import AppWidget, AppWidgetHintClass
from .AppSlider import AppSlider
from .AppTextLabel import AppTextLabel
from .AppLayoutBox import AppLayoutBox
from pyqt5Custom import ImageBox
from typing import Union, Literal
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
#from PySide2.QtMultimedia import QMediaPlayer
from Core.Media.EXPlayer import EXPlayer
from PySide2.QtCore import QEvent, Qt
from functools import partial
from Core import appManager, AutoTranslateWord, musicPlayerManager
from PySide2.QtCore import Signal ############################

musicBoxHint = Union[QWidget, AppWidgetHintClass,'AppMusicBox']
class AppMusicBox(AppWidget(QWidget)):
    music_info_signal = Signal(str, int)################################
    def __init__(self:musicBoxHint, mediaPlayer:EXPlayer, *args, height=150, **kwargs):
        super().__init__(*args, height=height, **kwargs)
        self.mediaPlayer = mediaPlayer
        self.hLyaout = QHBoxLayout(self)
        self.hLyaout.setContentsMargins(5, 5, 5, 5)
        self.hLyaout.setSpacing(5)
        self.iconLabel = ImageBox(appManager.getUIImagePath('CD.png'))
        self.iconLabel.setMaximumHeight(int(self.size().height() * 0.9))
        self.SetIcon = self.iconLabel.setSource
        self.hLyaout.addWidget(self.iconLabel)

        self.vLayout = QVBoxLayout()
        self.vaLayoutWidget = QWidget()
        self.vaLayoutWidget.setLayout(self.vLayout)
        self.vLayout.setContentsMargins(0, 0, 0, 0)
        self.vLayout.setSpacing(0)
        self.hLyaout.addWidget(self.vaLayoutWidget, stretch=1)

        #info bar
        self.titleLabel = AppTextLabel(text='', fontSize=15, fontBold=True)
        self.title = self.titleLabel.text
        self.SetTitle = self.titleLabel.SetText

        self.artistLabel = AppTextLabel(text='', fontSize=13)
        self.artist = self.artistLabel.text
        self.SetArtist = self.artistLabel.SetText

        self.infoBar = AppLayoutBox(direction='Horizontal',borderCornerRadius=0)
        self.infoBar.addWidget(self.titleLabel, stretch=1)
        self.infoBar.addWidget(self.artistLabel, stretch=0)
        self.vLayout.addWidget(self.infoBar)


        #button bar
        self.buttonBar = AppLayoutBox(direction='Horizontal',borderCornerRadius=0)
        self.soundButton = self.buttonBar.addButton(None, appManager.getUIImagePath('sound3.png'), None)
        def onSoundButtonClicked():
            def eventFilter(self, obj, event):
                if event.type() == QEvent.Type.MouseButtonPress:
                    if event.button() == Qt.LeftButton and not self.geometry().contains(event.globalPos()):
                        self.hide()
                        self.deleteLater()
                return False
            box = AppLayoutBox(parent=self)
            setattr(box, 'eventFilter', partial(eventFilter, box))
            self.appWindow.installEventFilter(box)
            box.layout.setContentsMargins(30, 0, 30, 0)
            box.layout.setSpacing(20)
            box.addText(AutoTranslateWord('Volume'))
            slider = AppSlider(parent=box, direction='Horizontal', minimum=0, maximum=100)
            slider.setValue(self.mediaPlayer.volume)
            slider.valueChanged.connect(self.mediaPlayer.setVolume)
            def changVolumnIcon(value):
                if value==0:
                    self.soundButton.setIcon(appManager.getUIImagePath('sound0.png'))
                elif value<30:
                    self.soundButton.setIcon(appManager.getUIImagePath('sound1.png'))
                elif value<70:
                    self.soundButton.setIcon(appManager.getUIImagePath('sound2.png'))
                else:
                    self.soundButton.setIcon(appManager.getUIImagePath('sound3.png'))
            slider.valueChanged.connect(changVolumnIcon)
            box.addWidget(slider)
            valueLabel = box.addText(str(self.mediaPlayer.volume))
            slider.valueChanged.connect(lambda value: valueLabel.setText(str(value)))
            box.adjustSize()
            box.show()
            box.raise_()
            box.move(self.soundButton.pos())
        self.soundButton.clicked.connect(onSoundButtonClicked)
        self.playModeButton = self.buttonBar.addButton(None, appManager.getUIImagePath('random.png'), None)
        playModes = ['listLoop', 'random', 'loop']
        if hasattr(self.mediaPlayer, 'playMode'):
            self.playModeButton.clicked.connect(
                lambda: self.SetPlayMode(playModes[(playModes.index(self.mediaPlayer.playMode) + 1) % len(playModes)]))
        self.prevSongButton = self.buttonBar.addButton(None, appManager.getUIImagePath('prevSong.png'), None)
        self.prevSongButton.clicked.connect(self.mediaPlayer.goPreviousMusic) if hasattr(self.mediaPlayer, 'goPreviousMusic') else None
        self.playButton = self.buttonBar.addButton(None, appManager.getUIImagePath('stop.png'), None)
        self.playButton.clicked.connect( lambda: musicPlayerManager.play() if not musicPlayerManager.isPlaying() else musicPlayerManager.pause())
        self.nextSongButton = self.buttonBar.addButton(None, appManager.getUIImagePath('nextSong.png'), None)
        self.nextSongButton.clicked.connect(self.mediaPlayer.goNextMusic) if hasattr(self.mediaPlayer, 'goNextMusic') else None
        self.smallMenuButton = self.buttonBar.addButton(None, appManager.getUIImagePath('3bar.png'), None)
        self.vLayout.addWidget(self.buttonBar)

        #progress bar
        self.progressSlider = AppSlider(parent=self, direction='Horizontal', backgroundColor=self.furthurBackgroundColor, minimum=0, maximum=0)
        self.currentTimeText = AppTextLabel(text='00:00', fontSize=10)
        self.progressSlider.valueChanged.connect(lambda value: self.currentTimeText.SetText(f'{int(value// 60):02d}:{int(value % 60):02d}'))
        ## 拉动进度条时把音频也跳到对应位置
        self.progressSlider.sliderReleased.connect(lambda : self.mediaPlayer.setPosition(self.progressSlider.value() * 1000))
        #self.progressSlider.sliderMoved.connect(lambda : self.mediaPlayer.setPosition(self.progressSlider.value() * 1000))
        self.progressSlider.jumpPress.connect(lambda : self.mediaPlayer.setPosition(self.progressSlider.value() * 1000))
        self.progressBar = AppLayoutBox(direction='Horizontal',borderCornerRadius=0)
        self.progressBar.addWidget(self.currentTimeText, stretch=0)
        self.progressBar.addWidget(self.progressSlider, stretch=1)
        self.vLayout.addWidget(self.progressBar)

        #if hasattr(self.mediaPlayer, 'currentMusic') and
        if hasattr(self.mediaPlayer, 'addOnMusicChanged'):
            def onMusicChanged(music):
                self.progressSlider.setMaximum(music.duration)
                self.SetTitle(music.title or AutoTranslateWord('Unknown'))
                artistText = (music.artist or music.albumArtist) or AutoTranslateWord('Unknown')
                self.SetArtist(artistText)
                self.SetIcon(music.coverPath) if music.coverPath else None
            self.mediaPlayer.addOnMusicChanged(onMusicChanged)

        def onPlayModeChanged(mode:Literal['listLoop', 'random', 'loop']):
            if mode == 'loop':
                self.playModeButton.setIcon(appManager.getUIImagePath('loop.png'))
            elif mode == 'listLoop':
                self.playModeButton.setIcon(appManager.getUIImagePath('double_right_arrow.png'))
            elif mode == 'random':
                self.playModeButton.setIcon(appManager.getUIImagePath('random.png'))
        if hasattr(self.mediaPlayer, 'addOnPlayModeChanged'):
            self.mediaPlayer.addOnPlayModeChanged(onPlayModeChanged)
        onPlayModeChanged(self.mediaPlayer.playMode)

        def onPlayStateChanged(state:EXPlayer.State):
            #if state == EXPlayer.State.PlayingState:
            if self.mediaPlayer.isPlaying():
                self.playButton.setIcon(appManager.getUIImagePath('play.png'))
            else:
                self.playButton.setIcon(appManager.getUIImagePath('stop.png'))
        self.mediaPlayer.stateChanged.connect(onPlayStateChanged)

        def onPositionChanged(position:int):
            sec = int(position / 1000)
            self.progressSlider.setValue(sec)
            #########################################################################################
            if hasattr(self.mediaPlayer, 'currentMusic'):
                title = self.mediaPlayer.currentMusic.title or AutoTranslateWord('Unknown')
                self.music_info_signal.emit(title, sec)
                #####################################################################################
        self.mediaPlayer.positionChanged.connect(onPositionChanged)

        def onPlayerCleared():
            self.progressSlider.setMaximum(0)
            self.progressSlider.setValue(0)
            self.SetTitle("")
            self.SetArtist("")
            self.SetIcon(appManager.getUIImagePath('CD.png'))
        if hasattr(self.mediaPlayer, 'addOnClearCallback'):
            self.mediaPlayer.addOnClearCallback(onPlayerCleared)

        if hasattr(self.mediaPlayer,'currentMusic') and self.mediaPlayer.currentMusic is not None:
            self.progressSlider.setMaximum(self.mediaPlayer.currentMusic.duration)
            self.progressSlider.setValue(int(appManager.record.lastSongTime.value / 1000))
            self.SetTitle(self.mediaPlayer.currentMusic.title or AutoTranslateWord('Unknown'))
            artistText = self.mediaPlayer.currentMusic.artist or self.mediaPlayer.currentMusic.albumArtist
            self.SetArtist(artistText) if artistText else AutoTranslateWord('Unknown')
            self.SetIcon(self.mediaPlayer.currentMusic.coverPath) if self.mediaPlayer.currentMusic.coverPath else None

    def SetArtist(self, artist:str) -> None:
        self.artistLabel.SetText(artist)
    def SetTitle(self, title:str) -> None:
        self.titleLabel.SetText(title)
    def SetIcon(self, iconPath:str) -> None:
        self.iconLabel.setSource(iconPath)
    def SetPlayMode(self, mode:Literal['listLoop','random','loop']) -> None:
        if hasattr(self.mediaPlayer, 'playMode'):
            if mode == "listLoop":
                self.playModeButton.setIcon(appManager.getUIImagePath('double_right_arrow.png'))
            elif mode == "random":
                self.playModeButton.setIcon(appManager.getUIImagePath('random.png'))
            elif mode == "loop":
                self.playModeButton.setIcon(appManager.getUIImagePath('loop.png'))
            self.mediaPlayer.playMode = mode


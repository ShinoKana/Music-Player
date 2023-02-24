from .AppWidget import AppWidget, AppWidgetHintClass
from .AppSlider import AppSlider
from .AppTextLabel import AppTextLabel
from .AppLayoutBox import AppLayoutBox
from pyqt5Custom import ImageBox
from typing import Union
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from Core import appManager

musicBoxHint = Union[QWidget, AppWidgetHintClass]
class AppMusicBox(AppWidget(QWidget)):
    def __init__(self:musicBoxHint, *args, height=150, **kwargs):
        super().__init__(*args, height=height, **kwargs)
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
        self.titleLabel = AppTextLabel(text='----', fontSize=12)
        self.title = self.titleLabel.text
        self.SetTitle = self.titleLabel.SetText

        self.artistLabel = AppTextLabel(text='', fontSize=10)
        self.artist = self.artistLabel.text
        self.SetArtist = self.artistLabel.SetText

        self.infoBar = AppLayoutBox(direction='Horizontal',borderCornerRadius=0)
        self.infoBar.addWidget(self.titleLabel, stretch=1)
        self.infoBar.addWidget(self.artistLabel, stretch=0)
        self.vLayout.addWidget(self.infoBar)

        #button bar
        self.buttonBar = AppLayoutBox(direction='Horizontal',borderCornerRadius=0)
        self.soundButton = self.buttonBar.addButton(None, appManager.getUIImagePath('sound3.png'), None)
        self.playModeButton = self.buttonBar.addButton(None, appManager.getUIImagePath('random.png'), None)
        self.prevSongButton = self.buttonBar.addButton(None, appManager.getUIImagePath('prevSong.png'), None)
        self.playButton = self.buttonBar.addButton(None, appManager.getUIImagePath('stop.png'), None)
        self.nextSongButton = self.buttonBar.addButton(None, appManager.getUIImagePath('nextSong.png'), None)
        self.smallMenuButton = self.buttonBar.addButton(None, appManager.getUIImagePath('3bar.png'), None)
        self.vLayout.addWidget(self.buttonBar)

        #progress bar
        self.progressSlider = AppSlider(direction='Horizontal')
        self.currentTimeText = AppTextLabel(text='00:00', fontSize=10)
        self.progressSlider.valueChanged.connect(lambda value: self.currentTimeText.SetText(str(value)))
        self.progressBar = AppLayoutBox(direction='Horizontal',borderCornerRadius=0)
        self.progressBar.addWidget(self.currentTimeText, stretch=0)
        self.progressBar.addWidget(self.progressSlider, stretch=1)
        self.vLayout.addWidget(self.progressBar)





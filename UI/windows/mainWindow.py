from PySide2.QtCore import QPropertyAnimation, QSize, QEasingCurve, QVariantAnimation
from PySide2.QtWidgets import QVBoxLayout, QWidget

from Core.DataType import AutoTranslateWord
from Core.Managers import appManager

from .AppWindow import AppWindow
from pages import SettingPage, HomePage, PlayerPage, SongListPage
from components import AppMusicBox, AppButton

class MainWindow(AppWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, title=AutoTranslateWord('(22-23CUHK) CSCI3280 Group Project - Music Player'), windowSize=(1500, 900), navBarRatio=1/11,**kwargs)
        self.__VERSION = '1.0.0'
        self.__isHiding = False
        #music box
        self.musicBox = AppMusicBox(borderCornerRadius=0, backgroundColor=appManager.config.currentComponentColor_DarkerOrLighter())
        self.musicBox.setMaximumHeight(150)
        self.hideWindowButton = AppButton(parent=self, icon= appManager.getUIImagePath('miniToTray.png'),
                                          command=self.hideOrShowMainWindow, backgroundColor=appManager.config.currentComponentColor_DarkerOrLighter())
        self.hideWindowButton.setFixedSize(QSize(self.musicBox.infoBar.height(), self.musicBox.infoBar.height()))
        self.musicBox.infoBar.addWidget(self.hideWindowButton, stretch=0)

        #add music box at the bottom
        self.mainLayout.removeWidget(self.pageStackWidget)
        self.rightSide = QVBoxLayout()
        self.rightSide.setContentsMargins(0, 0, 0, 0)
        self.rightSide.setSpacing(0)
        self.rightSide.addWidget(self.pageStackWidget, stretch=1)
        self.rightSide.addWidget(self.musicBox)

        self.rightSideWidget = QWidget()
        self.rightSideWidget.setLayout(self.rightSide)
        self.mainLayout.addWidget(self.rightSideWidget)

        #pageStackWidget
        self.settingPage = self.addPage(SettingPage)
        self.homePage = self.addPage(HomePage)
        self.playerPage = self.addPage(PlayerPage)
        self.songListPage = self.addPage(SongListPage)

        #navigation bar
        self.addNavBarSwitchPageButton(AutoTranslateWord("Home"), appManager.getUIImagePath("home.png"), self.homePage)
        self.addNavBarSwitchPageButton(AutoTranslateWord("Player"), appManager.getUIImagePath("play.png"), self.playerPage)
        self.addNavBarSwitchPageButton(AutoTranslateWord("SongList"), appManager.getUIImagePath("dots_horizon.png"), self.songListPage)
        self.addNavBarSwitchPageButton(AutoTranslateWord("Setting"), appManager.getUIImagePath("gear.png"), self.settingPage)

        self.switchPage(self.homePage)

        # region start animation
        self.openAni_size = QPropertyAnimation(self, b'size')
        self.openAni_size.setDuration(700)
        self.openAni_size.setStartValue(QSize(0, self.DEFALUT_WINDOW_SIZE[1]))
        self.openAni_size.setEndValue(QSize(*self.DEFALUT_WINDOW_SIZE))
        self.openAni_size.setEasingCurve(QEasingCurve.OutBack)

        self.openAni_opacity = QPropertyAnimation(self, b'windowOpacity')
        self.openAni_opacity.setDuration(700)
        self.openAni_opacity.setStartValue(0)
        self.openAni_opacity.setEndValue(1)
        self.openAni_opacity.setEasingCurve(QEasingCurve.Linear)

        self.setWindowOpacity(0)
        self.openAni_size.start()
        self.openAni_opacity.start()
        # endregion
    @property
    def VERSION(self):
        return self.__VERSION
    def allowMultiplePageInstances(cls):
        return False
    def hideOrShowMainWindow(self):
        if not self.__isHiding:
            self.hideNavBar()
            self.naviBarHideButton.hide()
            self.titleBar.hide()
            #hide page
            animation_main = QVariantAnimation(self)
            animation_main.setDuration(200)
            animation_main.setStartValue(self.height())
            animation_main.setEndValue(self.musicBox.height())
            animation_main.valueChanged.connect(lambda value: self.setMaximumHeight(value))

            animation_page = QVariantAnimation(self.pageStackWidget)
            animation_page.setDuration(200)
            animation_page.setStartValue(self.pageStackWidget.height())
            animation_page.setEndValue(0)
            animation_page.valueChanged.connect(lambda value: self.pageStackWidget.setMaximumHeight(value))

            animation_main.start()
            animation_page.start()

            self.__isHiding = True
        else:
            self.showNavBar()
            self.naviBarHideButton.show()
            self.titleBar.show()
            #show page
            animation_main = QVariantAnimation(self)
            animation_main.setDuration(200)
            animation_main.setStartValue(self.height())
            animation_main.setEndValue(self.DEFALUT_WINDOW_SIZE[1])
            animation_main.valueChanged.connect(lambda value: self.setMaximumHeight(value))
            animation_main.valueChanged.connect(lambda value: self.resize(self.width(), value))

            animation_page = QVariantAnimation(self.pageStackWidget)
            animation_page.setDuration(200)
            animation_page.setStartValue(self.pageStackWidget.height())
            animation_page.setEndValue(self.DEFALUT_WINDOW_SIZE[1] - self.musicBox.height())
            animation_page.valueChanged.connect(lambda value: self.pageStackWidget.setMaximumHeight(value))
            animation_page.valueChanged.connect(lambda value: self.pageStackWidget.resize(self.pageStackWidget.width(), value))

            animation_main.start()
            animation_page.start()

            self.pageStackWidget.show()
            self.__isHiding = False

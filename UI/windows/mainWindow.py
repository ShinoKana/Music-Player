from PySide2.QtCore import QPropertyAnimation, QSize, QEasingCurve, QVariantAnimation
from PySide2.QtWidgets import QVBoxLayout, QWidget
from Core.DataType import AutoTranslateWord
from Core import appManager, musicPlayerManager
from .AppWindow import AppWindow
from pages import SettingPage, HomePage, PlayerPage, SongListPage, GroupInfoPage, SongManagePage
from components import AppMusicBox, AppButton

class MainWindow(AppWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, title=AutoTranslateWord('(22-23CUHK) CSCI3280 Group Project - Music Player'), windowSize=(1500, 900),
                         navBarRatio=1/11,**kwargs)

        self.__isHiding = False
        #music box
        self.musicBox = AppMusicBox(appWindow=self, mediaPlayer=musicPlayerManager, borderCornerRadius=0, backgroundColor=appManager.config.currentComponentColor_DarkerOrLighter())
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
        self.homePage = self.addPage(HomePage)
        self.playerPage = self.addPage(PlayerPage)
        self.songListPage = self.addPage(SongListPage)
        self.songManagePage = self.addPage(SongManagePage)
        self.settingPage = self.addPage(SettingPage)
        self.groupInfoPage = self.addPage(GroupInfoPage)

        #navigation bar
        self.addNavBarSwitchPageButton(AutoTranslateWord("Home"), appManager.getUIImagePath("home.png"), self.homePage)
        self.addNavBarSwitchPageButton(AutoTranslateWord("Player"), appManager.getUIImagePath("stop.png"), self.playerPage)
        self.addNavBarSwitchPageButton(AutoTranslateWord("Play List"), appManager.getUIImagePath("3bar.png"), self.songListPage)
        self.addNavBarSwitchPageButton(AutoTranslateWord("Song Manage"), appManager.getUIImagePath("music.png"), self.songManagePage)
        self.addNavBarSwitchPageButton(AutoTranslateWord("Setting"), appManager.getUIImagePath("gear.png"), self.settingPage)
        self.addNavBarSwitchPageButton(AutoTranslateWord("GroupInfo"), appManager.getUIImagePath("user.png"), self.groupInfoPage)

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

        def setMainWindow():
            appManager.mainWindow = self
        self.openAni_opacity.finished.connect(setMainWindow)

    def paintEvent(self, e) -> None:
        super().paintEvent(e)
        if appManager.mainWindow == self:
            if len(appManager._toastMessages)>0:
                args = appManager._toastMessages.pop(0)
                self.toast(*args)
            if len(appManager._loadingMessages) > 0:
                args = appManager._loadingMessages.pop(0)
                self.goloading(*args)
            if appManager._stopLoading:
                self.stoploading()
                appManager._stopLoading = False

    def allowMultiplePageInstances(cls):
        return False
    def hideOrShowMainWindow(self):
        if not self.__isHiding:
            self.hideNavBar()
            self.naviBarHideButton.hide()

            animation_main = QVariantAnimation(self)
            animation_main.setDuration(220)
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

            animation_main = QVariantAnimation(self)
            animation_main.setDuration(220)
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

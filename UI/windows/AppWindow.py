from typing import Union, List
from abc import abstractmethod
from PySide2.QtWidgets import QHBoxLayout, QApplication, QStackedWidget, QWidget, QVBoxLayout
from PySide2.QtGui import QColor, QIcon, QPixmap, QResizeEvent, QCloseEvent
from PySide2.QtCore import QVariantAnimation, Signal

from Core.DataType import AutoTranslateWord
from Core import appManager

from ExternalPackage import ToastToolTip
from ExternalPackage.qframelesswindow import FramelessWindow
from ExternalPackage.pyqt5Custom import Toast, Spinner
from components import AppTitleBar, AppNavigationBar, AppButton
from pages.AppPage import AppPage

class AppWindow(FramelessWindow):
    _instance = None
    _hasInit = False
    onPageChanged = Signal(AppPage)
    def __new__(cls, *args, **kwargs):
        if cls.allowMultiplePageInstances(cls):
            originInit = cls.__init__
            def newInit(self, *args, **kwargs):
                originInit(self, *args, **kwargs)
                try:
                    self.naviBarHideButton.raise_()
                except:
                    pass
                self.titleBar.raise_()
            return super().__new__(cls)
        else:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                originalInit = cls.__init__
                def newInit(self, *args, **kwargs):
                    if not cls._hasInit:
                        originalInit(self, *args, **kwargs)
                        cls._hasInit = True
                        try:
                            self.naviBarHideButton.raise_()
                        except:
                            pass
                        self.titleBar.raise_()
                    else:
                        cls._instance.raise_()
                        self.titleBar.raise_()
                cls.__init__ = newInit
            return cls._instance
    def __init__(self, QApp: QApplication, parentWindow:'AppWindow'=None, title:str="", iconPath:str= appManager.getUIImagePath("square_logo.png"),
                 windowSize:tuple=(1600, 900), navBarRatio:float=1/11, needNavBar:bool=True, needTopNavBar:bool=False):
        super().__init__(parent=None)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor('transparent'))
        self.setPalette(palette)

        self.__QApp = QApp
        self.__parentWindow = None
        if parentWindow is not None:
            self.parentWindow = parentWindow
        self.childWindows:List['AppWindow'] = []
        self.__title = title
        self.__iconPath = iconPath

        self.__DEFAULT_WINDOW_SIZE = windowSize
        self.__NavBarAndPageRatio = navBarRatio

        #title bar
        self.setTitleBar(AppTitleBar(parent=self, titleText=title, iconPath=iconPath))

        #loadingBox
        self.loadingSpinner = Spinner(3, QColor('white'))
        self.loadingToastBox = Toast(parent=self.window(), text="", icon=self.loadingSpinner)
        self.loadingToastBox.close_btn.clicked.disconnect(self.loadingToastBox.fall)
        self.loadingToastBox.close_btn.clicked.connect(self.stoploading)
        self.loadingToastBox.setMinimumWidth(160)
        self.__isloading = False
        self.__loadingText = ""

        #size
        self.resize(*self.__DEFAULT_WINDOW_SIZE)
        desktop = QApplication.primaryScreen().availableSize()
        desktopWidth, desktopHeight = desktop.width(), desktop.height()
        self.move(desktopWidth // 2 - self.width() // 2, desktopHeight // 2 - self.height() // 2) #put to center of screen

        self.mainLayout = QHBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        #pageStackWidget
        self.pages = []
        self.pageStackWidget = QStackedWidget(self)
        self.pageStackWidget.setContentsMargins(0, 0, 0, 0)

        #navigation bar
        if needNavBar:
            self.navigationBar = AppNavigationBar(width=self.NavBar_DEFAULT_SIZE[0], borderCornerRadius=0, fontBold=True)
            if not needTopNavBar:
                self.navigationBar.navigationBar.setContentsMargins(7, 25, 7, 18)
            else:
                self.navigationBar.navigationBar.setContentsMargins(5, 4, 5, 4)
            self.naviBarHideButton = AppButton(parent=self, icon=appManager.getUIImagePath('left_arrow.png'), borderCornerRadius=8)
            self.naviBarHideButton.thisStyleDict['default']['radius-corners'] = (False, True, False, True)
            self.naviBarHideButton.setFixedSize(20, 100)
            self.naviBarHideButton.move(self.navigationBar.width(), (self.DEFALUT_WINDOW_SIZE[1]-self.naviBarHideButton.height())//2)
            self.naviBarHideButton.clicked.connect(self.hideNavBar)
            self.naviBarHideButton.show()
        else:
            def noNavBarError():
                raise NotImplementedError("This window doesn't have a navigation bar")
            self.addNavBarIcon = noNavBarError
            self.addNaviBarButton = noNavBarError
            self.hideNavBar = noNavBarError
            self.showNavBar = noNavBarError
        if not needTopNavBar:
            def noTopNavBarError():
                raise NotImplementedError("This window doesn't have a top navigation bar")
            self.addTopNavBarButton = noTopNavBarError

        self.mainLayout.addWidget(self.navigationBar) if needNavBar else None
        self.mainLayout.addWidget(self.pageStackWidget)

        if needTopNavBar:
            self.titleBar.SetBackgroundColor(appManager.config.currentComponentColor())
            self.titleBar.SetMargin(0, 2, 0, 0)
            self.VLayout = QVBoxLayout(self)
            self.VLayout.setContentsMargins(0, 0, 0, 0)
            self.VLayout.setSpacing(0)
            self.mainLayoutWidget = QWidget(self)
            self.mainLayoutWidget.setLayout(self.mainLayout)
            self.VLayout.addWidget(self.titleBar, stretch=0)
            self.VLayout.addWidget(self.mainLayoutWidget, stretch=1)

        self.setLayout(self.mainLayout)
        self.currentPage = None
        self.naviBarHideButton.raise_() if needNavBar else None

    def __del__(self):
        if self._instance == self:
            self._instance = None
            self._hasInit = False
        super().__del__()
    @classmethod
    @abstractmethod
    def allowMultiplePageInstances(cls):
        return False  # default is False

    #region property
    @property
    def QApp(self):
        return self.__QApp
    @property
    def parentWindow(self):
        return self.__parentWindow
    @parentWindow.setter
    def parentWindow(self, value):
        if value == self.__parentWindow:
            return
        if self.__parentWindow is not None:
            self.__parentWindow.childWindows.remove(self)
        self.__parentWindow = value
        if self.__parentWindow is not None:
            self.__parentWindow.childWindows.append(self)
    @property
    def title(self):
        return self.__title
    @title.setter
    def title(self, value):
        self.SetTitle(value)
    def SetTitle(self, value):
        self.__title = value
        self.window().setWindowTitle(value)
    @property
    def iconPath(self):
        return self.__iconPath
    @iconPath.setter
    def iconPath(self, value):
        self.SetIcon(value)
    def SetIcon(self, value):
        self.titleBar.SetIcon(value)
    @property
    def DEFALUT_WINDOW_SIZE(self):
        return self.__DEFAULT_WINDOW_SIZE
    @property
    def NavBarAndPageRatio(self)->float:
        return self.__NavBarAndPageRatio
    @property
    def APP_PAGE_DEFAULT_SIZE(self)->tuple:
        return (int(self.DEFALUT_WINDOW_SIZE[0] * (1 - self.NavBarAndPageRatio)), self.DEFALUT_WINDOW_SIZE[1])
    @property
    def NavBar_DEFAULT_SIZE(self)->tuple:
        return (int(self.DEFALUT_WINDOW_SIZE[0] * self.NavBarAndPageRatio), self.DEFALUT_WINDOW_SIZE[1])
    #endregion

    #region page
    def addPage(self, page: Union[AppPage, type], *args, **kwargs) -> AppPage:
        if page in self.pages:
            return page
        if isinstance(page, type) and issubclass(page, AppPage):
            _page = page(self, self.pageStackWidget, *args, **kwargs)
        else:
            _page = page
        if _page.parent() != self.pageStackWidget:
            _page.setParent(self.pageStackWidget)
        self.pageStackWidget.addWidget(_page)
        self.pages.append(_page)
        return _page
    def switchPage(self, page: AppPage):
        if page == self.currentPage:
            return
        if self.currentPage is not None:
            self.currentPage.onSwitchOut()
        self.currentPage = page
        self.pageStackWidget.setCurrentWidget(page)
        page.onSwitchIn()
        self.onPageChanged.emit(page)
    def getPage(self, index:int):
        if index < 0 or index >= self.pageStackWidget.count():
            return None
        return self.pageStackWidget.widget(index)
    #endregion

    #region navbar & top bar
    def addNavBarIcon(self, iconPath):
        self.navigationBar.addIcon(iconPath)
    def addNavBarButton(self, text:str, iconPath:str, callback:callable):
        self.navigationBar.addButton(text, iconPath, callback)
    def addNavBarSwitchPageButton(self, text:str, iconPath:str, page:AppPage):
        button = self.navigationBar.addButton(text, iconPath, lambda: self.switchPage(page))
        col = appManager.config.currentComponentColor_DarkerOrLighter()
        originCol = button.backgroundColor
        def changeButtonColor(*args):
            button.SetBackgroundColor(col) if self.currentPage == page else button.SetBackgroundColor(originCol)
            button.update()
        self.onPageChanged.connect(changeButtonColor)
    def hideNavBar(self):
        animation = QVariantAnimation(self.navigationBar)
        animation.setStartValue(self.navigationBar.width())
        animation.setEndValue(0)
        animation.setDuration(150)
        animation.valueChanged.connect(lambda value: self.navigationBar.setFixedWidth(value))
        animation.valueChanged.connect(lambda value: self.naviBarHideButton.move(value, (self.height()-self.naviBarHideButton.height())//2))
        animation.finished.connect(lambda: self.naviBarHideButton.setIcon(appManager.getUIImagePath('right_arrow.png')))
        animation.finished.connect(lambda: self.naviBarHideButton.clicked.disconnect())
        animation.finished.connect(lambda: self.naviBarHideButton.clicked.connect(self.showNavBar))
        animation.finished.connect(lambda: self.navigationBar.hide())
        animation.start()
    def showNavBar(self):
        self.navigationBar.show()
        animation = QVariantAnimation(self.navigationBar)
        animation.setStartValue(0)
        animation.setEndValue(int(self.DEFALUT_WINDOW_SIZE[0] * self.NavBarAndPageRatio))
        animation.setDuration(150)
        animation.valueChanged.connect(lambda value: self.navigationBar.setMinimumWidth(value))
        animation.valueChanged.connect(lambda value: self.naviBarHideButton.move(value, (self.height()-self.naviBarHideButton.height())//2))
        animation.finished.connect(lambda: self.naviBarHideButton.setIcon(appManager.getUIImagePath('left_arrow.png')))
        animation.finished.connect(lambda: self.naviBarHideButton.clicked.disconnect())
        animation.finished.connect(lambda: self.naviBarHideButton.clicked.connect(self.hideNavBar))
        animation.start()
    def addTopNavBarButton(self, text:str, iconPath:str, callback:callable):
        self.titleBar.addButton(text, iconPath, callback)

    #endregion

    #region toast and loading
    def toast(self, title: str="", content:str="", duration: float = 3, icon: Union[str,QIcon,QPixmap]=None):
        t = ToastToolTip(parent=self.window(), title=title, content=content, duration=duration, icon=icon)
        fontColor = 'black' if appManager.config.isLightTheme() else 'white'
        borderColor = fontColor
        t.setStyleSheet(""" 
            QWidget {
                background-color: """+ appManager.config.currentComponentColor().name() +""";
                border-radius: 10px;
                border: 2px solid """+ borderColor +""";
            }
            #titleLabel {
                color: """ + fontColor + """;
                font: 17px 'Segoe UI', 'Microsoft YaHei';
                border-radius: 0px;
                border: 0px;
            }
            #contentLabel {
                color: """ + fontColor + """;
                font: 16px 'Segoe UI', 'Microsoft YaHei';
                border-radius: 0px;
                border: none;
            }
            #closeButton {
                background-color: """+ appManager.config.currentComponentColor().darker().name() +""";
                border-radius: 5px;
                margin: 0px;
                width: 14px;
                height: 14px;
                border-images: url(:/qfluentwidgets/images/state_tool_tip/close_normal.png) top center no-repeat;
            }
            #closeButton:hover {
                background-color: """+ appManager.config.currentComponentColor().lighter().name() +""";
                border-images: url(:/qfluentwidgets/images/state_tool_tip/close_hover.png) top center no-repeat;
            }
            #closeButton:pressed {
                background-color: """+ appManager.config.currentComponentColor().lighter(150).name() +""";
                border-images: url(:/qfluentwidgets/images/state_tool_tip/close_hover.png) top center no-repeat;
            }
            #iconLabel {
                background-color: """+ appManager.config.currentComponentColor().darker().name() +""";
            }
            """)
        if content=="" or content is None:
            t.contentLabel.hide()
        t.adjustSize()
        t.show()
    def goloading(self, text=None, closable=True):
        if text is None:
            text = AutoTranslateWord("Loading...")
        if closable:
            self.loadingToastBox.close_btn.show()
        else:
            self.loadingToastBox.close_btn.hide()
        if self.__isloading:
            if self.__loadingText == text:
                return
            self.loadingToastBox.setText(text)
            self.__loadingText = text
            self.loadingToastBox.adjustSize()
            return
        else:
            self.loadingToastBox.setText(text)
            self.loadingToastBox.rise()
            self.loadingToastBox.adjustSize()
            self.__isloading = True
            self.__loadingText = text
    def stoploading(self):
        if self.__isloading:
            self.loadingToastBox.fall()
            self.__isloading = False
            self.__loadingText = ""
    #endregion

    #region event
    def resizeEvent(self, e:QResizeEvent):
        self.naviBarHideButton.move(self.navigationBar.width(), (e.size().height()-self.naviBarHideButton.height())//2)
        super().resizeEvent(e)
    def closeEvent(self, e:QCloseEvent):
        self.stoploading()
        for child in self.childWindows:
            child.close()
        super().closeEvent(e)
    #endregion

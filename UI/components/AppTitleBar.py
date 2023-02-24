from Core.Managers import appManager
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QLabel
from PySide2.QtGui import QColor, QIcon
from ExternalPackage.qframelesswindow import TitleBar, TitleBarButton
from .AppNavigationBar import AppNavigationBar
from .AppWidget import AppWidget
from .AppButton import AppButton

class AppTitleBar(AppWidget(TitleBar)):
    '''title bar of a window'''
    def __init__(self, parent, titleText=None, iconPath=None, borderCornerRadius=0, backgroundColor='transparent',**kwargs):
        super().__init__(parent=parent,borderCornerRadius=borderCornerRadius, backgroundColor=backgroundColor, **kwargs)
        self.__titleText = None
        self.__iconPath = None

        self.iconLabel = QLabel(self)
        self.iconLabel.setFixedSize(22, 22)
        self.hBoxLayout.insertSpacing(0, 10)
        self.hBoxLayout.insertWidget(1, self.iconLabel, 0, Qt.AlignLeft | Qt.AlignVCenter)
        self.window().windowIconChanged.connect(self.SetIcon)

        self.titleLabel = QLabel(self)
        self.hBoxLayout.insertWidget(2, self.titleLabel, 0, Qt.AlignLeft | Qt.AlignVCenter)
        self.titleLabel.setStyleSheet(f"""
            QLabel{{
                background: transparent;
                font: 15px 'Segoe UI';
                padding: 0 3px;
                color: {'white' if not appManager.config.isLightTheme()else 'black'}
            }}
        """)
        self.window().windowTitleChanged.connect(self.SetTitle)

        self.navigationBar = AppNavigationBar(direction='Horizontal', borderCornerRadius=0, backgroundColor='transparent')
        self.navigationBar.setFixedHeight(30)
        self.hBoxLayout.insertWidget(3, self.navigationBar, 1, Qt.AlignLeft | Qt.AlignVCenter)

        if not appManager.config.isLightTheme():
            for button in (self.findChildren(TitleBarButton)):
                button.setNormalColor(Qt.white)
                button.setHoverColor(Qt.white)
                button.setPressedColor(Qt.white)
                if button is not self.closeBtn:
                    button.setHoverBackgroundColor(QColor(255, 255, 255, 26))
                    button.setPressedBackgroundColor(QColor(255, 255, 255, 51))
        if titleText:
            parent.setWindowTitle(titleText)
            self.SetTitle(titleText)
        if iconPath:
            parent.setWindowIcon(QIcon(iconPath))
            self.SetIcon(iconPath)
    @property
    def title(self):
        return self.__titleText
    @title.setter
    def title(self, titleText):
        self.SetTitle(titleText)
    def SetTitle(self, title):
        if title == self.__titleText:
            return
        self.__titleText = title
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    @property
    def iconPath(self):
        return self.__iconPath
    @iconPath.setter
    def iconPath(self, iconPath):
        self.SetIconPath(iconPath)

    def SetIcon(self, iconPath):
        if iconPath == self.__iconPath:
            return
        if iconPath is None:
            self.iconLabel.clear()
            self.__iconPath = None
            return
        self.__iconPath = iconPath
        if isinstance(iconPath, QIcon):
            icon = iconPath
        else:
            icon = QIcon(iconPath)
        self.iconLabel.setPixmap(icon.pixmap(22, 22))

    def addButton(self, text, iconPath=None, command=None)->AppButton:
        button = self.navigationBar.addButton(text, iconPath, command)
        if button is not None:
            button.SetBorderColor(appManager.config.currentComponentColor_DarkerOrLighter())
            button.SetBorderWidth(1)
        return button
    def removeButton(self, text):
        self.navigationBar.removeButton(text)
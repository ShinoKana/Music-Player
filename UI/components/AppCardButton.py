from ExternalPackage.pyqt5Custom import StyledButton
from .AppWidget import AppWidget, AppWidgetHintClass
from .AppTextLabel import AppTextLabel
from .AppTextArea import AppTextArea
from typing import Union, Callable
from PySide2.QtWidgets import QWidget,  QVBoxLayout
from PySide2.QtGui import QIcon, QPixmap, QColor
from PySide2.QtCore import Qt
from Core import appManager

CardButtonHint = Union[AppWidgetHintClass, 'AppCardButton', StyledButton]
class AppCardButton(AppWidget(StyledButton)):
    def __init__(self:CardButtonHint, height=150, title='',titleFontSize=18, titleBold=True, titleFontColor=None,
                 text='', textFontSize=12, textBold=False, textFontColor=None, icon:Union[str, QIcon, QPixmap]=None,
                 command:Callable[[],any]=None, **kwargs):
        super().__init__(height=height, icon=icon, **kwargs)
        self.setIconSize(self.size().width(), self.size().height())

        self.conwdt.setStyleSheet("background-color:transparent;")
        self.conlyt.removeWidget(self.textLbl)

        self.vlayout = QVBoxLayout()
        self.vlayout.setContentsMargins(0,5,0,5)
        self.vlayout.setSpacing(5)
        self.vlayout.setAlignment(Qt.AlignVCenter)

        self.titleLabel = AppTextLabel(text=title, fontSize=titleFontSize, fontBold=titleBold, fontColor=titleFontColor,
                                       textAlign='center', backgroundColor='transparent')
        self.textLabel = AppTextLabel(text=text, fontSize=textFontSize, fontColor=textFontColor, textAlign='center',
                                      backgroundColor='transparent', wrap=True, fontBold=textBold)

        self.vlayout.addWidget(self.titleLabel)
        self.vlayout.addWidget(self.textLabel)
        self.vlayoutWidget = QWidget()
        self.vlayoutWidget.setLayout(self.vlayout)

        self.conlyt.addWidget(self.vlayoutWidget)
        self.conlyt.setStretch(1, 1)
        self.conlyt.setStretch(0, 0)
        self.layout.setStretch(0, 1)

        if command:
            self.addCommand(command)
        self.adjustSize()
        if self._icon is not None:
            self._icon.setFixedSize(self.size().height()*0.9, self.size().height()*0.9)
    @property
    def title(self) -> AppTextLabel:
        return self.titleLabel.text
    @title.setter
    def title(self, title:str):
        self.SetTitle(title)
    def SetTitle(self:CardButtonHint, title:str):
        self.titleLabel.text = title
    @property
    def text(self) -> AppTextArea:
        return self.textLabel.text
    @text.setter
    def text(self, text:str):
        self.textLabel.text = text
    def SetText(self:CardButtonHint, text:str):
        self.textLabel.SetText(text)
    def addCommand(self:CardButtonHint, command:Callable[[],any]):
        self.clicked.connect(command)
    def removeCommand(self:CardButtonHint, command:Callable[[],any]):
        self.clicked.disconnect(command)
    @property
    def commands(self) -> list:
        return self.__commands
    def SetIcon(self:CardButtonHint, icon:Union[str, QIcon, QPixmap]):
        _realIcon = icon
        if isinstance(icon, str):
            _realIcon = QIcon(icon)
        elif isinstance(icon, QIcon):
            _realIcon = QPixmap(icon.pixmap(self.size().width(), self.size().height()))
        self.iconLbl.setPixmap(icon)
    def SetBackgroundColor(self:CardButtonHint, color:Union[QColor,str]):
        '''override method of AppWidget.SetBackgroundColor'''
        if color is None:
            return
        if isinstance(color, str):
            color = QColor(color)
        hoverColor = [int(val*0.8) for val in color.toRgb().toTuple()] if appManager.config.isLightTheme() else [int(val*1.2) for val in color.toRgb().toTuple()]
        hoverColor[3] = 255
        pressedColor = [val*0.6 for val in color.toTuple()] if appManager.config.isLightTheme() else [val*1.4 for val in color.toTuple()]
        pressedColor[3] = 255
        sd = {'background-color': color.toTuple()}
        hsd = {'background-color': tuple(hoverColor)}
        psd = {'background-color': tuple(pressedColor)}
        StyledButton.setStyleDict(self, sd, 'default')
        StyledButton.setStyleDict(self, hsd, 'hover')
        StyledButton.setStyleDict(self, hsd, 'check-hover')
        StyledButton.setStyleDict(self, psd, 'press')
    def SetForegroundColor(self:CardButtonHint, color:Union[QColor,str]):
        '''override method of AppWidget.SetForegroundColor'''
        if color is None:
            return
        if isinstance(color, str):
            color = QColor(color)
        sd = {'color': color.toTuple()[:-1]}
        self.setStyleDict(sd, 'default')
        self.setStyleDict(sd, 'hover')
        self.setStyleDict(sd, 'check-hover')
        self.setStyleDict(sd, 'press')
    def SetFontSize(self:CardButtonHint, fontSize:int):
        '''override method of AppWidget.SetFontSize'''
        if fontSize is not None:
            sd = {'font-size': fontSize}
            self.setStyleDict(sd, 'default')
            self.setStyleDict(sd, 'hover')
            self.setStyleDict(sd, 'check-hover')
            self.setStyleDict(sd, 'press')
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.conwdt.setMinimumWidth(self.size().width())
        self.conlyt.setContentsMargins(self.width()*0.05, 0, self.width()*0.05, 0)
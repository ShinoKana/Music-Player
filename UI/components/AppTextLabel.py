from PySide2.QtWidgets import QLabel
from PySide2.QtGui import QColor, QPixmap, QIcon
from Core.Managers import appManager
from .AppWidget import AppWidget, AppWidgetHintClass
from typing import Literal, Union

TextLabelHint = Union[QLabel, AppWidgetHintClass, 'AppTextLabel']
class AppTextLabel(AppWidget(QLabel)):
    def __init__(self:TextLabelHint, text: str = None, fontSize:int=13,
                 height:int=20, fontColor:Union[QColor,str]=None, icon:Union[str, QPixmap, QIcon]=None,
                 textAlign:Literal['left', 'center', 'right','bottom', 'top', 'middle']='center',
                 wrap:bool=False,**kwargs):
        super().__init__(height=height, fontSize=fontSize,textAlign=textAlign, **kwargs)
        self.__text = text
        self.__fontColor = None
        self.__icon = None
        self.fontColor = self.foregroundColor
        self.SetFontColor = self.SetForegroundColor
        self.setText(text) if text else None
        self.SetIcon(icon) if icon else None
        self.wrap = wrap
        self.adjustSize()
        if fontColor is not None:
            self.SetFontColor(fontColor)
        else:
            self.SetFontColor('black' if appManager.config.isLightTheme() else 'white')

    @property
    def text(self) -> str:
        return self.__text
    @text.setter
    def text(self, text: str):
        self.SetText(text)
    def SetText(self:QLabel, text: str):
        if text is not None and text != self.__text:
            self.__text = text
            QLabel.setText(self,text)
            self.adjustSize()
    @property
    def wrap(self:TextLabelHint) -> bool:
        return self.wordWrap()
    @wrap.setter
    def wrap(self:TextLabelHint, wrap:bool):
        self.SetWrap(wrap)
    def SetWrap(self:TextLabelHint, wrap:bool):
        if wrap:
            self.setWordWrap(True)
            self.adjustSize()
        else:
            self.setWordWrap(False)
            self.adjustSize()
    @property
    def icon(self) -> QPixmap:
        return self.__icon
    @icon.setter
    def icon(self, iconPath: str):
        self.SetIcon(iconPath)
    def SetIcon(self: QLabel, icon: Union[str, QPixmap, QIcon]):
        if isinstance(icon, str):
            _icon = QIcon(icon)
        elif isinstance(icon, QPixmap) :
            _icon = icon
        elif isinstance(icon, QIcon):
            _icon = QPixmap(icon.pixmap(self.height(), self.height()))
        else:
            return
        self.__icon = icon
        QLabel.setPixmap(self, icon)






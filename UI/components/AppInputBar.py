from .AppWidget import AppWidget, AppWidgetHintClass
from .AppTextLabel import AppTextLabel
from PySide2.QtWidgets import QLineEdit, QWidget, QHBoxLayout
from PySide2.QtGui import QColor
from Core import appManager
from typing import Union

InputBarHint = Union[AppWidgetHintClass, QLineEdit, 'AppInputBar']
class AppInputBar(AppWidget(QLineEdit)):
    def __init__(self:InputBarHint, hintText="", fontSize=12, fontColor:Union[str,QColor]=None,
                 padding=(2, 2, 2, 2), height:int=40, **kwargs):
        super().__init__(padding=padding, height=height,
                         fontSize=fontSize, **kwargs)
        self.__hintText = None
        self.fontColor = self.foregroundColor
        self.SetFontColor = self.SetForegroundColor

        self.SetHintText(hintText)
        self.SetFontColor(fontColor if fontColor else 'black' if appManager.config.isLightTheme() else 'white')
        self.adjustSize()

    @property
    def hintText(self) -> str:
        return self.__hintText
    @hintText.setter
    def hintText(self, text: str):
        self.SetHintText(text)
    def SetHintText(self:InputBarHint, hintText: str):
        self.setPlaceholderText(hintText)
        self.__hintText = hintText

class AppInputBar_WithLabel(AppWidget(QWidget)):
    def __init__(self:InputBarHint, hintText="", fontSize=12, fontColor:Union[str,QColor]=None,
                 padding=(2, 2, 2, 2), height:int=40, labelText="", labelTextSize=12, **kwargs):
        super().__init__(padding=padding, height=height)
        self.__layout = QHBoxLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setSpacing(5)

        self.__label = AppTextLabel(text=labelText, fontSize=labelTextSize, backgroundColor='transparent')
        self.SetLabelText = self.__label.SetText
        self.labelText = self.__label.text
        self.SetLabelFontColor = self.__label.SetFontColor
        self.labelFontColor = self.__label.fontColor
        self.SetLabelTextSize = self.__label.SetFontSize
        self.labelTextSize = self.__label.fontSize
        self.__layout.addWidget(self.__label)

        self.__inputBar = AppInputBar(hintText=hintText, fontSize=fontSize, fontColor=fontColor,
                                        padding=padding, height=height, **kwargs)
        self.SetHintText = self.__inputBar.SetHintText
        self.hintText = self.__inputBar.hintText
        self.SetFontColor = self.__inputBar.SetFontColor
        self.fontColor = self.__inputBar.fontColor
        self.SetFontSize = self.__inputBar.SetFontSize
        self.fontSize = self.__inputBar.fontSize
        self.__layout.addWidget(self.__inputBar)

        self.setLayout(self.__layout)
        self.adjustSize()
from PySide2.QtWidgets import QTextEdit
from PySide2.QtGui import QColor
from .AppWidget import AppWidget, AppWidgetHintClass
from Core import appManager
from typing import Union, Literal

AppTextAreaHint = Union[QTextEdit, AppWidgetHintClass, 'AppTextArea']
class AppTextArea(AppWidget(QTextEdit)):
    def __init__(self:AppTextAreaHint,text: str = "", fontSize:int=12, height:int=40, editable:bool=True,
                 fontColor: Union[str,QColor] = None, textAlign: Literal['left', 'center', 'right','top','bottom','middle'] = 'center',
                 **kwargs):
        super().__init__(height=height, fontSize=fontSize,textAlign=textAlign, **kwargs)
        self.__editable = None
        self.__text = None
        self.__fontColor = None
        self.fontColor = self.foregroundColor
        self.SetFontColor = self.SetForegroundColor
        self.SetText(text)
        self.SetEditable(editable)
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
    def SetText(self:QTextEdit, text: str):
        if text is not None and text != self.__text:
            self.__text = text
            self.setText(text)
            self.adjustSize()
    @property
    def editable(self) -> bool:
        return self.__editable
    @editable.setter
    def editable(self, editable: bool):
        self.SetEditable(editable)
    def SetEditable(self:QTextEdit, editable: bool):
        if editable != self.__editable:
            self.__editable = editable
            QTextEdit.setReadOnly(self, not editable)
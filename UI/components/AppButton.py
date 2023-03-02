from .AppWidget import AppWidget, AppWidgetHintClass
from PySide2.QtGui import QColor
from typing import Union, Callable, List
from ExternalPackage.pyqt5Custom import StyledButton
from Core import appManager

ButtonHint = Union[AppWidgetHintClass, StyledButton, 'AppButton']
class AppButton(AppWidget(StyledButton)):
    def __init__(self:ButtonHint, height=40, fontSize=12, fontColor:Union[str,QColor]=None,
                 text="", icon:str=None, command:Callable[[],any]=None, **kwargs):
        super().__init__(height=height,text=text, icon=icon, **kwargs)
        self.conwdt.setStyleSheet("background-color:transparent;") # special treat for styled button
        self.__commands:List[Callable[[],any]] = []
        self.fontColor = self.foregroundColor
        self.SetFontSize(fontSize)
        self.SetFontColor(fontColor if fontColor else 'white' if not appManager.config.isLightTheme() else 'black')
        if command:
            self.addCommand(command)
        if 'backgroundColor' in kwargs.keys():
            self.SetBackgroundColor(kwargs['backgroundColor'])
        if 'foregroundColor' in kwargs.keys():
            self.SetForegroundColor(kwargs['foregroundColor'])
        if 'borderColor' in kwargs.keys():
            self.SetBorderColor(kwargs['borderColor'])
        if 'borderWidth' in kwargs.keys():
            self.SetBorderWidth(kwargs['borderWidth'])
        if 'borderCornerRadius' in kwargs.keys():
            self.SetBorderCornerRadius(kwargs['borderCornerRadius'])

        self.adjustSize()
    @property
    def commands(self:ButtonHint):
        return self.__commands
    def addCommand(self:ButtonHint, command:Callable[[],any]):
        self.__commands.append(command)
        self.clicked.connect(command)
    def removeCommand(self:ButtonHint, command:Callable[[],any]):
        if command not in self.__commands:
            return
        self.__commands.remove(command)
        self.clicked.disconnect(command)
    @property
    def text(self:ButtonHint):
        return StyledButton.text(self)
    @text.setter
    def text(self:ButtonHint, text:str):
        self.SetText(text)
    def SetText(self:ButtonHint, text:str):
        StyledButton.setText(self,text)

    def SetBackgroundColor(self:ButtonHint, color:Union[QColor,str]):
        '''override method of AppWidget.SetBackgroundColor'''
        if color is None:
            return
        if isinstance(color, str):
            color = QColor(color)
        self._backgroundColor = color
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
        #no need super for background color
    def SetForegroundColor(self:ButtonHint, color:Union[QColor,str]):
        '''override method of AppWidget.SetForegroundColor'''
        if color is None:
            return
        if isinstance(color, str):
            color = QColor(color)
        sd = {'color': color.toTuple()[:-1]}
        StyledButton.setStyleDict(self, sd, 'default')
        StyledButton.setStyleDict(self, sd, 'hover')
        StyledButton.setStyleDict(self, sd, 'check-hover')
        StyledButton.setStyleDict(self, sd, 'press')
        super().SetForegroundColor(color)
    def SetFontSize(self:ButtonHint, fontSize:int):
        '''override method of AppWidget.SetFontSize'''
        if fontSize is not None:
            if fontSize < 0 :
                return
            sd = {'font-size': fontSize}
            StyledButton.setStyleDict(self, sd, 'default')
            StyledButton.setStyleDict(self, sd, 'hover')
            StyledButton.setStyleDict(self, sd, 'check-hover')
            StyledButton.setStyleDict(self, sd, 'press')
            super().SetFontSize(fontSize)
    def SetFontColor(self:ButtonHint, color:Union[QColor,str]):
        '''override method of AppWidget.SetFontColor'''
        self.SetForegroundColor(color)
    def SetBorderCornerRadius(self:ButtonHint, radius:int):
        '''override method of AppWidget.SetBorderCornerRadius'''
        if radius is not None:
            if radius < 0:
                return
            sd = {'border-radius': radius}
            StyledButton.setStyleDict(self, sd, 'default')
            StyledButton.setStyleDict(self, sd, 'hover')
            StyledButton.setStyleDict(self, sd, 'check-hover')
            StyledButton.setStyleDict(self, sd, 'press')
            super().SetBorderCornerRadius(radius)
    def SetBorderWidth(self:ButtonHint, width:int):
        '''override method of AppWidget.SetBorderWidth'''
        if width is not None:
            if width < 0 :
                return
            sd = {'border-width': width}
            StyledButton.setStyleDict(self, sd, 'default')
            StyledButton.setStyleDict(self, sd, 'hover')
            StyledButton.setStyleDict(self, sd, 'check-hover')
            StyledButton.setStyleDict(self, sd, 'press')
            super().SetBorderWidth(width)
    def SetBorderColor(self:ButtonHint, color:Union[QColor,str]):
        '''override method of AppWidget.SetBorderColor'''
        if color is None:
            return
        if isinstance(color, str):
            color = QColor(color)
        sd = {'border-color': color.toTuple()[:-1]}
        StyledButton.setStyleDict(self,sd, 'default')
        StyledButton.setStyleDict(self,sd, 'hover')
        StyledButton.setStyleDict(self,sd, 'check-hover')
        StyledButton.setStyleDict(self,sd, 'press')
        super().SetBorderColor(color)
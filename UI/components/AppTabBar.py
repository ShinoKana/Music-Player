from PySide2.QtWidgets import QTabBar
from PySide2.QtGui import QIcon,QPixmap
from PySide2.QtCore import QSize
from .AppWidget import AppWidget, AppWidgetHintClass
from typing import Union, Tuple, Callable, Sequence
from Core import appManager

TabBarHint = Union[QTabBar,'AppTabBar',AppWidgetHintClass]
class AppTabBar(AppWidget(QTabBar)):
    def __init__(self:TabBarHint,*args, height=30, tabs:Sequence[Tuple[str,Union[str,QIcon,QPixmap,None],Callable[[],any]]]=None,
                 fontSize=15, padding=(0,0,8,8),**kwargs):
        super().__init__(*args, height=height, fontSize=fontSize, padding=padding, **kwargs)
        self.__tabCommands = []
        self.setIconSize(QSize(int(self.height()*0.85),int(self.height()*0.85)))
        if tabs:
            for tab in tabs:
                self.addTab(tab[0],tab[1],tab[2])
        self.adjustSize()
    def changeStyle(self:TabBarHint, styleKey, value):
        super().changeStyle(styleKey, value)
        barStyle = self.componentStyleDict.copy()
        barStyle['background-color'] = 'transparent'
        barStyle = ''.join([f'{key}:{value};' for key, value in barStyle.items()])
        tabStyle = self.componentStyleDict.copy()
        tabStyle['border-top-left-radius'] = '{}px'.format(self.leftUpBorderCornerRadius)
        tabStyle['border-top-right-radius'] = '{}px'.format(self.rightUpBorderCornerRadius)
        tabStyle['border-bottom-left-radius'] = '0px'
        tabStyle['border-bottom-right-radius'] = '0px'
        tabStyle = ''.join([f'{key}:{value};' for key, value in tabStyle.items()])
        selectedColor = (self.backgroundColor.lighter(130) if not appManager.config.isLightTheme() else self.backgroundColor.darker(130)).name()
        hoverColor = (self.backgroundColor.lighter(115) if not appManager.config.isLightTheme() else self.backgroundColor.darker(115)).name()
        fontColor = self.foregroundColor if self.foregroundColor else 'black' if appManager.config.isLightTheme() else 'white'
        self.setStyleSheet("QTabBar{" +barStyle +f"height:{self.height()};"+ "}"+
                           "QTabBar::tab{" + tabStyle +"color: "+fontColor+f";height:{self.height()};"+";}"+
                           "QTabBar::tab:hover { background:"+hoverColor+";}" +
                           "QTabBar::tab:selected { background-color: "+selectedColor+f";height:{self.height()+5};"+"}"+
                           "QTabBar::tab:!selected { margin-top: 5px;}")
    def addTab(self, text:str, icon:Union[str,QIcon,QPixmap]=None, callback:Callable[[],any]=None):
        if isinstance(icon, str) or isinstance(icon, QPixmap):
            icon = QIcon(icon)
        if icon:
            buttonIndex = QTabBar.addTab(self,icon,text)
        else:
            buttonIndex = QTabBar.addTab(self,text)
        if callback:
            self.currentChanged.connect(lambda index: callback() if index == buttonIndex else None)
        self.__tabCommands.append(callback)
    def removeTab(self, index:int):
        QTabBar.removeTab(self,index)
        self.__tabCommands.pop(index)
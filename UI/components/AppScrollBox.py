from ExternalPackage import ScrollArea, ExpandLayout
from .AppWidget import AppWidget, AppWidgetHintClass
from typing import Union
from PySide2.QtWidgets import QWidget, QLabel
from PySide2.QtCore import Qt
from Core.Managers import appManager

ScrollBoxHint = Union[ScrollArea, AppWidgetHintClass, 'AppScrollBox']
class AppScrollBox(AppWidget(ScrollArea)):
    def __init__(self:ScrollBoxHint, titleText:str=None, titleTextSize:int=14, height=200, **kwargs):
        super().__init__(height=height, **kwargs)

        self.__titleText = None
        self.__titleTextSize = None
        self.__components = []
        self.titleLabel = QLabel(parent=self)
        self.titleLabel.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
        self.titleLabel.setContentsMargins(0, 0, 5, 0)
        self.titleLabel.setStyleSheet('color: {};'.format('black' if appManager.config.isLightTheme() else 'white') +
                                      'background-color: {};'.format(self.backgroundColor.darker(120).name()
                                                                     if appManager.config.isLightTheme() else
                                                                     self.backgroundColor.lighter(120).name()))
        if titleText:
            self.SetTitleText(titleText)
        self.SetFontSize(titleTextSize)
        self.titleLabel.adjustSize()
        self.titleLabel.resize(self.titleLabel.width(), self.titleLabel.height() + 10)

        self.scrollWidget = QWidget(self)

        self.expandLayout = ExpandLayout(self.scrollWidget)
        self.expandLayout.setSpacing(5)
        self.expandLayout.setContentsMargins(10,0,10,0)
        self.expandLayout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, self.titleLabel.size().height()+5, 0, 10)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.adjustSize()
        self.adjustScrollAreaSize()

    #region title text
    @property
    def titleText(self) -> str:
        return self.__titleText
    @titleText.setter
    def titleText(self:ScrollBoxHint, titleText: str):
        self.SetTitleText(titleText)
    def SetTitleText(self:ScrollBoxHint, titleText: str):
        self.titleLabel.setText(titleText)
        self.__titleText = titleText
    @property
    def titleTextSize(self) -> int:
        return self.__titleTextSize
    @titleTextSize.setter
    def titleTextSize(self:ScrollBoxHint, titleTextSize: int):
        self.SetTitleTextSize(titleTextSize)
    def SetTitleTextSize(self:ScrollBoxHint, titleTextSize: int):
        if titleTextSize == self.__titleTextSize:
            return
        self.titleLabel.font().setPointSize(titleTextSize)
        self.__titleTextSize = titleTextSize
    #endregion
    @property
    def components(self) -> list:
        return self.__components

    def resizeEvent(self:ScrollBoxHint, e):
        ''' override resizeEvent of QScrollArea '''
        self.scrollWidget.resize(self.width(), self.scrollWidget.height())
        self.titleLabel.resize(self.scrollWidget.size().width()*0.97, self.titleLabel.height()) if self.titleLabel else None
        self.titleLabel.move(int((self.scrollWidget.size().width() - self.titleLabel.size().width())/2), 0) if self.titleLabel else None
        super().resizeEvent(e)
    def addComponent(self:ScrollBoxHint, component):
        if isinstance(component, QWidget):
            component.setParent(self.scrollWidget)
            self.expandLayout.addWidget(component)
        else:
            newWidget = QWidget(self.scrollWidget)
            newWidget.setLayout(component)
            self.expandLayout.addWidget(newWidget)
        component.show()
        self.__components.append(component)
        self.adjustScrollAreaSize()
    def removeComponent(self:ScrollBoxHint, component):
        if component not in self.components:
            return
        self.expandLayout.removeWidget(component)
        component.setParent(None)
        self.__components.remove(component)
        component.deleteLater()
    def adjustScrollAreaSize(self):
        self.scrollWidget.adjustSize()
        self.scrollWidget.resize(self.scrollWidget.size())
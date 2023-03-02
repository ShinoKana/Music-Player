from PySide2.QtWidgets import QWidget, QVBoxLayout, QLayout
from .AppWidget import AppWidget, AppWidgetHintClass
from .AppButton import AppButton
from typing import Union, Callable
from Core import appManager

foldBoxHint= Union[QWidget, AppWidgetHintClass, 'AppFoldBox']
class AppFoldBox(AppWidget(QWidget)):

    def __init__(self:foldBoxHint, *args, titleText:str, foldingIcon:str=None, openningIcon:str=None,
                 buttonHeight:int=50, onHide:Callable[[],any]=None, onShow:Callable[[],any]=None,
                 defaultHide:bool=True, **kwargs):
        super().__init__(*args, height=buttonHeight, **kwargs)
        self._onShow = []
        self._onHide = []
        self._folded = False
        self._components = []
        self._foldIcon = foldingIcon
        self._openIcon = openningIcon
        self.outerLayout = QVBoxLayout(self)
        self.outerLayout.setContentsMargins(0, 0, 0, 0)
        self.outerLayout.setSpacing(0)

        #button
        self.foldButton = AppButton(text=titleText)
        self.foldButton.setFixedHeight(buttonHeight)
        self.outerLayout.addWidget(self.foldButton)

        #inner
        self.innerLayout = QVBoxLayout()
        self.innerLayout.setContentsMargins(5, 6, 5, 6)
        self.innerLayout.setSpacing(4)
        self.innerLayoutWidget:AppWidgetHintClass = AppWidget(QWidget)(parent=self, borderCornerRadius=(0,0,10,10))
        self.innerLayoutWidget.setLayout(self.innerLayout)
        self.outerLayout.addWidget(self.innerLayoutWidget)

        self.SetBackgroundColor(self.furthurBackgroundColor)
        self.SetBackgroundColor = self.innerLayoutWidget.SetBackgroundColor
        self.backgroundColor = self.innerLayoutWidget.backgroundColor

        if onHide is not None:
            self._onHide.append(onHide)
        if onShow is not None:
            self._onShow.append(onShow)

        def _onFoldButtonClicked():
            if self._folded:
                self.showInner()
            else:
                self.hideInner()
        self.foldButton.clicked.connect(_onFoldButtonClicked)
        self.adjustSize()

        if defaultHide:
            self.foldButton.clicked.emit()

    #region callbacks
    def addOnHideCallback(self, callback:Callable[[],any]):
        self._onHide.append(callback)
    def addOnShowCallback(self, callback:Callable[[],any]):
        self._onShow.append(callback)
    def removeOnHideCallback(self, callback:Callable[[],any]):
        self._onHide.remove(callback)
    def removeOnShowCallback(self, callback:Callable[[],any]):
        self._onShow.remove(callback)
    #endregion

    #components
    @property
    def components(self)->tuple:
        return tuple(self._components)
    def getComponentByIndex(self, index:int)->foldBoxHint:
        return self._components[index]
    def addComponent(self, component:Union[QWidget, QLayout])->QWidget:
        if isinstance(component, QLayout):
            widget = QWidget()
            widget.setLayout(component)
            self.innerLayout.addLayout(widget)
            self._components.append(widget)
        else:
            self.innerLayout.addWidget(component)
            self._components.append(component)
        self.adjustSize()
        return component
    def removeComponent(self, component:QWidget):
        if component in self._components:
            self.innerLayout.removeWidget(component)
            self._components.remove(component)
            self.adjustSize()

    #show & hide
    def hideInner(self,emitCallback=True):
        self.foldButton.setIcon(appManager.getUIImagePath('right_arrow.png' if self._foldIcon is None else self._foldIcon))
        self.innerLayoutWidget.hide()
        self.setMinimumHeight(self.foldButton.height())
        self.adjustSize()
        if emitCallback:
            for callback in self._onHide:
                callback()
        self._folded = True
    def showInner(self, emitCallback=True):
        self.foldButton.setIcon(appManager.getUIImagePath('down_arrow.png' if self._openIcon is None else self._openIcon))
        self.innerLayoutWidget.show()
        self.innerLayoutWidget.adjustSize()
        self.setMinimumHeight(self.innerLayoutWidget.height()+self.foldButton.height())
        self.adjustSize()
        if emitCallback:
            for callback in self._onShow:
                callback()
        self._folded = False


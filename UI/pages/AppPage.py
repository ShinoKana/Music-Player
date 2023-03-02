from typing import Union
from ExternalPackage import ScrollArea, ExpandLayout, setStyleSheet
from PySide2.QtWidgets import QWidget, QLabel, QFrame, QLayout
from PySide2.QtCore import Qt, QSize

class AppPage(ScrollArea):
    _changedPageClass = []
    def __new__(cls, *args, **kwargs):
        if cls not in AppPage._changedPageClass:
            AppPage._changedPageClass.append(cls)
            originInit = cls.__init__
            def newInit(self, *args, **kwargs):
                originInit(self, *args, **kwargs)
                self.adjustScrollAreaSize()
            cls.__init__ = newInit
        return super().__new__(cls, *args, **kwargs)
    def __init__(self, appWindow:'AppWindow', parent:Union[QFrame, QLayout]=None, titleText:str=None,
                 verticalSpace:int=9, margins=(10,0,40,40)):
        super().__init__(parent=parent)
        self.appWindow = appWindow
        self.scrollWidget = QWidget()
        self.scrollWidget.setObjectName('scrollWidget')
        self.__verticalSpace = verticalSpace
        self.__margins = {'left':margins[0], 'top':margins[1], 'right':margins[2], 'bottom':margins[3]}

        self.expandLayout = ExpandLayout(self.scrollWidget)
        self.expandLayout.setAlignment(Qt.AlignTop|Qt.AlignHCenter)
        self.SetVerticalSpace(verticalSpace)
        self.SetMargins(margins)

        self.resize(*self.appWindow.APP_PAGE_DEFAULT_SIZE)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, int(self.appWindow.APP_PAGE_DEFAULT_SIZE[1]*0.12), 0, 0)
        self.setWidget(self.scrollWidget)

        # Title Label
        if titleText:
            self.titleLabel = QLabel(text=titleText, parent=self)
            self.titleLabel.setObjectName('settingLabel')  # copy style from settingPage, thus name is settingLabel
            self.titleLabel.move(int(0.03*self.appWindow.APP_PAGE_DEFAULT_SIZE[0]), int(0.0375*self.appWindow.APP_PAGE_DEFAULT_SIZE[1]))

        setStyleSheet(self, 'setting_interface') # copy style from settingPage(from package qfluentwidgets)

        if parent:
            parent.addWidget(self)
    @property
    def verticalSpace(self):
        return self.__verticalSpace
    @verticalSpace.setter
    def verticalSpace(self, value:int):
        self.SetVerticalSpace(value)
    def SetVerticalSpace(self, value:int):
        self.__verticalSpace = value
        self.expandLayout.setSpacing(self.__verticalSpace)
    @property
    def margins(self)->tuple:
        return (self.__margins['top'], self.__margins['bottom'], self.__margins['left'], self.__margins['right'])
    @margins.setter
    def margins(self, value:Union[tuple,int]):
        self.SetMargins(value)
    def SetMargins(self, *args):
        if len(args) == 1:
            if isinstance(args[0], int):
                self.SetMargins(args[0], args[0], args[0], args[0])
            elif isinstance(args[0], tuple) and len(args[0]) == 4:
                self.SetMargins(*args[0])
        elif len(args) == 4:
            self.__margins['top'] = args[0] if args[0] is not None else None
            self.__margins['bottom'] = args[1] if args[1] is not None else None
            self.__margins['left'] = args[2] if args[2] is not None else None
            self.__margins['right'] = args[3] if args[3] is not None else None
            self.expandLayout.setContentsMargins(self.__margins['left'], self.__margins['top'],
                                                    self.__margins['right'], self.__margins['bottom'])
        else:
            raise ValueError('margins must be tuple or 4 int')

    def onSwitchIn(self):
        pass
    def onSwitchOut(self):
        pass

    def resizeEvent(self, e):
        ''' override resizeEvent of QScrollArea '''
        self.scrollWidget.resize(self.width(), self.scrollWidget.height())
        super().resizeEvent(e)

    def addComponent(self, component:Union[QWidget, QLayout], expandWidth=False):
        try:
            component.appWindow = self.appWindow
        except:
            pass
        if isinstance(component, QWidget):
            component.setParent(self.scrollWidget)
            if expandWidth:
                component.setMinimumWidth(self.appWindow.APP_PAGE_DEFAULT_SIZE[0] - self.__margins['left'] - self.__margins['right'])
            self.expandLayout.addWidget(component)
        elif isinstance(component, QLayout):
            newWidget = QWidget(self.scrollWidget)
            newWidget.setLayout(component)
            if expandWidth:
                newWidget.setMinimumWidth(self.appWindow.APP_PAGE_DEFAULT_SIZE[0] - self.__margins['left'] - self.__margins['right'])
            newWidget.adjustSize()
            self.expandLayout.addWidget(newWidget)
        else:
            raise TypeError('component must be QWidget or QLayout')
    def addSpace(self, height:int):
        widget = QWidget()
        widget.setFixedHeight(height)
        self.addComponent(widget)

    def adjustScrollAreaSize(self):
        self.scrollWidget.adjustSize()
        self.scrollWidget.resize(self.scrollWidget.size() + QSize(0, int(0.05*self.appWindow.APP_PAGE_DEFAULT_SIZE[1])))


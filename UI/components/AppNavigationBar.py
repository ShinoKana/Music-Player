from typing import Sequence,Callable,Tuple
from PySide2.QtCore import Qt, QSize
from PySide2.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout
from ExternalPackage.pyqt5Custom import ImageBox
from .AppWidget import AppWidget, AppWidgetHintClass
from typing import Union, Literal
from .AppButton import AppButton

NaviBarHint = Union[AppWidgetHintClass, 'AppNavigationBar', QWidget]
class AppNavigationBar(AppWidget(QWidget)):
    def __init__(self:NaviBarHint, logoPath: str = None, width=140, height=50,
                 buttons: Sequence[Tuple[str, str, Callable[[], any]]] = None,
                 borderCornerRadius=0, direction:Literal['Horizontal','Vertical']='Vertical', **kwargs):
        super().__init__(borderCornerRadius=borderCornerRadius, **kwargs)
        self.__direction = direction
        if direction =='Vertical':
            self.setFixedWidth(width) if width else None
        else:
            self.setFixedHeight(height) if height else None

        self.setAutoFillBackground(True)

        if direction=='Vertical':
            self.navigationBar = QVBoxLayout()
            self.navigationBar.setSpacing(8)
            self.navigationBar.setContentsMargins(5,5,5,5)
            self.navigationBar.addWidget(QWidget(), stretch=1)
        else:
            self.navigationBar = QHBoxLayout()
            self.navigationBar.setSpacing(2)
            self.navigationBar.setContentsMargins(5,1,5,1)

        self.buttons={}
        self.icons={}

        if logoPath:
            self.addIcon(logoPath)
        if buttons:
            for button in buttons:
                self.addButton(*button)
        self.setLayout(self.navigationBar)
        self.adjustSize()

    def addButton(self, text, iconPath=None, command=None)->'AppButton':
        if text in self.buttons.keys():
            return self.buttons[text]
        button = AppButton(text=text, icon=iconPath)
        button.SetBorderCornerRadius(5) if self.__direction=='Horizontal' else None
        if self.__direction =='Vertical':
            w, h = int(self.width()*0.9), int(self.width()*0.6)
        else:
            w, h = int(len(text)*15+18), int(self.height()*0.8)
        button.setFixedSize(QSize(w, h))
        button.setIconSize(int(h/2.5),int(h/2.5)) if iconPath else None
        if self.__direction=='Vertical':
            self.navigationBar.insertWidget(len(self.buttons),button, alignment=Qt.AlignTop | Qt.AlignHCenter)
        else:
            self.navigationBar.insertWidget(len(self.buttons),button, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self.buttons[text]=button
        button.adjustSize()
        if command:
            button.clicked.connect(command)
        return button
    def removeButton(self, text):
        if text not in self.buttons.keys():
            raise Exception("AppButton with text '{}' does not exist".format(text))
        self.navigationBar.removeWidget(self.buttons[text])
        self.buttons[text].deleteLater()
        del self.buttons[text]
    def addIcon(self, iconPath:str):
        if iconPath in self.icons.keys():
            return
        icon = ImageBox(iconPath)
        icon.setMinimumWidth(int(self.width() * 0.8)) if self.__direction=='Vertical' else icon.setMinimumHeight(int(self.height() * 0.8))
        if self.__direction=='Vertical':
            self.navigationBar.addWidget(icon, alignment=Qt.AlignBottom, stretch=1)
        else:
            self.navigationBar.addWidget(icon, alignment=Qt.AlignRight, stretch=1)
        self.icons[iconPath]=icon
    def removeIcon(self, iconPath:str):
        if iconPath not in self.icons.keys():
            return
        self.navigationBar.removeWidget(self.icons[iconPath])
        self.icons[iconPath].deleteLater()
        del self.icons[iconPath]

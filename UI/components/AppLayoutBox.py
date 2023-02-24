from PySide2.QtWidgets import QLabel, QWidget, QHBoxLayout, QVBoxLayout
from PySide2.QtGui import QColor, QPixmap, QIcon
from PySide2.QtCore import Qt
from .AppWidget import AppWidget, AppWidgetHintClass
from typing import Union, Sequence, Tuple, Callable, Optional, Literal
from .AppTextLabel import AppTextLabel
from .AppButton import AppButton

ItemBoxHint = Union[QWidget, AppWidgetHintClass, 'AppLayoutBox']
class AppLayoutBox(AppWidget(QWidget)):
    def __init__(self: ItemBoxHint, height: int = 30, width=100, direction:Literal['Horizontal','Vertical']='Horizontal',
                 contain:Sequence[Tuple[Union[Tuple[str],Tuple[Union[QPixmap,QIcon]],
                                  Tuple[Optional[str],Union[str,QPixmap,QIcon,None],Optional[Callable[[],any]]],
                                  Tuple[Union[QWidget, AppWidgetHintClass]]]]]=None,
                 align:Literal['left','right','top','bottom','center']='center', **kwargs):
        super().__init__(**kwargs)
        self.__align = None
        self.__components = []
        self.__direction = direction

        if direction == 'Horizontal':
            self.setMinimumHeight(height) if height else None
            self.layout = QHBoxLayout(self)
            self.layout.setContentsMargins(self.size().width() * 0.04, height * 0.2,
                                           self.size().width() * 0.04, height * 0.2)
            self.layout.setSpacing(int(self.width() * 0.08))
        else:
            self.setMinimumWidth(width) if width else None
            self.layout = QVBoxLayout(self)
            self.layout.setContentsMargins(width * 0.1, self.size().height() * 0.04,
                                           width * 0.1, self.size().height() * 0.04)
            self.layout.setSpacing(int(self.height() * 0.08))
        self.SetAlign(align)
        if contain:
            for item in contain:
                if len(item) == 1:
                    if isinstance(item[0], str):
                        self.addText(item[0])
                    elif isinstance(item[0], QWidget):
                        self.addWidget(item[0])
                    elif isinstance(item[0], QIcon) or isinstance(item[0], QPixmap):
                        self.addImage(item[0])
                else:
                    self.addButton(*item)

        self.adjustSize()
    @property
    def components(self) -> Sequence[Union[QLabel, AppTextLabel, AppButton, QWidget]]:
        return self.__components
    def getComponent(self, index:int) -> Union[QLabel, AppTextLabel, AppButton, QWidget]:
        if index >= len(self.__components):
            raise None
        return self.__components[index]
    @property
    def direction(self) -> Literal['Horizontal','Vertical']:
        return self.__direction
    @property
    def align(self) -> Literal['left','right','top','bottom','center']:
        return self.__align
    @align.setter
    def align(self, align:Literal['left','right','top','bottom','center']):
        self.SetAlign(align)
    def SetAlign(self, align:Literal['left','right','top','bottom','center']):
        ali = Qt.AlignVCenter if self.direction == "Horizontal" else Qt.AlignHCenter
        if align == 'left':
            self.layout.setAlignment(Qt.AlignLeft | ali)
        elif align == 'right':
            self.layout.setAlignment(Qt.AlignRight | ali)
        elif align == 'top':
            self.layout.setAlignment(Qt.AlignTop | ali)
        elif align == 'bottom':
            self.layout.setAlignment(Qt.AlignBottom | ali)
        elif align == 'center':
            self.layout.setAlignment(Qt.AlignCenter | ali)
        self.__align = align
    def addImage(self, img:Union[QPixmap, str, QIcon], stretch:int=0) -> QLabel:
        if isinstance(img, str):
            img = QPixmap(img).scaled(int(self.height()*0.95), int(self.height()*0.95), Qt.KeepAspectRatio)
        elif isinstance(img, QPixmap):
            img = img.scaled(int(self.height()*0.95), int(self.height()*0.95), Qt.KeepAspectRatio)
        elif isinstance(img, QIcon):
            img = img.pixmap(int(self.height()*0.95), int(self.height()*0.95)).scaled(int(self.height()*0.95), int(self.height()*0.95), Qt.KeepAspectRatio)
        label = QLabel()
        label.setPixmap(img)
        self.layout.addWidget(label, stretch=stretch)
        self.__components.append(label)
        #self.adjustSize()
        return label
    def addText(self, text:str, fontSize:int=None, fontColor:Union[str,QColor]=None, stretch:int=0) -> AppTextLabel:
        label = AppTextLabel(text=text, fontSize=fontSize, fontColor=fontColor, height=int(self.height()*0.93))
        label.SetBackgroundColor('transparent')
        self.layout.addWidget(label, stretch=stretch)
        self.__components.append(label)
        #self.adjustSize()
        return label
    def addButton(self, text=None, img:Union[QPixmap, str, QIcon]=None, command:Callable[[],any]=None, stretch:int=0) -> AppButton:
        button = AppButton(parent=self, text=text, icon=img, height=int(self.height()*0.95), command=command)
        self.layout.addWidget(button, stretch=stretch)
        self.__components.append(button)
        self.adjustSize()
        return button
    def addWidget(self, widget:QWidget, stretch:int=0):
        if isinstance(widget, QWidget):
            widget.setParent(self)
            widget.resize(widget.size().width(),int(self.height()*0.95))
            self.__components.append(widget)
            self.layout.addWidget(widget, stretch=stretch)
            self.adjustSize()
        else:
            raise TypeError("widget must be QWidget")



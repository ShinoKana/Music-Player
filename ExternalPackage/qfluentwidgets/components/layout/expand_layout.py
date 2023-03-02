# coding:utf-8
from typing import List

from PySide2.QtCore import QSize, QPoint, Qt, QEvent, QRect
from PySide2.QtGui import QResizeEvent
from PySide2.QtWidgets import QLayout, QLayoutItem, QWidget

class ExpandLayout(QLayout):
    """ Expand layout """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []   #type:List[QLayoutItem]
        self._widgets = [] #type:List[QWidget]
    @property
    def allWidgets(self)->tuple:
        return tuple(self._widgets)
    def removeWidget(self, widget: QWidget):
        if widget in self._widgets:
            self._widgets.remove(widget)
            super().removeWidget(widget)
    def addWidget(self, widget: QWidget):
        if widget in self._widgets:
            return
        self._widgets.append(widget)
        widget.installEventFilter(self)
    def insertWidget(self, index: int, widget: QWidget):
        if widget in self._widgets:
            return
        self._widgets.insert(index, widget)
        widget.installEventFilter(self)
    def addItem(self, item: QLayoutItem):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index: int):
        if 0 <= index < len(self._items):
            return self._items[index]

        return None

    def takeAt(self, index: int):
        if 0 <= index < len(self._items):
            self._widgets.pop(index)
            return self._items.pop(index)

        return None

    def expandingDirections(self):
        return Qt.Vertical

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width: int):
        """ getTranslation the minimal height according to width """
        return self.__doLayout(QRect(0, 0, width, 0), False)

    def setGeometry(self, rect: QRect):
        super().setGeometry(rect)
        self.__doLayout(rect, True)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for w in self._widgets:
            size = size.expandedTo(w.minimumSize())

        m = self.contentsMargins()
        size += QSize(m.left()+m.right(), m.top()+m.bottom())

        return size

    def __doLayout(self, rect: QRect, move: bool):
        """ adjust widgets position according to the window size """
        margin = self.contentsMargins()
        x = rect.x() + margin.left()
        y = rect.y() + margin.top() + margin.bottom()
        width = rect.width() - margin.left() - margin.right()

        for i, w in enumerate(self._widgets):
            y += (i>0)*self.spacing()
            if move:
                w.setGeometry(QRect(QPoint(x, y), QSize(width, w.height())))
            y += w.height()
        return y - rect.y()

    def eventFilter(self, obj, e: QEvent) -> bool:
        if obj in self._widgets:
            if e.type() == QEvent.Resize:
                re = QResizeEvent(e.size(), e.oldSize())
                ds = re.size() - re.oldSize()  # type:QSize
                if ds.height() != 0 and ds.width() == 0:
                    w = self.parentWidget()
                    w.resize(w.width(), w.height() + ds.height())

        return super().eventFilter(obj, e)

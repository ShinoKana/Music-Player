# coding:utf-8
#from PyQt5.QtCore import QSize, QPoint, Qt, QRect
#from PyQt5.QtWidgets import QLayout
from PySide2.QtCore import QSize, QPoint, Qt, QRect
from PySide2.QtWidgets import QLayout

class FlowLayout(QLayout):
    """ Flow layout """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._verticalSpacing = 10
        self._horizontalSpacing = 10

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index: int):
        if 0 <= index < len(self._items):
            return self._items[index]

        return None

    def takeAt(self, index: int):
        if 0 <= index < len(self._items):
            return self._items.pop(index)

        return None

    def removeAllWidgets(self):
        """ remove all widgets from layout """
        while self._items:
            self.takeAt(0)

    def expandingDirections(self):
        return Qt.Orientation(0)

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

        for item in self._items:
            size = size.expandedTo(item.minimumSize())

        m = self.contentsMargins()
        size += QSize(m.left()+m.right(), m.top()+m.bottom())

        return size

    def setVerticalSpacing(self, spacing: int):
        """ set vertical spacing between widgets """
        self._verticalSpacing = spacing

    def verticalSpacing(self):
        """ getTranslation vertical spacing between widgets """
        return self._verticalSpacing

    def setHorizontalSpacing(self, spacing: int):
        """ set horizontal spacing between widgets """
        self._horizontalSpacing = spacing

    def horizontalSpacing(self):
        """ getTranslation horizontal spacing between widgets """
        return self._horizontalSpacing

    def __doLayout(self, rect: QRect, move: bool):
        """ adjust widgets position according to the window size """
        margin = self.contentsMargins()
        x = rect.x() + margin.left()
        y = rect.y() + margin.top()
        rowHeight = 0
        spaceX = self.horizontalSpacing()
        spaceY = self.verticalSpacing()

        for item in self._items:
            nextX = x + item.sizeHint().width() + spaceX

            if nextX - spaceX > rect.right() and rowHeight > 0:
                x = rect.x() + margin.left()
                y = y + rowHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                rowHeight = 0

            if move:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            rowHeight = max(rowHeight, item.sizeHint().height())

        return y + rowHeight - rect.y()

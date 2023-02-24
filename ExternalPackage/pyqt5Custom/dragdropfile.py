#                 PyQt5 Custom Widgets                #
#                GPL 3.0 - Kadir Aksoy                #
#   https://github.com/kadir014/pyqt5-custom-widgets  #

from PySide2.QtCore    import Qt, Signal
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide2.QtGui     import QColor, QPainter, QPen, QBrush, QDropEvent
from .imagebox import ImageBox
from Core.DataType import FileInfo

class DragDropFile(QWidget):

    fileDropped = Signal(FileInfo)
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.appManager = __import__("Core").Managers.appManager
        self.setAcceptDrops(True)

        self.setMinimumSize(120, 65)

        self.thisBorderColor = QColor(190, 190, 190)
        self.hoverBackground = QColor(245, 245, 250)
        self.thisBorderRadius = 26
        self.thisBorderWidth = 6

        self.layout = QVBoxLayout()
        #self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)

        #self.title_lbl = QLabel(AutoTranslateWord("Drop your file here!").getTranslation())
        self.title_lbl = QLabel()
        self.addIcon = ImageBox(self.appManager.getUIImagePath("plus.png"))

        self.layout.addWidget(self.title_lbl, alignment=Qt.AlignCenter)
        self.layout.addSpacing(7)
        self.layout.addWidget(self.addIcon, alignment=Qt.AlignCenter)

        #self.title_lbl.setStyleSheet("font-size:19px;")
        #self.filename_lbl.setStyleSheet("font-size:14px; color: #666666;")

        self.dragEnter = False

        self.file = None

    def setTitle(self, title):
        self.title_lbl.setText(title)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self.dragEnter = True
            event.accept()
            self.repaint()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.dragEnter = False
        self.repaint()

    def dropEvent(self, event:QDropEvent):
        for url in event.mimeData().urls():
            file = FileInfo(url.toLocalFile())
            self.fileDropped.emit(file)

        self.dragEnter = False
        self.repaint()

    def paintEvent(self, event):
        pt = QPainter()
        pt.begin(self)
        pt.setRenderHint(QPainter.Antialiasing, on=True)

        pen = QPen(self.thisBorderColor, self.thisBorderWidth, Qt.DotLine, Qt.RoundCap)
        pt.setPen(pen)

        if self.dragEnter:
            brush = QBrush(self.hoverBackground)
            pt.setBrush(brush)

        pt.drawRoundedRect(self.thisBorderWidth, self.thisBorderWidth, self.width()-self.thisBorderWidth*2, self.height()-self.thisBorderWidth*2, self.thisBorderRadius, self.thisBorderRadius)

        pt.end()

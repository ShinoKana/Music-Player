# coding:utf-8
from PySide2.QtCore import QEasingCurve, Signal, QSize, QPoint,QPropertyAnimation, QTimer,Qt
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import QWidget, QToolButton, QGraphicsOpacityEffect

from .label import PixmapLabel
from ...common import setStyleSheet

_toastCount = 0

class StateToolTip(QWidget):
    """ State tooltip """

    closedSignal = Signal()
    def __init__(self, title, content, parent=None):
        """
        Parameters
        ----------
        title: str
            _thisTitle of tooltip

        content: str
            _thisContent of tooltip

        parant:
            parentLayout window
        """
        super().__init__(parent)
        self.title = title
        self.content = content

        self.titleLabel = QLabel(self.title, self)
        self.contentLabel = QLabel(self.content, self)
        self.rotateTimer = QTimer(self)
        self.closeTimer = QTimer(self)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.busyImage = QPixmap(":/qfluentwidgets/images/state_tool_tip/running.png")
        self.doneImage = QPixmap(":/qfluentwidgets/images/state_tool_tip/completed.png")
        self.closeButton = QToolButton(self)

        self.isDone = False
        self.rotateAngle = 0
        self.deltaAngle = 20

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setAttribute(Qt.WA_StyledBackground)
        self.rotateTimer.setInterval(50)
        self.closeTimer.setInterval(1000)
        self.contentLabel.setMinimumWidth(200)

        # connect signal to slot
        self.closeButton.clicked.connect(self.__onCloseButtonClicked)
        self.rotateTimer.timeout.connect(self.__rotateTimerFlowSlot)
        self.closeTimer.timeout.connect(self.__slowlyClose)

        self.__setQss()
        self.__initLayout()

        self.rotateTimer.start()

    def __initLayout(self):
        """ initialize layout """
        self.setFixedSize(max(self.titleLabel.width(),
                          self.contentLabel.width()) + 70, 64)
        self.titleLabel.move(40, 11)
        self.contentLabel.move(15, 34)
        self.closeButton.move(self.width() - 30, 23)

    def __setQss(self):
        """ set style sheet """
        self.titleLabel.setObjectName("titleLabel")
        self.contentLabel.setObjectName("contentLabel")

        setStyleSheet(self, 'state_tool_tip')

        self.titleLabel.adjustSize()
        self.contentLabel.adjustSize()

    def setTitle(self, title: str):
        """ set the _thisTitle of tooltip """
        self.title = title
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def setContent(self, content: str):
        """ set the _thisContent of tooltip """
        self.content = content
        self.contentLabel.setText(content)

        # adjustSize() will mask spinner getTranslation stuck
        self.contentLabel.adjustSize()

    def setState(self, isDone=False):
        """ set the state of tooltip """
        self.isDone = isDone
        self.update()
        if self.isDone:
            self.closeTimer.start()

    def __onCloseButtonClicked(self):
        """ close button clicked slot """
        self.closedSignal.emit()
        self.hide()

    def __slowlyClose(self):
        """ fade out """
        self.rotateTimer.stop()
        self.animation.setEasingCurve(QEasingCurve.Linear)
        self.animation.setDuration(500)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.finished.connect(self.deleteLater)
        self.animation.start()

    def __rotateTimerFlowSlot(self):
        """ rotate timer time out slot """
        self.rotateAngle = (self.rotateAngle + self.deltaAngle) % 360
        self.update()

    def paintEvent(self, e):
        """ paint state tooltip """
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        if not self.isDone:
            painter.translate(24, 23)
            painter.rotate(self.rotateAngle)
            painter.drawPixmap(
                -int(self.busyImage.width() / 2),
                -int(self.busyImage.height() / 2),
                self.busyImage,
            )
        else:
            painter.drawPixmap(14, 13, self.doneImage.width(),
                               self.doneImage.height(), self.doneImage)


from typing import Union
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
class ToastToolTip(QWidget):
    """ Toast tooltip """
    def __init__(self, title: str, content: str, icon: Union[str,QIcon,QPixmap]=None, duration:float=2.5, parent=None):
        """
        Parameters
        ----------
        title: str
            _thisTitle of tooltip

        content: str
            _thisContent of tooltip

        icon: str
            _thisIcon of toast, can be `completed` or `info`
        duration:
            duration of toast
        parant:
            parentLayout window
        """
        super().__init__(parent)
        self._thisTitle = title
        self._thisContent = content
        if icon is not None:
            self._thisIcon = icon
        else:
            self._thisIcon = f":/qfluentwidgets/images/state_tool_tip/info.png"
        self.duration = duration

        self.titleLabel = QLabel(self._thisTitle, self)
        self.contentLabel = QLabel(self._thisContent, self)
        self.iconLabel = PixmapLabel(self)
        self.closeButton = QToolButton(self)
        self.closeTimer = QTimer(self)
        self.opacityEffect = QGraphicsOpacityEffect(self)
        self.opacityAni = QPropertyAnimation(self.opacityEffect, b"opacity")
        self.slideAni = QPropertyAnimation(self, b'pos')

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setAttribute(Qt.WA_StyledBackground)
        self.closeButton.setFixedSize(QSize(14, 14))
        self.closeButton.setIconSize(QSize(14, 14))
        self.closeTimer.setInterval(self.duration * 1000)
        self.contentLabel.setMinimumWidth(250)

        self.iconLabel.setPixmap(QPixmap(self._thisIcon) if isinstance(self._thisIcon, str) or isinstance(self._thisIcon, QIcon) else self._thisIcon)
        self.iconLabel.adjustSize()
        #self.iconLabel.move(15, 13)

        self.setGraphicsEffect(self.opacityEffect)
        self.opacityEffect.setOpacity(1)

        # connect signal to slot
        self.closeButton.clicked.connect(self.hide)
        self.closeTimer.timeout.connect(self.__fadeOut)

        self.__setQss()
        self.__initLayout()

    def __initLayout(self):
        '''self.setFixedSize(max(self.titleLabel.width(),
                          self.contentLabel.width()) + 90, 64)
        self.titleLabel.move(40, 11)
        self.contentLabel.move(15, 34)
        self.closeButton.move(self.width() - 30, 23)'''
        self.vLayout = QVBoxLayout(self)
        self.hLayout1 = QHBoxLayout()
        self.hLayout2 = QHBoxLayout()
        self.hLayout1.addWidget(self.iconLabel)
        self.hLayout1.addWidget(self.titleLabel)
        self.hLayout1.addWidget(self.closeButton)
        self.hLayout2.addWidget(self.contentLabel)
        self.vLayout.addLayout(self.hLayout1)
        self.vLayout.addLayout(self.hLayout2)

    def __setQss(self):
        """ set style sheet """
        self.titleLabel.setObjectName("titleLabel")
        self.contentLabel.setObjectName("contentLabel")
        self.closeButton.setObjectName("closeButton")
        self.iconLabel.setObjectName("iconLabel")
        #setStyleSheet(self, 'state_tool_tip')
        self.titleLabel.adjustSize()
        self.contentLabel.adjustSize()

    def __fadeOut(self):
        """ fade out """
        self.opacityAni.setDuration(350)
        self.opacityAni.setStartValue(1)
        self.opacityAni.setEndValue(0)
        self.opacityAni.finished.connect(self.deleteLater)
        self.opacityAni.start()

    def getSuitablePos(self):
        """ getTranslation suitable position in main window """
        global _toastCount
        dy = _toastCount*(self.height() + 20)
        pos = QPoint(self.window().width() - self.width() - 30, 63+dy)
        pos += QPoint(0, self.height() + 20)
        return pos

    def showEvent(self, e):
        pos = self.getSuitablePos()
        global _toastCount
        _toastCount += 1
        self.slideAni.setDuration(350)
        self.slideAni.setEasingCurve(QEasingCurve.OutQuad)
        self.slideAni.setStartValue(QPoint(self.window().width(), pos.y()))
        self.slideAni.setEndValue(pos)
        def minusToastCount():
            global _toastCount
            _toastCount -= 1 if _toastCount > 0 else 0
        self.slideAni.finished.connect(minusToastCount)
        self.slideAni.start()
        super().showEvent(e)
        self.closeTimer.start()

    def adjustSize(self) -> None:
        self.titleLabel.adjustSize()
        self.contentLabel.adjustSize()
        self.closeButton.adjustSize()
        self.iconLabel.adjustSize()
        super().adjustSize()

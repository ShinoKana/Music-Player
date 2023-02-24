# coding: utf-8
from enum import Enum

from PySide2.QtCore import Qt, QTimer, Property, Signal
from PySide2.QtGui import QColor, QPainter
from PySide2.QtWidgets import QHBoxLayout, QLabel, QToolButton, QWidget
from ...common.style_sheet import setStyleSheet

class Indicator(QToolButton):
    """ Indicator of switch button """

    #checkedChanged = pyqtSignal(bool)
    checkedChanged = Signal(bool)
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setCheckable(True)
        super().setChecked(False)
        self.resize(50, 26)
        self.__sliderOnColor = QColor(Qt.white)
        self.__sliderOffColor = QColor(Qt.black)
        self.__sliderDisabledColor = QColor(QColor(155, 154, 153))
        self.timer = QTimer(self)
        self.padding = self.height()//4
        self.sliderX = self.padding
        self.sliderRadius = (self.height()-2*self.padding)//2
        self.sliderEndX = self.width()-2*self.sliderRadius
        self.sliderStep = self.width()/50
        self.timer.timeout.connect(self.__updateSliderPos)

    def __updateSliderPos(self):
        """ update slider position """
        if self.isChecked():
            if self.sliderX+self.sliderStep < self.sliderEndX:
                self.sliderX += self.sliderStep
            else:
                self.sliderX = self.sliderEndX
                self.timer.stop()
        else:
            if self.sliderX-self.sliderStep > self.sliderEndX:
                self.sliderX -= self.sliderStep
            else:
                self.sliderX = self.sliderEndX
                self.timer.stop()

        self.style().polish(self)

    def setChecked(self, isChecked: bool):
        """ set checked state """
        if isChecked == self.isChecked():
            return

        super().setChecked(isChecked)
        self.sliderEndX = self.width()-2*self.sliderRadius - \
            self.padding if self.isChecked() else self.padding
        self.timer.start(5)

    def mouseReleaseEvent(self, e):
        """ toggle checked state when mouse release"""
        super().mouseReleaseEvent(e)
        self.sliderEndX = self.width()-2*self.sliderRadius - \
            self.padding if self.isChecked() else self.padding
        self.timer.start(5)
        self.checkedChanged.emit(self.isChecked())

    def resizeEvent(self, e):
        self.padding = self.height()//4
        self.sliderRadius = (self.height()-2*self.padding)//2
        self.sliderStep = self.width()/50
        self.sliderEndX = self.width()-2*self.sliderRadius - \
            self.padding if self.isChecked() else self.padding
        self.update()

    def paintEvent(self, e):
        """ paint indicator """
        # the background and border are specified by qss
        super().paintEvent(e)

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        if self.isEnabled():
            color = self.sliderOnColor if self.isChecked() else self.sliderOffColor
        else:
            color = self.sliderDisabledColor

        painter.setBrush(color)
        painter.drawEllipse(self.sliderX, self.padding,
                            self.sliderRadius*2, self.sliderRadius*2)

    def getSliderOnColor(self):
        return self.__sliderOnColor

    def setSliderOnColor(self, color: QColor):
        self.__sliderOnColor = color
        self.update()

    def getSliderOffColor(self):
        return self.__sliderOffColor

    def setSliderOffColor(self, color: QColor):
        self.__sliderOffColor = color
        self.update()

    def getSliderDisabledColor(self):
        return self.__sliderDisabledColor

    def setSliderDisabledColor(self, color: QColor):
        self.__sliderDisabledColor = color
        self.update()

    #sliderOnColor = pyqtProperty(QColor, getSliderOnColor, setSliderOnColor)
    sliderOnColor = Property(QColor, getSliderOnColor, setSliderOnColor)
    #sliderOffColor = pyqtProperty(QColor, getSliderOffColor, setSliderOffColor)
    sliderOffColor = Property(QColor, getSliderOffColor, setSliderOffColor)
    #sliderDisabledColor = pyqtProperty(QColor, getSliderDisabledColor, setSliderDisabledColor)
    sliderDisabledColor = Property(QColor, getSliderDisabledColor, setSliderDisabledColor)

class IndicatorPosition(Enum):
    """ Indicator position """
    LEFT = 0
    RIGHT = 1


class SwitchButton(QWidget):
    """ Switch button class """

    checkedChanged = Signal(bool)
    def __init__(self, text='Off', parent=None, indicatorPos=IndicatorPosition.LEFT):
        """
        Parameters
        ----------
        text: str
            the text of switch button

        parent: QWidget
            parentLayout widget

        indicatorPosition: IndicatorPosition
            the position of indicator
        """
        super().__init__(parent=parent)
        self.text = text
        self.__spacing = 15
        self.indicatorPos = indicatorPos
        self.hBox = QHBoxLayout(self)
        self.indicator = Indicator(self)
        self.label = QLabel(text, self)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setAttribute(Qt.WA_StyledBackground)

        # set layout
        self.hBox.setSpacing(self.__spacing)
        self.hBox.setContentsMargins(0, 0, 0, 0)

        if self.indicatorPos == IndicatorPosition.LEFT:
            self.hBox.addWidget(self.indicator)
            self.hBox.addWidget(self.label)
            self.hBox.setAlignment(Qt.AlignLeft)
        else:
            self.hBox.addWidget(self.label, 0, Qt.AlignRight)
            self.hBox.addWidget(self.indicator, 0, Qt.AlignRight)
            self.hBox.setAlignment(Qt.AlignRight)

        # set default style sheet
        setStyleSheet(self, 'switch_button')

        # connect signal to slot
        self.indicator.checkedChanged.connect(self.checkedChanged)

    def isChecked(self):
        return self.indicator.isChecked()

    def setChecked(self, isChecked: bool):
        """ set checked state """
        self.adjustSize()
        self.indicator.setChecked(isChecked)

    def toggleChecked(self):
        """ toggle checked state """
        self.indicator.setChecked(not self.indicator.isChecked())

    def setText(self, text: str):
        self.text = text
        self.label.setText(text)
        self.adjustSize()

    def getSpacing(self):
        return self.__spacing

    def setSpacing(self, spacing: int):
        self.__spacing = spacing
        self.hBox.setSpacing(spacing)
        self.update()

    spacing = Property(int, getSpacing, setSpacing)
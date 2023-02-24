# coding:utf-8
from typing import List

'''from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout'''
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout
from ...common.style_sheet import setStyleSheet
from ..layout.expand_layout import ExpandLayout


class SettingCardGroup(QWidget):
    """ Setting card group """

    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)
        self.titleLabel = QLabel(title, self)
        self.vBoxLayout = QVBoxLayout(self)
        self.cardLayout = ExpandLayout()

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setSpacing(0)
        self.cardLayout.setContentsMargins(0, 0, 0, 0)
        self.cardLayout.setSpacing(6)

        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addSpacing(15)
        self.vBoxLayout.addLayout(self.cardLayout, 1)

        setStyleSheet(self, 'setting_card_group')
        self.titleLabel.adjustSize()

    def addSettingCard(self, card: QWidget):
        """ add setting card to group """
        card.setParent(self)
        self.cardLayout.addWidget(card)
        self.adjustSize()

    def addSettingCards(self, cards: List[QWidget]):
        """ add setting cards to group """
        for card in cards:
            self.addSettingCard(card)

    def adjustSize(self):
        h = self.cardLayout.heightForWidth(self.width()) + 52
        return self.resize(self.width(), h)

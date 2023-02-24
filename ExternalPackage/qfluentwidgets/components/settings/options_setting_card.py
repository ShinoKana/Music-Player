# coding:utf-8
from typing import List

from PySide2.QtCore import Signal
from PySide2.QtWidgets import QButtonGroup, QLabel, QRadioButton

from ...common.config import OptionsConfigItem, qconfig
from .expand_setting_card import ExpandSettingCard


class OptionsSettingCard(ExpandSettingCard):
    """ setting card with a group of options """

    optionChanged = Signal(OptionsConfigItem)

    def __init__(self, configItem: OptionsConfigItem, iconPath: str, title: str, content: str = None,
                 texts: List[str] = None, parent=None):
        """
        Parameters
        ----------
        configItem: OptionsConfigItem
            options config item

        iconPath: str
            icon path

        title: str
            the title of setting card

        content: str
            the content of setting card

        texts: List[str]
            the texts of radio buttons

        parent: QWidget
            parentLayout window
        """
        super().__init__(iconPath, title, content, parent)
        self.texts = texts or []
        self.configItem = configItem
        self.configName = configItem.name
        self.choiceLabel = QLabel(self)
        self.buttonGroup = QButtonGroup(self)

        self.addWidget(self.choiceLabel)

        # create buttons
        self.viewLayout.setSpacing(24)
        self.viewLayout.setContentsMargins(60, 22, 0, 22)
        for text, option in zip(texts, configItem.options):
            button = QRadioButton(text, self.view)
            self.buttonGroup.addButton(button)
            self.viewLayout.addWidget(button)
            button.setProperty(self.configName, option)

        self._adjustViewSize()
        self.setSelected(qconfig.get(self.configItem))
        self.buttonGroup.buttonClicked.connect(self.__onButtonClicked)

    def __onButtonClicked(self, button: QRadioButton):
        """ button clicked slot """
        if button.text() == self.choiceLabel.text():
            return

        value = button.property(self.configName)
        qconfig.set(self.configItem, value)

        self.choiceLabel.setText(button.text())
        self.choiceLabel.adjustSize()
        self.optionChanged.emit(self.configItem)

    def setSelected(self, value):
        """ select button according to the value """
        for button in self.viewLayout.widgets:
            isChecked = button.property(self.configName) == value
            button.setChecked(isChecked)
            if isChecked:
                self.choiceLabel.setText(button.text())
                self.choiceLabel.adjustSize()

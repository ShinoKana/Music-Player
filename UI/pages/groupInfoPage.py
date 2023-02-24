from Core.DataType import AutoTranslateWord
from .AppPage import AppPage
from components.AppTextLabel import AppTextLabel
from typing import Union
from PySide2.QtWidgets import QFrame, QLayout, QLabel, QGridLayout

class GroupInfoPage(AppPage):
    def __init__(self, appWindow, parent: Union[QFrame, QLayout] = None):
        super().__init__(appWindow=appWindow, parent=parent, titleText=AutoTranslateWord("groupInfo"))
  
        groupInfoLayout = QGridLayout(self)
        groupInfoLayout.addWidget(AppTextLabel(text='CHAN Tai Ming 1155159003'), 1, 0)
        groupInfoLayout.addWidget(AppTextLabel(text='DAI Ruyi 1155173812'), 2, 0)
        groupInfoLayout.addWidget(AppTextLabel(text='NING Chenyu 1155177065'), 3, 0)
        groupInfoLayout.addWidget(AppTextLabel(text='YUE Haoyuan 1155157271'), 4, 0)

    def onSwitchIn(self):
        pass

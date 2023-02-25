from Core.DataType import AutoTranslateWord
from Core import appManager
from .AppPage import AppPage
from components import AppCardButton, AppHyperlinkCard
from typing import Union
from PySide2.QtWidgets import QFrame, QLayout, QVBoxLayout

class GroupInfoPage(AppPage):
    def __init__(self, appWindow, parent: Union[QFrame, QLayout] = None):
        super().__init__(appWindow=appWindow, parent=parent, titleText=AutoTranslateWord("groupInfo"))
  
        groupInfoLayout = QVBoxLayout()
        groupInfoLayout.setContentsMargins(5,5,5,5)
        groupInfoLayout.setSpacing(5)
        groupInfoLayout.addWidget(AppCardButton(title='CHAN Tai Ming 1155159003', height=100,
                                                text="Computer Science - Year3"))
        groupInfoLayout.addWidget(AppCardButton(title='DAI Ruyi 1155173812', height=100))
        groupInfoLayout.addWidget(AppCardButton(title='NING Chenyu 1155177065', height=100))
        groupInfoLayout.addWidget(AppCardButton(title='YUE Haoyuan 1155157271', height=100))

        self.addComponent(groupInfoLayout)

        self.addSpace(20)
        self.addComponent(AppHyperlinkCard(title=AutoTranslateWord("github repo"),
                                           url="https://github.com/ShinoKana/Music-Player",
                                           iconPath=appManager.getDefaultUIIconPath('Link'),
                                           text=AutoTranslateWord("click to open"),
                                           content=AutoTranslateWord("Check out our github repo!")))

    def onSwitchIn(self):
        pass

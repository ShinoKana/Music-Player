from Core.DataType import AutoTranslateWord
from Core import appManager
from .AppPage import AppPage
from components import AppCardButton, AppHyperlinkCard
from typing import Union
from PySide2.QtWidgets import QFrame, QLayout, QVBoxLayout
import Core

class GroupInfoPage(AppPage):
    def __init__(self, appWindow, parent: Union[QFrame, QLayout] = None):
        super().__init__(appWindow=appWindow, parent=parent, titleText=AutoTranslateWord("groupInfo"))
  
        groupInfoLayout = QVBoxLayout()
        groupInfoLayout.setContentsMargins(5,5,5,5)
        groupInfoLayout.setSpacing(5)

        card1 = AppCardButton(title='NING Chenyu 1155177065', height=120, text="Computer Science - Year3",
                              icon=appManager.getUIImagePath("ncy_icon.png"))
        card3 = AppCardButton(title='CHAN Tai Ming 1155159003', height=120, text="Computer Science - Year3",
                              icon=appManager.getUIImagePath("ctm_icon.png"))
        card4 = AppCardButton(title='DAI Ruyi 1155173812', height=120, text="Artificial Intelligence - Year2",
                              icon=appManager.getUIImagePath("dry_icon.png"))
        groupInfoLayout.addWidget(card1)
        groupInfoLayout.addWidget(card3)
        groupInfoLayout.addWidget(card4)
        self.addComponent(groupInfoLayout)

        self.addSpace(20)
        self.addComponent(AppHyperlinkCard(title=AutoTranslateWord("github repo"),
                                           url="https://github.com/ShinoKana/Music-Player",
                                           iconPath=appManager.getDefaultUIIconPath(Core.Default_UI_Icon.Link),
                                           text=AutoTranslateWord("click to open"),
                                           content=AutoTranslateWord("Check out our github repo!")))

    def onSwitchIn(self):
        pass
    def onSwitchOut(self):
        pass

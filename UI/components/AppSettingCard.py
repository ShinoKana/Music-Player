from ExternalPackage import SettingCard, ExpandSettingCard
import re
from Core import appManager
from PySide2.QtGui import QColor

#region change card init
settingCardOriginInit = SettingCard.__init__
def __settingCarNewInit(self, *args, **kwargs):
    settingCardOriginInit(self, *args, **kwargs)
    styleSheetStr = str(self.styleSheet())
    styleSheetStr = re.search(re.compile('(SettingCard \\{.+?\\})(.+)',re.S),styleSheetStr)
    settingCardStr = styleSheetStr.group(1)
    remainingStr = styleSheetStr.group(2)
    newBG = appManager.config.currentComponentColor()
    newBG = QColor(newBG).name()
    replaceWords = re.search(r'(background-color:.+?;)', settingCardStr).groups()[0]
    settingCardStr = settingCardStr.replace(replaceWords, f'background-color: {newBG};')
    settingCardStr = settingCardStr + remainingStr
    self.setStyleSheet(settingCardStr)
SettingCard.__init__ = __settingCarNewInit

expandSettingCardOriginInit = ExpandSettingCard.__init__
def __expandSettingCardNewInit(self, *args, **kwargs):
    expandSettingCardOriginInit(self, *args, **kwargs)
    styleSheetStr = str(self.card.styleSheet())
    newBG = appManager.config.currentComponentColor()
    newBG = QColor(newBG).name()
    frontPart, middlePart, endPart = re.search(re.compile(r'(.+?)(ExpandSettingCard\[isExpand=false\]>SettingCard \{.+?\})(.+)',re.S),styleSheetStr).groups()
    replaceWords = re.search(re.compile('(background-color: .+);', re.S), middlePart).groups()[0]
    middlePart = middlePart.replace(replaceWords, f'background-color: {newBG};')
    styleSheetStr = frontPart + middlePart + endPart

    frontPart, middlePart, endPart = re.search(re.compile(r'(.+?)(ExpandSettingCard\[isExpand=true\]>SettingCard \{.+?\})(.+)',re.S),styleSheetStr).groups()
    replaceWords = re.search(re.compile('(background-color: .+);', re.S), middlePart).groups()[0]
    middlePart = middlePart.replace(replaceWords, f'background-color: {newBG};')
    styleSheetStr = frontPart + middlePart + endPart

    middlePart, endPart = re.search(re.compile('(ExpandSettingCard \\{.+?\\})(.+)',re.S),styleSheetStr).groups()
    replaceWords = re.search(re.compile('(background-color: .+);',re.S),middlePart).groups()[0]
    middlePart = middlePart.replace(replaceWords,f'background-color: {newBG};')
    styleSheetStr = middlePart + endPart

    self.card.setStyleSheet(styleSheetStr)
ExpandSettingCard.__init__ = __expandSettingCardNewInit
#endregion

from ExternalPackage import (SettingCardGroup, SwitchSettingCard, RangeSettingCard, PrimaryPushSettingCard,
                             HyperlinkCard, ColorSettingCard, OptionsSettingCard, FolderListSettingCard)

AppSettingCardGroup = SettingCardGroup
AppSwitchSettingCard = SwitchSettingCard
AppRangeSettingCard = RangeSettingCard
AppButtonSettingCard = PrimaryPushSettingCard
AppHyperlinkCard = HyperlinkCard
AppColorSettingCard = ColorSettingCard
AppOptionsSettingCard = OptionsSettingCard
AppFolderListSettingCard = FolderListSettingCard


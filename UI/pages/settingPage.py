from PySide2.QtCore import Signal
from PySide2.QtWidgets import QLayout, QFrame
from components import (AppSettingCardGroup, AppSwitchSettingCard,
                        AppButtonSettingCard, AppColorSettingCard, AppOptionsSettingCard)
from Core.DataType import AutoTranslateWord, AutoTranslateWordList
from Core import appManager
from .AppPage import AppPage
import time
from typing import Union

class SettingPage(AppPage):
    """ Setting interface """

    themeModeChangedSig = Signal(str)
    languageChanged = Signal(str)
    changeNavigationBarSig = Signal()

    def __init__(self, appWindow:'AppWindow', parent: Union[QFrame, QLayout] = None):
        super().__init__(appWindow=appWindow, parent=parent, titleText=AutoTranslateWord("settings"))
        appManager.config.appRestartSig.connect(self.__showRestartTooltip)

        # region System setting
        self.systemGroup = AppSettingCardGroup(AutoTranslateWord("System"), self.scrollWidget)
        self.themeCard = AppOptionsSettingCard(iconPath=appManager.getDefaultUIIconPath("Brush"),
                                            configItem=appManager.config.themeModeConfig,
                                            title=AutoTranslateWord("Theme"),
                                            content=AutoTranslateWord("app color theme"),
                                            texts=AutoTranslateWordList('Light', 'Dark', 'Use system setting'),
                                            parent=self.systemGroup)
        self.componentLightColorCard = AppColorSettingCard(iconPath=appManager.getDefaultUIIconPath('Palette'),
                                                        title=AutoTranslateWord("Component (Light Mode) Color"),
                                                        content=AutoTranslateWord("Set the color of component when app is in light mode"),
                                                        parent=self.systemGroup,
                                                        configItem=appManager.config.componentLightColorConfig)
        self.componentDarkColorCard = AppColorSettingCard(iconPath=appManager.getDefaultUIIconPath('Palette'),
                                                       title=AutoTranslateWord("Component (Dark Mode) Color"),
                                                       content=AutoTranslateWord("Set the color of component bar when app is in dark mode"),
                                                       parent=self.systemGroup,
                                                       configItem=appManager.config.componentDarkColorConfig)
        self.languageCard = AppOptionsSettingCard(iconPath=appManager.getUIImagePath("language.png"),
                                               configItem=appManager.config.languageConfig,
                                               title=AutoTranslateWord("Language"),
                                               content=AutoTranslateWord("app language"),
                                               texts=AutoTranslateWordList(appManager.config.languages),
                                               parent=self.systemGroup)
        self.languageCard.optionChanged.connect(self.__changeLanguage)
        self.startOnBootCard = AppSwitchSettingCard(iconPath=appManager.getUIImagePath("boot.png"),
                                                 title=AutoTranslateWord("Start on boot"),
                                                 content=AutoTranslateWord("start app on boot"),
                                                 configItem=appManager.config.startOnBootConfig,
                                                 parent=self.systemGroup,
                                                 OnText=AutoTranslateWord("On"),
                                                 OffText=AutoTranslateWord("Off"))
        self.minimizeToTrayCard = AppSwitchSettingCard(iconPath=appManager.getUIImagePath("miniToTray.png"),
                                                    title=AutoTranslateWord("Minimize to tray"),
                                                    content=AutoTranslateWord("minimize app to tray when pressing exit button"),
                                                    configItem=appManager.config.minimizeToTrayConfig,
                                                    parent=self.systemGroup,
                                                    OnText=AutoTranslateWord("On"),
                                                    OffText=AutoTranslateWord("Off"))

        self.systemGroup.addSettingCard(self.themeCard)
        self.systemGroup.addSettingCard(self.componentLightColorCard)
        self.systemGroup.addSettingCard(self.componentDarkColorCard)
        self.systemGroup.addSettingCard(self.languageCard)
        self.systemGroup.addSettingCard(self.startOnBootCard)
        self.systemGroup.addSettingCard(self.minimizeToTrayCard)
        # endregion

        self.addComponent(self.systemGroup)

        #endregion
    def onSwitchIn(self):
        pass
    def __showRestartTooltip(self):
        self.appWindow.toast(title=AutoTranslateWord('Configuration updated successfully').getTranslation(appManager.config.currentLanguage),
            content=AutoTranslateWord('Configuration takes effect after restart').getTranslation(appManager.config.currentLanguage))

    def __changeLanguage(self, optionContent):
        appManager.config.currentLanguage = optionContent.value
        self.__showRestartTooltip()



from PySide2.QtCore import Signal
from PySide2.QtWidgets import QLayout, QFrame
from components import (AppSettingCardGroup, AppSwitchSettingCard,
                        AppButtonSettingCard, AppColorSettingCard, AppOptionsSettingCard)
from Core.DataType import AutoTranslateWord, AutoTranslateWordList
from Core.Managers import appManager
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

        # region personal data setting
        self.personalDataGroup = AppSettingCardGroup(AutoTranslateWord("Personal Data"), self.scrollWidget)
        self.lawyerDataManagementCard = AppButtonSettingCard(iconPath=appManager.getUIImagePath('user.png'),
                                                              title=AutoTranslateWord("Edit lawyer info"),
                                                              content=AutoTranslateWord("Add or edit lawyers' info for fast document edit"),
                                                              parent=self.personalDataGroup,
                                                              text=AutoTranslateWord('Edit'))
        self.lawyerDataManagementCard.clicked.connect(self.__onEditLawyerInfoCardClicked)
        self.personalDataGroup.addSettingCard(self.lawyerDataManagementCard)

        # endregion

        # region document setting
        self.documentGroup = AppSettingCardGroup(AutoTranslateWord("Document"), self.scrollWidget)
        self.wrongGrammarDetectCard = AppSwitchSettingCard(iconPath=appManager.getUIImagePath('grammar.png'),
                                                        title=AutoTranslateWord("Wrong Grammar Detection"),
                                                        content=AutoTranslateWord("Check grammar in documents during editing"),
                                                        configItem=appManager.config.wrongGrammarDetectConfig,
                                                        parent=self.documentGroup,
                                                        OnText=AutoTranslateWord("On"),
                                                        OffText=AutoTranslateWord("Off"))
        self.wrongGrammarColorCard = AppColorSettingCard(iconPath=appManager.getDefaultUIIconPath('Palette'),
                                                      title=AutoTranslateWord("Wrong Grammar Color"),
                                                      content=AutoTranslateWord("Set the color of wrong grammar"),
                                                      parent=self.documentGroup,
                                                      configItem=appManager.config.wrongGrammarColorConfig)
        self.wrongInfoDetectCard = AppSwitchSettingCard(iconPath=appManager.getUIImagePath('i.png'),
                                                     title=AutoTranslateWord("Wrong Info Detection"),
                                                     content=AutoTranslateWord("Check info in documents during editing"),
                                                     configItem=appManager.config.wrongInfoDetectConfig,
                                                     parent=self.documentGroup,
                                                     OnText=AutoTranslateWord("On"),
                                                     OffText=AutoTranslateWord("Off"))
        self.wrongInfoColorCard = AppColorSettingCard(iconPath=appManager.getDefaultUIIconPath('Palette'),
                                                   title=AutoTranslateWord("Wrong Info Color"),
                                                   content=AutoTranslateWord("Set the color of wrong info"),
                                                   parent=self.documentGroup,
                                                   configItem=appManager.config.wrongInfoColorConfig)
        self.autoTagCard = AppSwitchSettingCard(iconPath=appManager.getUIImagePath('tag.png'),
                                              title=AutoTranslateWord("Auto Tag"),
                                              content=AutoTranslateWord("generate auto-suggesred tags when edit/create/upload document."),
                                              parent=self.documentGroup,
                                             configItem=appManager.config.genTagsConfig)
        self.documentGroup.addSettingCard(self.wrongGrammarDetectCard)
        self.documentGroup.addSettingCard(self.wrongGrammarColorCard)
        self.documentGroup.addSettingCard(self.wrongInfoDetectCard)
        self.documentGroup.addSettingCard(self.wrongInfoColorCard)
        self.documentGroup.addSettingCard(self.autoTagCard)
        # endregion

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
        self.autoUpdateCard = AppSwitchSettingCard(iconPath=appManager.getUIImagePath("update.png"),
                                                title=AutoTranslateWord("Auto update"),
                                                content=AutoTranslateWord("auto update app"),
                                                configItem=appManager.config.autoCheckUpdateConfig,
                                                parent=self.systemGroup,
                                                OnText=AutoTranslateWord("On"),
                                                OffText=AutoTranslateWord("Off"))
        if appManager.config.languageConfig.value == 'en':
            copyrightWords = AutoTranslateWord("[current version]:{}   [Copyright] {}, [companyName] [All rights reserved]".format(self.appWindow.VERSION, time.strftime('%Y')))
        else:
            copyrightWords = AutoTranslateWord(
                "[current version]:{}   [Copyright] {}, [companyName]".format(self.appWindow.VERSION,time.strftime('%Y')))
        self.versionCard = AppButtonSettingCard(title=AutoTranslateWord("Version"),
                                                  content=copyrightWords,
                                                  parent=self.systemGroup,
                                                  text=AutoTranslateWord("Check update"),
                                                  iconPath=appManager.getUIImagePath("version.png"))
        self.systemGroup.addSettingCard(self.themeCard)
        self.systemGroup.addSettingCard(self.componentLightColorCard)
        self.systemGroup.addSettingCard(self.componentDarkColorCard)
        self.systemGroup.addSettingCard(self.languageCard)
        self.systemGroup.addSettingCard(self.startOnBootCard)
        self.systemGroup.addSettingCard(self.minimizeToTrayCard)
        self.systemGroup.addSettingCard(self.autoUpdateCard)
        self.systemGroup.addSettingCard(self.versionCard)
        # endregion

        #region other setting
        self.otherGroup = AppSettingCardGroup(AutoTranslateWord('Others'), self.scrollWidget)
        self.helpCard = AppButtonSettingCard(
            title=AutoTranslateWord('Seek for support'),
            iconPath=appManager.getDefaultUIIconPath('Help'),
            text=AutoTranslateWord('Help'),
            content=AutoTranslateWord('Send a message for specifying your problem to us'),
            parent=self.otherGroup
        )
        self.helpCard.clicked.connect(self.__onHelpCardClicked)
        self.feedbackCard = AppButtonSettingCard(
            title=AutoTranslateWord('Provide feedback'),
            iconPath=appManager.getDefaultUIIconPath('Feedback'),
            text=AutoTranslateWord('Provide feedback'),
            content=AutoTranslateWord('Help us improve this app by providing feedback'),
            parent=self.otherGroup
        )
        self.feedbackCard.clicked.connect(self.__onFeedbackCardClicked)
        self.otherGroup.addSettingCard(self.helpCard)
        self.otherGroup.addSettingCard(self.feedbackCard)
        #endregion

        self.addComponent(self.personalDataGroup)
        self.addComponent(self.documentGroup)
        self.addComponent(self.systemGroup)
        self.addComponent(self.otherGroup)

        #endregion
    def onSwitchIn(self):
        pass
    def __showRestartTooltip(self):
        self.appWindow.toast(title=AutoTranslateWord('Configuration updated successfully').getTranslation(appManager.config.currentLanguage),
            content=AutoTranslateWord('Configuration takes effect after restart').getTranslation(appManager.config.currentLanguage))
    def __onEditLawyerInfoCardClicked(self):
        from windows import LawyerInfoWindow
        window = LawyerInfoWindow(parentWindow=self.appWindow,QApp=self.appWindow.QApp)
        window.show()

    def __onHelpCardClicked(self):
        #TODO: add help card clicked event
        print('on help card clicked')

    def __onFeedbackCardClicked(self):
        #TODO: add feedback card clicked event
        print('on feedback card clicked')

    def __onCheckUpdateCardClicked(self):
        #TODO: add check update card clicked event
        print('on check update card clicked')

    def __changeLanguage(self, optionContent):
        appManager.config.currentLanguage = optionContent.value
        self.__showRestartTooltip()



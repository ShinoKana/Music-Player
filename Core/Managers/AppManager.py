import os, re
from typing import Dict, List, Literal
from PySide2.QtGui import QColor
from ExternalPackage import (ConfigItem, QConfig, OptionsConfigItem,
                             ColorConfigItem, BoolValidator, qconfig, OptionsValidator)
from pathlib import Path

RESOURCE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..', "Resources")
RESOURCE_IMAGE_PATH = os.path.join(RESOURCE_PATH, "images")
TRANSLATION_DATA_PATH = os.path.join(RESOURCE_PATH,"translation.csv")
APP_SETTING_PATH = os.path.join(RESOURCE_PATH, 'appSetting.json')

DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..', "Data")
DATABASE_PATH = os.path.join(DATA_PATH, "database.db")

Default_Icon_Type = Literal["Web", "Link", "Help", "Font", "Info", "Zoom", "Close", "Movie", "Brush",
                                                    "Music", "Video", "Embed", "Album", "Folder", "Search", "Update", "Palette",
                                                    "Feedback", "Minimize", "Download", "Question", "Alignment", "PencilInk",
                                                    "FolderAdd", "ChevronDown", "FileSearch", "Transparent", "MusicFolder",
                                                    "BackgroundColor", "FluorescentPen"]
from .Manager import *
@Manager
class ConfigManager(QConfig):
    #system
    themeModeConfig = OptionsConfigItem("System", "ThemeMode", "Light", OptionsValidator(["Light", "Dark", "Auto"]), restart=True)
    componentLightColorConfig = ColorConfigItem("System", "ComponentLightColor", QColor(119, 176, 253), restart=True)
    componentDarkColorConfig = ColorConfigItem("System", "ComponentDarkColor", QColor(39, 58, 83), restart=True)
    languageConfig = OptionsConfigItem("System", "Language", "en", OptionsValidator(["en"]))
    startOnBootConfig = ConfigItem("System", "StartOnBoot", False, BoolValidator())
    minimizeToTrayConfig = ConfigItem("System", "MinimizeToTray", True, BoolValidator())

    def __init__(self):
        #translation
        super().__init__()
        self._translationData = {}
        self._languages = []
        self._currentLanguage: int = 0
        with open(TRANSLATION_DATA_PATH, 'r', encoding='utf-8') as translationFile:
            hasGetLanguages = False
            for i, line in enumerate(translationFile.readlines()):
                if line[0] == '\n' or len(line) == 0 or line[0] == '#':
                    continue
                # getTranslation languages
                elif not hasGetLanguages:
                    self._languages = line.strip().split(',')[1:]
                    hasGetLanguages = True
                    continue
                # getTranslation translation data
                else:
                    lst = re.split(r'(?<!\\),', line.strip())
                    # don't care about case of key
                    self._translationData[str(lst[0]).lower().replace(r'\,', ',')] = [s.replace(r'\,', ',') for s in lst[1:]]
        if len(self._languages) == 0:
            raise Exception('No language found')
        self.languageConfig.validator = OptionsValidator(self._languages)
        # setting
        self._cfg = self
        self.file = Path(APP_SETTING_PATH)
        qconfig.load(APP_SETTING_PATH, self)
        self._currentLanguage = self._languages.index(self.languageConfig.value)

    @property
    def languages(self) -> List[str]:
        return self._languages
    @property
    def translationData(self) -> Dict[str, List[str]]:
        return self._translationData
    @property
    def currentLanguage(self) -> str:
        return self._languages[self._currentLanguage]
    @currentLanguage.setter
    def currentLanguage(self, lang: str):
        if lang not in self.languages:
            raise Exception("Language {} not supported".format(lang))
        self._currentLanguage = self.languages.index(lang)
    @property
    def currentLanguageIndex(self) -> int:
        return self._currentLanguage
    def isLightTheme(self)->bool:
        '''use this tp check real theme mode'''
        return self.theme == "light"
    def isDarkTheme(self)->bool:
        '''use this tp check real theme mode'''
        return self.theme == "dark"
    def currentComponentColor(self)->QColor:
        return self.componentLightColorConfig.value if self.isLightTheme() else self.componentDarkColorConfig.value
    def currentComponentColor_DarkerOrLighter(self, value=120)->QColor:
        if self.isLightTheme():
            return self.componentLightColorConfig.value.darker(value)
        else:
            return self.componentDarkColorConfig.value.lighter(value)

@Manager
class AppManager:
    _config:ConfigManager = None
    def __init__(self):
        self._config = ConfigManager()
    @property
    def config(self)->ConfigManager:
        return self._config
    @property
    def RESOURCE_PATH(self):
        '''path to "Resources" file'''
        return RESOURCE_PATH
    @property
    def RESOURCE_IMAGE_PATH(self):
        '''path to "Resources/images" file'''
        return RESOURCE_IMAGE_PATH
    @property
    def TRANSLATION_DATA_PATH(self):
        '''path to "Resources/translation.csv" file'''
        return TRANSLATION_DATA_PATH
    @property
    def APP_SETTING_PATH(self):
        '''path to "Resources/appSetting.json" file'''
        return APP_SETTING_PATH
    @property
    def DATA_PATH(self):
        '''path to "Data" file'''
        return DATA_PATH
    @property
    def DATABASE_PATH(self):
        '''path to "Data/database.db" file'''
        return DATABASE_PATH
    @property
    def translationData(self)->Dict[str, List[str]]:
        return self.config.translationData
    @property
    def languages(self)->List[str]:
        return self.config.languages
    def translate(self, text, targetLanguage:str = None) -> str:
        if targetLanguage is not None and targetLanguage not in self.config.languages:
            raise Exception("Translation fail. Language {} not supported".format(targetLanguage))
        matches = re.findall(r'(?<!\\)(\[.*?(?<!\\)\])', text)
        if len(matches) == 0:
            #single translation key
            try:
                return self.translationData[str(text).lower()][self.config.currentLanguageIndex if targetLanguage is None else self.languages.index(targetLanguage)]
            except KeyError:
                return text
        else:
            #combination word
            realText = text
            for match in matches:
                translation = self.translationData.get(match[1:-1].lower(), [match[1:-1]]*len(self.languages))[self.config.currentLanguageIndex if targetLanguage is None else self.languages.index(targetLanguage)]
                realText = realText.replace(match, translation)
            realText = realText.replace(r'\[', '[').replace(r'\]', ']')
            return realText
    def getDefaultUIIconPath(self, iconType:Default_Icon_Type ):
        '''icon resources included in external package \'qfluentwidgets\' '''
        iconColor = "white" if not self.config.isLightTheme() else "black"
        return f':/qfluentwidgets/images/setting_card/{iconType}_{iconColor}.png'
    def getUIImagePath(self, fileName: str):
        imgPath = os.path.join(RESOURCE_IMAGE_PATH, fileName)
        if not os.path.exists(imgPath):
            print(f"Image file not found: {imgPath}")
            return None
        return imgPath

appManager = AppManager()
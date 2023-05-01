# -*- coding:utf-8 -*-
import os, re, json, uuid, sys
from enum import Enum
from typing import Dict, List, Union
from pathlib import Path
from PySide2.QtGui import QColor
from PySide2.QtCore import QObject
from ExternalPackage.qfluentwidgets.common import (ConfigValidator, OptionsConfigItem, OptionsValidator, ColorConfigItem, BoolValidator,
                            ConfigItem, ConfigSerializer, ColorValidator, exceptionHandler, ColorSerializer,
                            RangeValidator, QConfig, qconfig)

#path
def _getPathBytes(path:Union[str, bytes, Path])->bytes:
    encode = sys.getdefaultencoding()
    if isinstance(path, str):
        _path = path.encode(encode)
    elif isinstance(path, bytes):
        _path = path
    elif isinstance(path, Path):
        _path = path.as_posix().encode(encode)
    else:
        raise TypeError(f'path must be str, bytes or Path, not {type(path)}')
    return _path

_RESOURCE_PATH_str = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..','..', "Resources")
RESOURCE_PATH = _getPathBytes(_RESOURCE_PATH_str)
RESOURCE_IMAGE_PATH = _getPathBytes(os.path.join(_RESOURCE_PATH_str, "images"))
TRANSLATION_DATA_PATH = _getPathBytes(os.path.join(_RESOURCE_PATH_str, "translation.csv"))
APP_SETTING_PATH = _getPathBytes(os.path.join(_RESOURCE_PATH_str, 'appSetting.json'))
APP_RECORD_PATH = _getPathBytes(os.path.join(_RESOURCE_PATH_str, 'appRecord.json'))
APP_TEMP_RECORD_PATH = _getPathBytes(os.path.join(_RESOURCE_PATH_str, 'appTempRecord.json'))

_DATA_PATH_str = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', "Data")
DATA_PATH = _getPathBytes(_DATA_PATH_str)
DATABASE_PATH = _getPathBytes(os.path.join(_DATA_PATH_str, "database.db"))

#config
class NumberValidator(ConfigValidator):
    def validate(self, value):
        return isinstance(value, int) or isinstance(value, float)
    def correct(self, value):
        return value if self.validate(value) else 0

from .Manager import *
class ConfigManager(QConfig, Manager):
    #system
    themeModeConfig = OptionsConfigItem("System", "ThemeMode", "Light", OptionsValidator(["Light", "Dark", "Auto"]), restart=True)
    componentLightColorConfig = ColorConfigItem("System", "ComponentLightColor", QColor(119, 176, 253), restart=True)
    componentDarkColorConfig = ColorConfigItem("System", "ComponentDarkColor", QColor(39, 58, 83), restart=True)
    languageConfig = OptionsConfigItem("System", "Language", "en", OptionsValidator(["en"]))
    startOnBootConfig = ConfigItem("System", "StartOnBoot", False, BoolValidator())
    minimizeToTrayConfig = ConfigItem("System", "MinimizeToTray", True, BoolValidator())

    def __init__(self):
        #translation
        QConfig.__init__(self)
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
        self.file = Path(APP_SETTING_PATH.decode(sys.getdefaultencoding()))
        qconfig.load(APP_SETTING_PATH, self)
        self._currentLanguage = self._languages.index(self.languageConfig.value)
        for name in dir(self.__class__):
            value = getattr(self.__class__, name)
            if isinstance(value, ConfigItem):
                value.onValueChanged.append(lambda *args: self.save())

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

#record
AppRecordValidator = ConfigValidator
AppRecordSerializer = ConfigSerializer
class RecordItem:
    onValueChanged = []
    def __init__(self, group: str, name: str, default, validator: AppRecordValidator = None,
                 serializer: AppRecordSerializer = None):
        self.group = group
        self.name = name
        self.validator = validator or AppRecordValidator()
        self.serializer = serializer or AppRecordSerializer()
        self.__value = default
        self.value = default
    @property
    def value(self):
        return self.__value
    @value.setter
    def value(self, v):
        self.__value = self.validator.correct(v)
        for callback in self.onValueChanged:
            callback(self.__value)
    @property
    def key(self):
        return self.group+"."+self.name if self.name else self.group
    def __str__(self) -> str:
        return f'{self.__class__.__name__}[value={self.value}]'
    def serialize(self):
        return self.serializer.serialize(self.value)
    def deserializeFrom(self, value):
        self.value = self.serializer.deserialize(value)
class RangeRecordItem(RecordItem):
    @property
    def range(self):
        """ getTranslation the available range of config """
        return self.validator.range

    def __str__(self) -> str:
        return f'{self.__class__.__name__}[range={self.range}, value={self.value}]'
class OptionsRecordItem(RecordItem):
    @property
    def options(self):
        return self.validator.options

    def __str__(self) -> str:
        return f'{self.__class__.__name__}[options={self.options}, value={self.value}]'
class ColorRecordItem(RecordItem):
    def __init__(self, group: str, name: str, default):
        super().__init__(group, name, QColor(default), ColorValidator(default), ColorSerializer())
    def __str__(self) -> str:
        return f'{self.__class__.__name__}[value={self.value.name()}]'
class AppRecord(QObject):
    """ Record of app """
    def __init__(self, recordPath:Union[str, bytes]):
        super().__init__()
        if isinstance(recordPath, bytes):
            _recordPath = recordPath.decode(sys.getdefaultencoding())
        else:
            _recordPath = recordPath
        self.file = Path(_recordPath)
        for name in dir(self.__class__):
            value = getattr(self.__class__, name)
            if isinstance(value, RecordItem):
                value.onValueChanged.append(lambda *args: self.save())
    def __del__(self):
        self.save()
    def get(self, item: RecordItem):
        return item.value
    def set(self, item: RecordItem, value):
        if item.value == value:
            return
        item.value = value
        self.save()
    def toDict(self, serialize=True):
        """ convert record items to `dict` """
        items = {}
        for name in dir(self.__class__):
            item = getattr(self, name)
            if not isinstance(item, RecordItem):
                continue
            value = item.serialize() if serialize else item.value
            if not items.get(item.group):
                if not item.name:
                    items[item.group] = value
                else:
                    items[item.group] = {}
            if item.name:
                items[item.group][item.name] = value
        return items
    def save(self):
        self.file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.toDict(), f, ensure_ascii=False, indent=4)
    @exceptionHandler()
    def load(self, file=None):
        if isinstance(file, (str, Path)):
            self.file = Path(file)
        try:
            with open(self.file, encoding="utf-8") as f:
                record = json.load(f)
        except:
            record = {}
        items = {}
        for name in dir(self.__class__):
            item = getattr(self.__class__, name)
            if isinstance(item, RecordItem):
                items[item.key] = item
        # update the value of record item
        for k, v in record.items():
            if not isinstance(v, dict) and items.get(k) is not None:
                items[k].deserializeFrom(v)
            elif isinstance(v, dict):
                for key, value in v.items():
                    key = k + "." + key
                    if items.get(key) is not None:
                        items[key].deserializeFrom(value)
class RecordManager(AppRecord, Manager):
    #system
    soundVolume = RangeRecordItem("system", "soundVolume", 100, RangeValidator(0, 100))
    #music
    musicPlayMode = OptionsRecordItem("music", "playMode", "listLoop", OptionsValidator(["listLoop", "random", "loop"]))
    lastSongIndex = RecordItem("music", "lastSongIndex", -1, NumberValidator())
    lastSongList = RecordItem("music", "lastSongList", -1, NumberValidator())
    lastSongTime = RecordItem("music", "lastSongTime", 0, NumberValidator())
    unfoldingSongList = RecordItem("music", "unfoldingSongList", "-1", AppRecordValidator())
    #user data
    userID = RecordItem('user', 'userID', '', AppRecordValidator())
    def __init__(self):
        AppRecord.__init__(self, APP_RECORD_PATH)
        self._temperateRecord = {}
        self.load()
        if self.userID.value is None or self.userID.value == '':
            self.userID.value = str((uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.uuid1()) + str(os.urandom(16))))).replace('-', '')
        print('user:', self.userID.value)
    def __del__(self):
        self.save()
    @exceptionHandler()
    def load(self, file=None):
        super().load(file)
        try:
            with open(APP_TEMP_RECORD_PATH, encoding="utf-8") as f:
                self._temperateRecord = json.load(f)
        except:
            self._temperateRecord = {}
    def save(self):
        super().save()
        with open(APP_TEMP_RECORD_PATH, "w", encoding="utf-8") as f:
            json.dump(self._temperateRecord, f, ensure_ascii=False, indent=4)
    def getTempRecord(self, key, default=None):
        return self._temperateRecord.get(key, default)
    def setTempRecord(self, key, value):
        '''key & value must be json serializable'''
        if self._temperateRecord.get(key) == value:
            return
        #check serializable
        try:
            json.dumps(key)
        except:
            raise ValueError(f"Key {key} is not json serializable")
        try:
            json.dumps(value)
        except:
            raise ValueError(f"Value {value} is not json serializable")
        self._temperateRecord[key] = value
        with open(APP_TEMP_RECORD_PATH, "w", encoding="utf-8") as f:
            json.dump(self._temperateRecord, f, ensure_ascii=False, indent=4)

#app manager
class Default_UI_Icon(Enum):
    Web = "Web"
    Link = "Link"
    Help = "Help"
    Font = "Font"
    Info = "Info"
    Zoom = "Zoom"
    Close = "Close"
    Movie = "Movie"
    Brush = "Brush"
    Music = "Music"
    Video = "Video"
    Embed = "Embed"
    Album = "Album"
    Folder = "Folder"
    Search = "Search"
    Update = "Update"
    Palette = "Palette"
    Feedback = "Feedback"
    Minimize = "Minimize"
    Download = "Download"
    Question = "Question"
    Alignment = "Alignment"
    PencilInk = "Pencil_ink"
    FolderAdd = "Folder_add"
    ChevronDown = "Chevron_down"
    FileSearch = "File_search"
    Transparent = "Transparent"
    MusicFolder = "Music_folder"
    BackgroundColor = "Background_color"
    FluorescentPen = "Fluorescent_pen"
class AppManager(Manager):

    _config:ConfigManager = None
    _record:RecordManager = None
    _mainWindow: 'AppWindow' = None

    _toastsBeforeStart = []
    _loadingMessagesBeforeStart = []

    def __init__(self):
        self._config = ConfigManager()
        self._record = RecordManager()

    def toast(self, title: str = "", content: str = "", duration: float = 4.5, icon: Union[str, 'QIcon', 'QPixmap'] = None):
        '''show a toast'''
        if self.mainWindow is None:
            self._toastsBeforeStart.append((title, content, duration, icon))
            return
        self.mainWindow.toast(title, content, duration, icon)
    def goLoading(self, text=None, closable=True):
        '''show loading page'''
        if self.mainWindow is None:
            self._loadingMessagesBeforeStart.append((text, closable))
            return
        self.mainWindow.goloading(text, closable)

    @property
    def mainWindow(self)->'AppWindow':
        return self._mainWindow
    @mainWindow.setter
    def mainWindow(self, value: 'AppWindow'):
        self._mainWindow = value
        for title, content, duration, icon in self._toastsBeforeStart:
            self.toast(title, content, duration, icon)
        self._toastsBeforeStart.clear()
        for text, closable in self._loadingMessagesBeforeStart:
            self.goLoading(text, closable)
        self._loadingMessagesBeforeStart.clear()

    @property
    def config(self)->ConfigManager:
        return self._config
    @property
    def record(self)->RecordManager:
        return self._record
    @property
    def RESOURCE_PATH(self):
        '''path to "Resources" file'''
        return RESOURCE_PATH.decode(sys.getfilesystemencoding())
    @property
    def RESOURCE_IMAGE_PATH(self):
        '''path to "Resources/images" file'''
        return RESOURCE_IMAGE_PATH.decode(sys.getfilesystemencoding())
    @property
    def TRANSLATION_DATA_PATH(self):
        '''path to "Resources/translation.csv" file'''
        return TRANSLATION_DATA_PATH.decode(sys.getfilesystemencoding())
    @property
    def APP_SETTING_PATH(self):
        '''path to "Resources/appSetting.json" file'''
        return APP_SETTING_PATH.decode(sys.getfilesystemencoding())
    @property
    def APP_RECORD_PATH(self):
        '''path to "Resources/appRecord.json" file'''
        return APP_RECORD_PATH.decode(sys.getfilesystemencoding())
    @property
    def APP_TEMP_RECORD_PATH(self):
        '''path to "Resources/appTempRecord.json" file'''
        return APP_TEMP_RECORD_PATH.decode(sys.getfilesystemencoding())
    @property
    def DATA_PATH(self):
        '''path to "Data" file'''
        return DATA_PATH.decode(sys.getfilesystemencoding())
    @property
    def DATABASE_PATH(self):
        '''path to "Data/database.db" file'''
        return DATABASE_PATH.decode(sys.getfilesystemencoding())

    def translate(self, text, targetLanguage:str = None) -> str:
        if targetLanguage is not None and targetLanguage not in self.config.languages:
            raise Exception("Translation fail. Language {} not supported".format(targetLanguage))
        matches = re.findall(r'(?<!\\)(\[.*?(?<!\\)\])', text)
        if len(matches) == 0:
            #single translation key
            try:
                return self.config.translationData[str(text).lower()][self.config.currentLanguageIndex if targetLanguage is None else self.config.languages.index(targetLanguage)]
            except KeyError:
                return text
        else:
            #combination word
            realText = text
            for match in matches:
                translation = self.config.translationData.get(match[1:-1].lower(), [match[1:-1]]*len(self.config.languages))[self.config.currentLanguageIndex if targetLanguage is None else self.config.languages.index(targetLanguage)]
                realText = realText.replace(match, translation)
            realText = realText.replace(r'\[', '[').replace(r'\]', ']')
            return realText
    def getDefaultUIIconPath(self, icon:Default_UI_Icon ):
        '''icon resources included in external package \'qfluentwidgets\' '''
        iconColor = "white" if not self.config.isLightTheme() else "black"
        return f':/qfluentwidgets/images/setting_card/{icon.value}_{iconColor}.png'
    def getUIImagePath(self, fileName: str):
        imgPath = os.path.join(RESOURCE_IMAGE_PATH.decode(sys.getfilesystemencoding()), fileName)
        if not os.path.exists(imgPath):
            print(f"Image file not found: {imgPath}")
            return None
        return imgPath

appManager = AppManager()
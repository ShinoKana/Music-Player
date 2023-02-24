# coding:utf-8
import json
from enum import Enum
from pathlib import Path
from typing import Iterable, List, Union
import darkdetect
from PySide2.QtCore import QObject, Signal
from PySide2.QtGui import QColor
from .exception_handler import exceptionHandler

class ConfigValidator:
    """ Config validator """

    def validate(self, value) -> bool:
        """ Verify whether the value is legal """
        return True

    def correct(self, value):
        """ correct illegal value """
        return value
class RangeValidator(ConfigValidator):
    """ Range validator """

    def __init__(self, min, max):
        self.min = min
        self.max = max
        self.range = (min, max)

    def validate(self, value) -> bool:
        return self.min <= value <= self.max

    def correct(self, value):
        return min(max(self.min, value), self.max)
class OptionsValidator(ConfigValidator):
    """ Options validator """

    def __init__(self, options: Union[Iterable, Enum]) -> None:
        if not options:
            raise ValueError("The `options` can't be empty.")

        if isinstance(options, Enum):
            options = options._member_map_.values()

        self.options = list(options)

    def validate(self, value) -> bool:
        return value in self.options

    def correct(self, value):
        return value if self.validate(value) else self.options[0]
class BoolValidator(OptionsValidator):
    """ Boolean validator """

    def __init__(self):
        super().__init__([True, False])
class FolderValidator(ConfigValidator):
    """ Folder validator """

    def validate(self, value: str) -> bool:
        return Path(value).exists()

    def correct(self, value: str):
        path = Path(value)
        path.mkdir(exist_ok=True, parents=True)
        return str(path.absolute()).replace("\\", "/")
class FolderListValidator(ConfigValidator):
    """ Folder list validator """

    def validate(self, value: List[str]) -> bool:
        return all(Path(i).exists() for i in value)

    def correct(self, value: List[str]):
        folders = []
        for folder in value:
            path = Path(folder)
            if path.exists():
                folders.append(str(path.absolute()).replace("\\", "/"))

        return folders
class ColorValidator(ConfigValidator):
    """ RGB color validator """

    def __init__(self, default):
        self.default = QColor(default)

    def validate(self, color) -> bool:
        try:
            return QColor(color).isValid()
        except:
            return False

    def correct(self, value):
        return QColor(value) if self.validate(value) else self.default


class ConfigSerializer:
    """ Config serializer """

    def serialize(self, value):
        """ serialize config value """
        return value

    def deserialize(self, value):
        """ deserialize config from config file's value """
        return value
class EnumSerializer(ConfigSerializer):
    """ enumeration class serializer """

    def __init__(self, enumClass):
        self.enumClass = enumClass

    def serialize(self, value: Enum):
        return value.value

    def deserialize(self, value):
        return self.enumClass(value)
class ColorSerializer(ConfigSerializer):
    """ QColor serializer """

    def serialize(self, value: QColor):
        return value.name()

    def deserialize(self, value):
        if isinstance(value, list):
            return QColor(*value)

        return QColor(value)

class ConfigItem:
    """ Config item """

    def __init__(self, group: str, name: str, default, validator: ConfigValidator = None,
                 serializer: ConfigSerializer = None, restart=False):
        """
        Parameters
        ----------
        group: str
            config group name

        name: str
            config item name, can be empty

        default:
            default value

        options: list
            options value

        serializer: ConfigSerializer
            config serializer

        restart: bool
            whether to restart the application after updating value
        """
        self.group = group
        self.name = name
        self.validator = validator or ConfigValidator()
        self.serializer = serializer or ConfigSerializer()
        self.__value = default
        self.value = default
        self.restart = restart

    @property
    def value(self):
        """ getTranslation the value of config item """
        return self.__value

    @value.setter
    def value(self, v):
        self.__value = self.validator.correct(v)

    @property
    def key(self):
        """ getTranslation the config key separated by `.` """
        return self.group+"."+self.name if self.name else self.group

    def __str__(self) -> str:
        return f'{self.__class__.__name__}[value={self.value}]'

    def serialize(self):
        return self.serializer.serialize(self.value)

    def deserializeFrom(self, value):
        self.value = self.serializer.deserialize(value)
class RangeConfigItem(ConfigItem):
    """ Config item of range """

    @property
    def range(self):
        """ getTranslation the available range of config """
        return self.validator.range

    def __str__(self) -> str:
        return f'{self.__class__.__name__}[range={self.range}, value={self.value}]'
class OptionsConfigItem(ConfigItem):
    """ Config item with options """

    @property
    def options(self):
        return self.validator.options

    def __str__(self) -> str:
        return f'{self.__class__.__name__}[options={self.options}, value={self.value}]'
class ColorConfigItem(ConfigItem):
    """ Color config item """

    def __init__(self, group: str, name: str, default, restart=False):
        super().__init__(group, name, QColor(default), ColorValidator(default),
                         ColorSerializer(), restart)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}[value={self.value.name()}]'


class QConfig(QObject):
    """ Config of app """

    appRestartSig = Signal()
    themeModeConfig = OptionsConfigItem("MainWindow", "Theme", "Light", OptionsValidator(["Light", "Dark", "Auto"]))

    def __init__(self):
        super().__init__()
        self.file = Path("config/config.json")
        self._theme = "Light"
        self._cfg = self

    def get(self, item: ConfigItem):
        return item.value

    def set(self, item: ConfigItem, value):
        if item.value == value:
            return

        item.value = value
        self.save()

        if item.restart:
            self._cfg.appRestartSig.emit()

    def toDict(self, serialize=True):
        """ convert config items to `dict` """
        items = {}
        for name in dir(self._cfg.__class__):
            item = getattr(self._cfg.__class__, name)
            if not isinstance(item, ConfigItem):
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
        self._cfg.file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._cfg.file, "w", encoding="utf-8") as f:
            json.dump(self._cfg.toDict(), f, ensure_ascii=False, indent=4)

    @exceptionHandler()
    def load(self, file=None, config=None):
        """ load config
        Parameters
        ----------
        file: str or Path
            the path of json config file

        config: Config
            config object to be initialized
        """
        if isinstance(config, QConfig):
            self._cfg = config

        if isinstance(file, (str, Path)):
            self._cfg.file = Path(file)

        try:
            with open(self._cfg.file, encoding="utf-8") as f:
                cfg = json.load(f)
        except:
            cfg = {}

        # map config items'key to item
        items = {}
        for name in dir(self._cfg.__class__):
            item = getattr(self._cfg.__class__, name)
            if isinstance(item, ConfigItem):
                items[item.key] = item

        # update the value of config item
        for k, v in cfg.items():
            if not isinstance(v, dict) and items.get(k) is not None:
                items[k].deserializeFrom(v)
            elif isinstance(v, dict):
                for key, value in v.items():
                    key = k + "." + key
                    if items.get(key) is not None:
                        items[key].deserializeFrom(value)

        if self.get(self._cfg.themeModeConfig) == "Auto":
            self._cfg._theme = darkdetect.theme() or "Light"
        else:
            self._cfg._theme = self.get(self._cfg.themeModeConfig)

    @property
    def theme(self):
        """ getTranslation theme mode, can be `light` or `dark` """
        return self._cfg._theme.lower()

qconfig = QConfig()

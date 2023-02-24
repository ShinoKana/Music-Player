from typing import List
from Core.Managers import appManager

class AutoTranslateWord(str):
    '''auto translate word'''
    def __new__(cls, s):
        if not hasattr(cls, "_appManager"):
            cls._appManager = __import__("Core").appManager
        if isinstance(s, str):
            return super().__new__(cls, appManager.translate(s))
        else:
            raise Exception("AutoTranslateWord only accept str as input")
    def __init__(self, rawText:str):
        self._rawText = rawText
    @property
    def rawText(self) -> str:
        return self._rawText
    @rawText.setter
    def rawText(self, newText:any):
        raise Exception("Can't change rawText. Raw text could only be set in constructor")
    def getTranslation(self, targetLanguage:str = None) -> str:
        return appManager.translate(self.rawText, targetLanguage)
    def __str__(self):
        return self.getTranslation()
    def __repr__(self):
        return "AutoTranslateWord({})".format(self.rawText)

class AutoTranslateWordList(list):
    '''auto translate word list'''
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)
    def __init__(self, *args):
        if len(args) == 1 and (isinstance(args[0], list) or isinstance(args[0], tuple)):
            super().__init__([appManager.translate(text) for text in args[0]])
        else:
            super().__init__([appManager.translate(text) for text in list(args)])
        self.__rawTextList = list(args)
    @property
    def rawTextList(self) -> List[str]:
        return self.__rawTextList
    @rawTextList.setter
    def rawTextList(self, newTextList:any):
        raise Exception("Can't change rawTextList. Raw text list could only be set in constructor")
    def getTranslations(self, targetLanguage:str = None) -> List[str]:
        return [appManager.translate(text, targetLanguage) for text in self.rawTextList]
    def __repr__(self):
        return "AutoTranslateWordList({})".format(self.rawTextList)

from enum import Enum
from types import DynamicClassAttribute
class AutoTranslateEnum(Enum):
    '''auto translate word enum'''
    @DynamicClassAttribute
    def name(self):
        return appManager.translate(self._name_)
    @DynamicClassAttribute
    def rawName(self):
        return self._name_
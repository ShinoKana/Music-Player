from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import QComboBox, QWidget, QListView, QLabel, QHBoxLayout
from typing import Union, Sequence, List, Callable
from .AppWidget import AppWidget, AppWidgetHintClass
from Core import appManager
from Core.DataType import AutoTranslateWord, AutoTranslateWordList

DropDownHint = Union[AppWidgetHintClass, QComboBox, 'AppDropDown']
class AppDropDown(AppWidget(QComboBox)):
    onChoiceChanged = Signal(str)
    def __init__(self: DropDownHint, choices: Union[AutoTranslateWordList,List[str]] = None,
                 onChoiceChanged:Callable[[str],any]=None, height: int = 40, **kwargs):
        super().__init__(height=height, **kwargs)
        self.setEditable(True)

        #line edit
        self.lineEdit().setReadOnly(True)
        self.lineEdit().setAlignment(Qt.AlignCenter)
        self.lineEdit().setStyleSheet('color:{};'.format('white' if not appManager.config.isLightTheme() else 'black')+
                                      'background-color:{};'.format('white' if appManager.config.isLightTheme() else self.backgroundColor.lighter().name()))
        self.lineEdit().font().setPointSize(int(self.height() * 0.4))

        #view
        view = QListView()
        self.setView(view)
        self.view().setStyleSheet('color:{};'.format('white' if not appManager.config.isLightTheme() else 'black')+
                                 'background-color:{};'.format('white' if appManager.config.isLightTheme() else self.backgroundColor.lighter().name())+
                                  'border-radius:0px;')
        view.font().setPointSize(int(self.height() * 0.35))

        self.__choiceKeys:List[str] = []
        self.__choiceTexts:List[str] = []
        def whenChoiceChanged(text:str):
            self.onChoiceChanged.emit(self.__choiceKeys[self.__choiceTexts.index(text)])
        self.currentTextChanged.connect(whenChoiceChanged)
        if onChoiceChanged:
            self.onChoiceChanged.connect(onChoiceChanged)
        if choices:
            self.AddChoices(choices)
            self.setCurrentIndex(0)
    @property
    def currentChoiceKey(self:DropDownHint):
        return self.__choiceKeys[self.currentIndex()]
    @currentChoiceKey.setter
    def currentChoiceKey(self:DropDownHint, key:str):
        self.SetCurrentChoice_byKey(key)
    @property
    def currentChoiceText(self:DropDownHint):
        return self.__choiceTexts[self.currentIndex()]
    @currentChoiceText.setter
    def currentChoiceText(self:DropDownHint, text:str):
        self.SetCurrentChoice_byText(text)
    def AddChoices(self:DropDownHint, choices: Union[AutoTranslateWordList,Sequence[Union[AutoTranslateWord,str]]]):
        if isinstance(choices, AutoTranslateWordList):
            self.__choiceKeys += choices.rawTextList
            self.__choiceTexts += choices.getTranslations()
            self.addItems(self.__choiceTexts)
        else:
            for choice in choices:
                if isinstance(choice, AutoTranslateWord):
                    self.__choiceKeys.append(choice.rawText)
                    self.__choiceTexts.append(choice.getTranslation())
                    self.addItem(self.__choiceTexts[-1])
                else:
                    self.__choiceKeys.append(choice)
                    self.__choiceTexts.append(choice)
                    self.addItem(choice)
    def AddChoice(self:DropDownHint, choice: Union[AutoTranslateWord,str]):
        if isinstance(choice, AutoTranslateWord):
            self.__choiceKeys.append(choice.rawText)
            self.__choiceTexts.append(choice.getTranslation())
            self.addItem(self.__choiceTexts[-1])
        else:
            self.__choiceKeys.append(choice)
            self.__choiceTexts.append(choice)
            self.addItem(choice)
    def RemoveChoice(self:DropDownHint, choice: Union[AutoTranslateWord,str]):
        if isinstance(choice, AutoTranslateWord):
            self.removeItem(self.__choiceTexts.index(choice.rawText))
            self.__choiceKeys.remove(choice.rawText)
            self.__choiceTexts.remove(choice.getTranslation())
        else:
            self.removeItem(self.__choiceTexts.index(choice))
            self.__choiceKeys.remove(choice)
            self.__choiceTexts.remove(choice)
    def SetCurrentChoice_byKey(self:DropDownHint, key:str):
        if key in self.__choiceKeys:
            self.setCurrentIndex(self.__choiceKeys.index(key))
    def SetCurrentChoice_byText(self:DropDownHint, text:str):
        if text in self.__choiceTexts:
            self.setCurrentIndex(self.__choiceTexts.index(text))

class AppDropDown_WithLabel(AppWidget(QWidget)):
    def __init__(self: DropDownHint, titleText: Union[str, AutoTranslateWord]="", choices: Union[AutoTranslateWordList,List[str]] = None,
                 titleTextFontSize:int=12, onChoiceChanged:Callable[[str],any]=None, height: int = 40, **kwargs):
        super().__init__(height=height, **kwargs)
        self.__layout = QHBoxLayout(self)
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setSpacing(0)

        self.__titleText = titleText
        self.__titleLabel = QLabel(text=titleText)
        self.__titleLabel.font().setPointSize(titleTextFontSize)

        self.__dropDown = AppDropDown(choices=choices, onChoiceChanged=onChoiceChanged, height=height)
        self.currentChoiceKey = self.__dropDown.currentChoiceKey
        self.currentChoiceText = self.__dropDown.currentChoiceText
        self.AddChoices = self.__dropDown.AddChoices
        self.AddChoice = self.__dropDown.AddChoice
        self.RemoveChoice = self.__dropDown.RemoveChoice
        self.SetCurrentChoice_byKey = self.__dropDown.SetCurrentChoice_byKey
        self.SetCurrentChoice_byText = self.__dropDown.SetCurrentChoice_byText

        self.__layout.addWidget(self.__label, 0, 0)
        self.__layout.addWidget(self.__dropDown, 0, 1)

        self.setLayout(self.__layout)
    @property
    def titleText(self:DropDownHint):
        return self.__titleText
    @titleText.setter
    def titleText(self:DropDownHint, text:Union[str,AutoTranslateWord]):
        self.SetTitleText(text)
    def SetTitleText(self:DropDownHint, text:Union[str,AutoTranslateWord]):
        self.__titleText = text
        self.__titleLabel.setText(text)
    @property
    def titleTextFontSize(self:DropDownHint):
        return self.__titleLabel.font().pointSize()
    @titleTextFontSize.setter
    def titleTextFontSize(self:DropDownHint, size:int):
        self.SetTitleTextFontSize(size)
    def SetTitleTextFontSize(self:DropDownHint, size:int):
        self.__titleLabel.font().setPointSize(size)



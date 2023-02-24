from PySide2.QtGui import QColor
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QHBoxLayout, QWidget
from Core.Managers import appManager
from Core.DataType import AutoTranslateWord, AutoTranslateWordList
from typing import Callable, Union, Sequence
from .AppTextLabel import AppTextLabel
from .AppWidget import AppWidget, AppWidgetHintClass
from .AppButton import AppButton
from .AppInputBar import AppInputBar
from .AppDropDown import AppDropDown

SearchBarClass = Union[AppWidgetHintClass, QWidget, 'AppSearchBar']

class AppSearchBar(AppWidget(QWidget)):
    def __init__(self:SearchBarClass, titleText:str=None, titleTextSize:int=None, searchButtonText:str=None, searchButtonTextSize:int=None,
                 hintText:str=None, hintTextSize:int=None, searchCommand:Callable[[str],any]=None, height:int=40, **kwargs):
        super().__init__(height=height, **kwargs)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(self.size().width()*0.02, height*0.2,
                                           self.size().width()*0.02, height*0.2)
        self.hBoxLayout.setSpacing(int(self.width()*0.02))
        self.hBoxLayout.setAlignment(Qt.AlignCenter)

        self.titleLabel = AppTextLabel(text=titleText, height=int(height * 0.8), fontSize=titleTextSize)
        self.titleText = self.titleLabel.text #copy the text property
        self.SetTitleText = self.titleLabel.SetText #copy the setText method
        self.SetTitleTextSize = self.titleLabel.SetFontSize #copy the setFontSize method
        self.hBoxLayout.addWidget(self.titleLabel)

        self.inputArea = AppInputBar(hintText=hintText, height=int(height * 0.8), parent=self, fontSize=hintTextSize)
        self.hintText = self.inputArea.hintText #copy the hintText property
        self.SetHintText = self.inputArea.SetHintText #copy the setHintText method
        self.SetHintTextSize = self.inputArea.SetFontSize #copy the setFontSize method
        self.hBoxLayout.addWidget(self.inputArea)

        self.searchButton = AppButton(text=searchButtonText, icon=appManager.getUIImagePath('small_search.png'),
                                      height=int(height*0.8), backgroundColor=QColor('white') if appManager.config.isLightTheme() else self.backgroundColor.lighter(),
                                      fontSize=searchButtonTextSize)
        self.searchButtonText = self.searchButton.text #copy the text property
        self.SetSearchButtonText = self.searchButton.SetText #copy the setText method
        self.SetSearchButtonTextSize = self.searchButton.SetFontSize #copy the setFontSize method
        self.hBoxLayout.addWidget(self.searchButton)

        if searchCommand is not None:
            self.searchButton.clicked.connect(lambda:searchCommand(self.inputArea.text()))

        self.hBoxLayout.setStretch(0, 1)
        self.hBoxLayout.setStretch(1, 8)
        self.hBoxLayout.setStretch(2, 1)

        self.adjustSize()

class AppSearchBar_WithDropDown(AppWidget(QWidget)):
    def __init__(self:SearchBarClass, titleText:str=None, titleTextSize:int=12, searchButtonText:str=None, hintText:str=None, hintTextSize:int=12,
                 searchCommand:Callable[[str],any]=None, searchButtonTextSize:int=12, dropdownChoices:Union[AutoTranslateWordList,Sequence[Union[AutoTranslateWord,str]]]=None,
                 onDropdownChanged:Callable[[str],any]=None, height:int=40, **kwargs):
        super().__init__(height=height, **kwargs)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(self.size().width() * 0.02, height * 0.2,
                                           self.size().width() * 0.02, height * 0.2)
        self.hBoxLayout.setSpacing(int(self.width() * 0.02))
        self.hBoxLayout.setAlignment(Qt.AlignCenter)

        self.titleLabel = AppTextLabel(text=titleText, height=int(height * 0.8), fontSize=titleTextSize)
        self.titleText = self.titleLabel.text  # copy the text property
        self.SetTitleText = self.titleLabel.SetText  # copy the setText method
        self.SetTitleTextSize = self.titleLabel.SetFontSize  # copy the setFontSize method
        self.hBoxLayout.addWidget(self.titleLabel)

        self.dropDown = AppDropDown(parent=self, onChoiceChanged=onDropdownChanged, height=int(height * 0.8), choices=dropdownChoices)
        self.currentDropDownChoiceKey = self.dropDown.currentChoiceKey
        self.currentDropDownChoiceText = self.dropDown.currentChoiceText
        self.AddDropDownChoice = self.dropDown.AddChoice
        self.RemoveDropDownChoice = self.dropDown.RemoveChoice
        self.AddDropDownChoices = self.dropDown.AddChoices
        self.SetDropDownChoice_byKey = self.dropDown.SetCurrentChoice_byKey
        self.SetDropDownChoice_byText = self.dropDown.SetCurrentChoice_byText

        self.hBoxLayout.addWidget(self.dropDown)

        self.inputArea = AppInputBar(hintText=hintText, height=int(height * 0.8), parent=self,
                                     fontSize=hintTextSize)
        self.hintText = self.inputArea.hintText  # copy the hintText property
        self.SetHintText = self.inputArea.SetHintText  # copy the setHintText method
        self.SetHintTextSize = self.inputArea.SetFontSize  # copy the setFontSize method
        self.hBoxLayout.addWidget(self.inputArea)

        self.searchButton = AppButton(text=searchButtonText, icon=appManager.getUIImagePath('small_search.png'),
                                      height=int(height * 0.8), fontSize=searchButtonTextSize, backgroundColor=QColor('white') if appManager.config.isLightTheme() else self.backgroundColor.lighter())
        self.searchButtonText = self.searchButton.text  # copy the text property
        self.SetSearchButtonText = self.searchButton.SetText  # copy the setText method
        self.SetSearchButtonTextSize = self.searchButton.SetFontSize  # copy the setFontSize method
        self.hBoxLayout.addWidget(self.searchButton)

        if searchCommand is not None:
            self.searchButton.clicked.connect(lambda: searchCommand(self.inputArea.text()))

        self.hBoxLayout.setStretch(0, 1)
        self.hBoxLayout.setStretch(1, 1)
        self.hBoxLayout.setStretch(2, 7)
        self.hBoxLayout.setStretch(3, 1)

        self.adjustSize()

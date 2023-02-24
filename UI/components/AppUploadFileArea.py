from ExternalPackage.pyqt5Custom import DragDropFile
from .AppWidget import AppWidget, AppWidgetHintClass
from .AppButton import AppButton
from .AppScrollBox import AppScrollBox
from .AppLayoutBox import AppLayoutBox
from Core.DataType import AutoTranslateWord, FileInfo
from Core.Managers import appManager
from typing import Callable, Union, List, Dict, Sequence
from PySide2.QtGui import QColor
from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import QVBoxLayout, QWidget, QFileDialog
import re

UploadFileAreaHint = Union['AppUploadFileArea', AppWidgetHintClass, DragDropFile]
class AppUploadFileArea(AppWidget(DragDropFile)):
    OnClickSignal = Signal()
    def __init__(self: UploadFileAreaHint, hintText:str=None, fontSize=16, onFileAdded:Callable[[FileInfo],any]=None,
                 allowMultiFile:bool=True, fontColor:Union[str,QColor]=None, onClick:Callable[[],any]=None, height:int=225,
                 onlyAcceptFiles:tuple=(), borderCornerRadius=20, clickAddFileHintText:str=None, onFileRemoved:Callable[[FileInfo],any]=None,
                 **kwargs):
        super().__init__(height=height, borderCornerRadius=borderCornerRadius, **kwargs)
        self.__hintText = None
        self.__fontSize = fontSize
        self.__fontColor = fontColor
        self.__allowMultiFile = allowMultiFile
        self.__currentFiles : List[FileInfo] = []
        self.__onFileAdded = []
        self.__onFileRemoved = []
        self.SetForegroundColor = self.SetFontColor
        self.foregroundColor = self.fontColor
        #icon
        self.addIcon.setMaximumSize(self.width()*0.15, self.width()*0.15)
        self.addIcon.setStyleSheet('background-color: transparent;')
        #hint text
        self.title_lbl.setAttribute(Qt.WA_StyledBackground, True)
        self.title_lbl.setStyleSheet('background-color: transparent;'+
                                     'font-size: {}pt;'.format(fontSize)+
                                     'color: {};'.format(QColor(fontColor).name() if fontColor is not None else 'black' if appManager.config.isLightTheme() else 'white'))
        self.adjustSize()

        if hintText:
            self.SetHintText(hintText)
        else:
            self.SetHintText(AutoTranslateWord('Drop files here to upload, or click to select.'))
        if fontColor is not None:
            self.SetFontColor(fontColor)
        else:
            self.SetFontColor('black' if appManager.config.isLightTheme() else 'white')

        def whenAddFile(fileInfo:FileInfo):
            if fileInfo in self.__currentFiles:
                return
            if not self.allowMultiFile:
                for file in self.__currentFiles:
                    self.removeFile(file)
            self.__currentFiles.append(fileInfo)
            if not self.__allowMultiFile and len(self.__currentFiles)>1:
                self.__currentFiles = [self.__currentFiles[-1]]
            for func in self.__onFileAdded:
                func(fileInfo)
        self.fileDropped.connect(whenAddFile)
        self.__onFileAdded.append(onFileAdded) if onFileAdded else None
        self.__onFileRemoved.append(onFileRemoved) if onFileRemoved else None

        clickAddFileHint = clickAddFileHintText if clickAddFileHintText else AutoTranslateWord('Select one or more files to open')
        acceptFiles = ';;'.join([f'{fileType} {AutoTranslateWord("file")} (*.{fileType})' for fileType in onlyAcceptFiles]) if len(onlyAcceptFiles)>0 else 'All Files (*);;'
        def clickToAddFile():
            filepath = QFileDialog.getOpenFileNames(self, clickAddFileHint, '', acceptFiles)
            if len(filepath[0]) > 0:
                for path in filepath[0]:
                    fileInfo = FileInfo(path)
                    self.fileDropped.emit(fileInfo)
        self.OnClickSignal.connect(clickToAddFile)
        self.OnClickSignal.connect(onClick) if onClick else None
        self.mousePressEvent = lambda event: self.OnClickSignal.emit()

        self.adjustSize()

    #region text & font
    @property
    def hintText(self) -> str:
        return self.__hintText
    @hintText.setter
    def hintText(self, hintText: str):
        self.SetHintText(hintText)
    def SetHintText(self: UploadFileAreaHint, hintText: str):
        self.__hintText = hintText
        if hintText is not None:
            self.title_lbl.setText(hintText)
    @property
    def fontSize(self) -> int:
        return self.__fontSize
    @fontSize.setter
    def fontSize(self, fontSize: int):
        self.SetFontSize(fontSize)
    def SetFontSize(self: UploadFileAreaHint, fontSize: int):
        if fontSize is not None:
            self.__fontSize = fontSize
            self.title_lbl.setStyleSheet(self.title_lbl.styleSheet().replace(re.search('(?<!-)font-size:.*pt;', self.title_lbl.styleSheet()).group(), f'font-size: {self.__fontSize}pt;'))
    @property
    def fontColor(self) -> QColor:
        return self.__fontColor
    @fontColor.setter
    def fontColor(self, color: Union[QColor,str]):
        self.SetFontColor(color)
    def SetFontColor(self:UploadFileAreaHint, color: Union[QColor, str]):
        if isinstance(color, str):
            color = QColor(color)
        if color is not None and color != self.__fontColor:
            self.__fontColor = color
            match = re.search('(?<!-)color:.*;', self.title_lbl.styleSheet())
            if match:
                self.title_lbl.setStyleSheet(self.title_lbl.styleSheet().replace(match.group(), f'color: {self.__fontColor.name()};'))
            else:
                self.title_lbl.setStyleSheet(self.title_lbl.styleSheet() + f'color: {self.__fontColor.name()};')
    #endregion
    @property
    def allowMultiFile(self):
        return self.__allowMultiFile
    @property
    def currentFiles(self) -> List[FileInfo]:
        return self.__currentFiles
    def addEvent_onClick(self, func:Callable[[],any]):
        self.OnClickSignal.connect(func)
    def removeEvent_onClick(self, func:Callable[[],any]):
        self.OnClickSignal.disconnect(func)
    def addEvent_onFileAdded(self, func:Callable[[FileInfo],any]):
        self.__onFileAdded.append(func)
    def removeEvent_onFileAdded(self, func:Callable[[FileInfo],any]):
        self.__onFileAdded.remove(func)
    def addEvent_onFileRemoved(self, func:Callable[[FileInfo],any]):
        self.__onFileRemoved.append(func)
    def removeEvent_onFileRemoved(self, func:Callable[[FileInfo],any]):
        self.__onFileRemoved.remove(func)
    def removeFile(self, fileInfo:FileInfo):
        if fileInfo in self.__currentFiles:
            self.__currentFiles.remove(fileInfo)
            for func in self.__onFileRemoved:
                func(fileInfo)



UploadFileArea_WithFileBox_Hint = Union['AppUploadFileArea_WithFileBox', AppWidgetHintClass, QWidget]
class AppUploadFileArea_WithFileBox(AppWidget(QWidget)):
    def __init__(self: UploadFileArea_WithFileBox_Hint, hintText:str=None, fontSize=16, onFileAdded:Callable[[FileInfo],any]=None,
                 allowMultiFile:bool=True, fontColor:Union[str,QColor]=None, onClick:Callable[[],any]=None, height:int=225,
                 onlyAcceptFiles:tuple=(), clickAddFileHintText:str=None, fileListBoxTitleText:str=None, uploadButtonCommand:Callable[[Sequence[FileInfo]],any]=None,
                 borderCornerRadius=20, onFileRemoved:Callable[[FileInfo],any]=None, **kwargs):
        super().__init__(height=height, borderCornerRadius=borderCornerRadius, **kwargs)
        self.__currentFileBoxes:Dict[str, AppLayoutBox] = {}
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(8, 10, 8, 10)
        self.vBoxLayout.setSpacing(3)

        #upload file area
        self.uploadFileArea:UploadFileAreaHint = AppUploadFileArea(hintText=hintText, onFileAdded=onFileAdded, fontSize=fontSize,
                                                                   allowMultiFile=allowMultiFile, height=height, onClick=onClick,
                                                                   fontColor=fontColor, onlyAcceptFiles=onlyAcceptFiles, clickAddFileHintText=clickAddFileHintText,
                                                                   borderCornerRadius=borderCornerRadius)
        self.vBoxLayout.addWidget(self.uploadFileArea)
        self.hintText = self.uploadFileArea.hintText
        self.SetHintText = self.uploadFileArea.SetHintText
        self.hintTextSize = self.uploadFileArea.fontSize
        self.SetHintTextSize = self.uploadFileArea.SetFontSize
        self.hintTextColor = self.uploadFileArea.fontColor
        self.SetHintTextColor = self.uploadFileArea.SetFontColor

        self.allowMultiFile = self.uploadFileArea.allowMultiFile
        self.currentFiles = self.uploadFileArea.currentFiles
        self.addEvent_onClick = self.uploadFileArea.addEvent_onClick
        self.removeEvent_onClick = self.uploadFileArea.removeEvent_onClick
        self.addEvent_onFileAdded = self.uploadFileArea.addEvent_onFileAdded
        self.removeEvent_onFileAdded = self.uploadFileArea.removeEvent_onFileAdded
        originRemoveFileMethod = self.uploadFileArea.removeFile
        def removeFileBoxFromListBox(fileInfo:FileInfo):
            if fileInfo.filePath in self.__currentFileBoxes.keys():
                self.fileListBox.removeComponent(self.__currentFileBoxes[fileInfo.filePath])
                self.__currentFileBoxes[fileInfo.filePath].deleteLater()
                self.__currentFileBoxes.pop(fileInfo.filePath)
            if len(self.__currentFileBoxes) == 0:
                self.fileListBox.hide()
                self.uploadButton.hide()
                self.resize(self.width(), self.uploadFileArea.height() + 20)
        def removeFile(fileInfo:FileInfo):
            '''override the function in AppUploadFileArea'''
            if fileInfo in self.currentFiles:
                originRemoveFileMethod(fileInfo)
                removeFileBoxFromListBox(fileInfo)
        self.uploadFileArea.removeFile = removeFile
        self.removeFile = self.uploadFileArea.removeFile
        self.addEvent_onFileRemoved = self.uploadFileArea.addEvent_onFileRemoved
        self.removeEvent_onFileRemoved = self.uploadFileArea.removeEvent_onFileRemoved
        self.addEvent_onFileRemoved(onFileRemoved) if onFileRemoved is not None else None
        def addFileBoxToListBox(fileInfo:FileInfo):
            itemBox = AppLayoutBox(height=30, align='left', parent=self.fileListBox, fontBold=True)
            itemBox.addImage(fileInfo.fileIcon, stretch=0)
            itemBox.addText(fileInfo.fileName, stretch=1)
            pathStr = fileInfo.filePath
            if len(pathStr) > 40:
                pathStr = '...' + pathStr[-37:]
            itemBox.addText(pathStr, stretch=1)
            itemBox.addText(fileInfo.fileType, stretch=1)
            itemBox.addText(fileInfo.fileSize_withUnit(), stretch=1)
            itemBox.addButton(AutoTranslateWord('delete'), appManager.getUIImagePath('cross.png'), command= lambda: self.removeFile(fileInfo), stretch=0)
            self.fileListBox.addComponent(itemBox)
            self.__currentFileBoxes[fileInfo.filePath] = itemBox
            self.fileListBox.show()
            self.uploadButton.show()
            self.resize(self.width(), self.uploadFileArea.height() + self.fileListBox.height() + self.uploadButton.height() + 26)
        self.addEvent_onFileAdded(addFileBoxToListBox)

        #file list box
        fileBoxTitleText = fileListBoxTitleText if fileListBoxTitleText is not None else AutoTranslateWord('upload List')
        self.fileListBox = AppScrollBox(titleText=fileBoxTitleText, height=height)
        self.vBoxLayout.addWidget(self.fileListBox)
        self.SetFileBoxTitleText = self.fileListBox.SetTitleText
        self.fileBoxTitleText = self.fileListBox.titleText
        self.fileBoxTitleTextSize = self.fileListBox.titleTextSize
        self.SetFileBoxTitleTextSize = self.fileListBox.SetTitleTextSize
        self.fileBoxComponents = self.fileListBox.components
        self.addFileBox = self.fileListBox.addComponent
        self.removeFileBox = self.fileListBox.removeComponent
        self.fileListBox.hide()

        #upload button
        self.uploadButton = AppButton(text=AutoTranslateWord('upload'), parent=self,height=34, fontBold=True)
        self.vBoxLayout.addWidget(self.uploadButton, alignment=Qt.AlignRight)
        self.uploadButton.hide()
        if uploadButtonCommand is not None:
            self.addUploadButtonCommand(uploadButtonCommand)

        self.adjustSize()

    def addUploadButtonCommand(self, func:Callable[[Sequence[FileInfo]],any]):
        self.uploadButton.clicked.connect(func)
    def removeUploadButtonCommand(self, func:Callable[[Sequence[FileInfo]],any]):
        self.uploadButton.clicked.disconnect(func)






from typing import Optional
from mimetypes import guess_type
import os
from PySide2.QtGui import QIcon
from .AutoTranslateWord import AutoTranslateEnum
import Core

class FileType(AutoTranslateEnum):
    DOC = 0
    TXT = 1
    PDF = 2
    IMG = 3
    VIDEO = 4
    AUDIO = 5
    OTHER = 6

class FileInfo:
    '''file info, for files that not in database.
        Usually used for uploading files to database'''
    def __init__(self, filePath: str, readContent: bool = False):
        if not os.path.exists(filePath):
            raise FileNotFoundError(f"File not found: {filePath}")
        self._filePath: str = filePath
        self._fileContent : bytes = open(filePath, 'rb').read() if readContent else None
        self._fileName: str = os.path.basename(filePath)
        self._pureFileName: str = os.path.splitext(self._fileName)[0]
        self._extension: str = os.path.splitext(self._fileName)[-1][1:]
        self._fileSize: int = os.path.getsize(self._filePath)

        self._fileType: FileType = FileType.OTHER
        if self._extension != '':
            docTypes = ['doc', 'docx', 'docm', 'dotx', 'dotm', 'odt', 'ott', 'rtf', 'wpd', 'wps', 'xml']
            txtTypes = ['txt', 'log', 'tex', 'md']
            pdfTypes = ['pdf', 'xps', 'oxps']
            imgTypes = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tif', 'tiff', 'ico', 'svg', 'psd', 'ai', 'eps', 'indd',
                        'raw', 'nef', 'cr2', 'orf', 'sr2', 'arw', 'dng', 'webp']
            videoTypes = ['mp4', 'm4v', 'mov', 'avi', 'wmv', 'flv', 'swf', 'mkv', 'mpg', 'mpeg', '3gp', '3g2', '3gpp',
                          '3gpp2', 'webm', 'vob', 'ogv', 'ogg', 'drc', 'gifv', 'mng', 'qt', 'rm', 'rmvb', 'roq', 'svi',
                          'viv', 'asf', 'amv', 'm4p', 'm4b', 'm4r', 'f4v', 'f4p', 'f4a', 'f4b']
            audioTypes = ['mp3', 'wav', 'wma', 'aac', 'flac', 'm4a', 'ogg', 'oga', 'mka', 'm3u', 'wpl', 'm3u8', 'pls',
                          'opus', 'ra', 'ram', 'weba', 'ac3', 'aiff', 'ape', 'dts', 'm4b', 'm4p', 'mpc', 'ofr', 'ofs',
                          'tta', 'voc', 'vox', 'wv', 'cda']
            if self._extension in docTypes:
                self._fileType = FileType.DOC
            elif self._extension in txtTypes:
                self._fileType = FileType.TXT
            elif self._extension in pdfTypes:
                self._fileType = FileType.PDF
            elif self._extension in imgTypes:
                self._fileType = FileType.IMG
            elif self._extension in videoTypes:
                self._fileType = FileType.VIDEO
            elif self._extension in audioTypes:
                self._fileType = FileType.AUDIO
            else:
                self._fileType = FileType.OTHER
        else:
            guseeType = guess_type(self.filePath)[0]
            if guseeType:
                if guseeType.startswith('images'):
                    self._fileType = FileType.IMG
                elif guseeType.startswith('video'):
                    self._fileType = FileType.VIDEO
                elif guseeType.startswith('audio'):
                    self._fileType = FileType.AUDIO
                elif guseeType.startswith('text'):
                    self._fileType = FileType.TXT
                else:
                    self._fileType = FileType.OTHER
            else:
                self._fileType = FileType.OTHER

        self._fileIcon: Optional[QIcon] = None
        if self._fileType == FileType.DOC:
            self._fileIcon = QIcon(Core.appManager.getUIImagePath("docx.png"))
        elif self._fileType == FileType.TXT:
            self._fileIcon = QIcon(Core.appManager.getUIImagePath("txt.png"))
        elif self._fileType == FileType.PDF:
            self._fileIcon = QIcon(Core.appManager.getUIImagePath("pdf.png"))
        elif self._fileType == FileType.IMG:
            self._fileIcon = QIcon(Core.appManager.getUIImagePath("jpg.png"))
        elif self._fileType == FileType.VIDEO:
            self._fileIcon = QIcon(Core.appManager.getUIImagePath("mov.png"))
        elif self._fileType == FileType.AUDIO:
            self._fileIcon = QIcon(Core.appManager.getUIImagePath("audio.png"))
        else:
            self._fileIcon = QIcon(Core.appManager.getUIImagePath("unknown.png"))
    @property
    def filePath(self) :
        return self._filePath
    @property
    def fileContent(self) :
        return self._fileContent
    @property
    def fileName(self):
        return self._fileName
    @property
    def pureFileName(self):
        return self._pureFileName
    @property
    def extension(self):
        return self._extension
    @property
    def fileSize(self):
        return self._fileSize
    @property
    def fileType(self):
        return self._fileType
    @property
    def fileIcon(self) :
        return self._fileIcon
    def fileSize_withUnit(self) -> str:
        if self._fileSize < 1024:
            return f"{self._fileSize} B"
        elif self._fileSize < 1024 * 1024:
            return f"{round(self._fileSize / 1024, 2)} KB"
        elif self._fileSize < 1024 * 1024 * 1024:
            return f"{round(self._fileSize / 1024 / 1024, 2)} MB"
        else:
            return f"{round(self._fileSize / 1024 / 1024 / 1024, 2)} GB"
    def fileTypeName(self):
        return self._fileType.getTranslatedName()
    def __eq__(self, other: 'FileInfo') -> bool:
        if isinstance(other, FileInfo):
            return self.filePath == other.filePath
        elif isinstance(other, str):
            return self.filePath == other
        else:
            return False
    def __repr__(self):
        return f"<FileInfo({self.filePath})>"


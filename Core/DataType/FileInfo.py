from mimetypes import guess_type
import os, hashlib
from PySide2.QtGui import QIcon
from .AutoTranslateWord import AutoTranslateEnum
import Core

class FileType(AutoTranslateEnum):
    DOC = ('doc', 'docx', 'docm', 'dotx', 'dotm', 'odt', 'ott', 'rtf', 'wpd', 'wps', 'xml')
    TXT = ('txt', 'log', 'tex', 'md')
    PDF = ('pdf', 'xps', 'oxps')
    IMG = ('jpg', 'jpeg', 'png', 'gif', 'bmp', 'tif', 'tiff', 'ico', 'svg', 'psd', 'ai', 'eps', 'indd',
                        'raw', 'nef', 'cr2', 'orf', 'sr2', 'arw', 'dng', 'webp')
    VIDEO = ('mp4', 'm4v', 'mov', 'avi', 'wmv', 'flv', 'swf', 'mkv', 'mpg', 'mpeg', '3gp', '3g2', '3gpp',
                          '3gpp2', 'webm', 'vob', 'ogv', 'ogg', 'drc', 'gifv', 'mng', 'qt', 'rm', 'rmvb', 'roq', 'svi',
                          'viv', 'asf', 'amv', 'm4p', 'm4b', 'm4r', 'f4v', 'f4p', 'f4a', 'f4b')
    AUDIO = ('mp3', 'wav', 'wma', 'aac', 'flac', 'm4a', 'ogg', 'oga', 'mka', 'm3u', 'wpl', 'm3u8', 'pls',
                          'opus', 'ra', 'ram', 'weba', 'ac3', 'aiff', 'ape', 'dts', 'm4b', 'm4p', 'mpc', 'ofr', 'ofs',
                          'tta', 'voc', 'vox', 'wv', 'cda')
    OTHER = ()
    @staticmethod
    def GetFileTypeByExtension(extension: str) -> 'FileType':
        for fileType in FileType:
            if extension in fileType.value:
                return fileType
        return FileType.OTHER

class FileInfo:
    '''file info, for files that not in database.
        Usually used for uploading files to database'''
    _filePath: str = None
    _fileContent: bytes = None
    _fileName: str = None #with extension
    _pureFileName: str = None #without extension
    _extension: str = None
    _fileSize: int = None
    _fileType: FileType = None
    _fileIcon: QIcon = None
    _fileHash: str = None
    @classmethod
    def FromFilePath(cls, filePath: str, readContent: bool = False) -> 'FileInfo':
        if not os.path.exists(filePath):
            raise FileNotFoundError(f"File not found: {filePath}")
        self = cls()
        self._filePath= filePath
        self._fileContent= open(filePath, 'rb').read() if readContent else None
        self._fileName= os.path.basename(filePath)
        self._pureFileName = os.path.splitext(self._fileName)[0]
        self._extension= os.path.splitext(self._fileName)[-1][1:]
        self._fileSize= os.path.getsize(self._filePath)

        if self._extension != '':
            self._fileType = FileType.GetFileTypeByExtension(self._extension)
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
        return self
    def readFile(self) -> bytes:
        self._fileContent = open(self._filePath, 'rb').read()
        return self._fileContent
    def getFileHash(self) -> str:
        '''get file hash will force read file content'''
        if self._fileHash is None:
            if self._fileContent is None:
                self.readFile()
            self._fileHash = hashlib.md5(self._fileContent).hexdigest()
        return self._fileHash
    @property
    def fileHash(self) -> str:
        return self.getFileHash()
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


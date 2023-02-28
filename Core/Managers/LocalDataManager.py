import os, shutil, hashlib
from typing import Tuple, Sequence, Union
from ExternalPackage.sqlite_utils import Database, Table
from Core import appManager
from Core.DataType import FileInfo
from .Manager import *

class LocalDataManager(Manager):
    def __init__(self):
        self._database = Database(appManager.DATABASE_PATH)
        self._database.setForeignKeyRestrict(True)
        self._database.create_table(name='file',
                                    columns={'filePath': str, 'filename': str, 'fileHash': str},
                                    pk=['fileHash'],
                                    not_null=['filePath', "filename", "fileHash"],
                                    if_not_exists=True)
        self._fileTable = self._database['file']
        self.fileTable.create_index(['filename','fileHash'], if_not_exists=True)
    @property
    def database(self)->Database:
        return self._database
    @property
    def fileTable(self)->Table:
        return self._fileTable

    def hasFile(self, hash:str)->bool:
        try:
            self.fileTable.get(hash)
            return True
        except:
            return False

    def getFileInfo_ByHash(self, hash: str, readFile:bool=False) -> Union[FileInfo, None]:
        try:
            result = self.fileTable.get(hash)
        except:
            return None
        fileinfo = FileInfo.FromFilePath(result['filePath'], readFile)
        fileinfo._fileHash = result['fileHash']
        return fileinfo
    def getFileInfos_ByName(self, filename: str, readFile:bool=False) -> Tuple[FileInfo]:
        try:
            output = []
            for result in self.fileTable.find('filename', '=', filename):
                fileinfo = FileInfo.FromFilePath(result['filePath'], readFile)
                fileinfo._fileHash = result['fileHash']
                output.append(fileinfo)
            return tuple(output)
        except:
            return tuple()
    def getFileInfos_ByPureName(self, pureName: str, readFile:bool=False) -> Tuple[FileInfo]:
        try:
            output = []
            for result in self.fileTable.find('filename', 'like', f"%{pureName}%"):
                fileinfo = FileInfo.FromFilePath(result['filePath'], readFile)
                fileinfo._fileHash = result['fileHash']
                output.append(fileinfo)
        except:
            return tuple()

    def saveFile(self, fileinfo: FileInfo, keepName=False)->Union[str,None]:
        '''return None if file already exists'''
        fileHash = fileinfo.getFileHash()
        if self.hasFile(fileHash):
            return None
        #save file to directory which hash is first 2 char
        hashDir = os.path.join(appManager.DATA_PATH, fileHash[:2])
        if not os.path.exists(hashDir):
            os.mkdir(hashDir)
        saveName = fileinfo.fileName if keepName else fileHash
        savePath = os.path.join(hashDir, saveName)
        shutil.copy(fileinfo.filePath, savePath)
        self.fileTable.insert({'filePath': savePath, 'filename': fileinfo.fileName, 'fileHash': fileHash}, pk='fileHash', replace=True)
        return fileHash
    def saveFiles(self, fileinfos: Sequence[FileInfo]):
        for fileinfo in fileinfos:
            self.saveFile(fileinfo)
    def saveData(self, data, filename:str=None, keepFilename=False)->Union[str, None]:
        '''return None if file already exists'''
        _bytes = bytes if isinstance(data, bytes) else bytes(data, encoding='utf-8')
        hash = hashlib.md5(_bytes).hexdigest()
        if self.hasFile(hash):
            return None
        hashDir = os.path.join(appManager.DATA_PATH, hash[:2])
        if not os.path.exists(hashDir):
            os.mkdir(hashDir)
        saveName = filename if (keepFilename and filename is not None) else hash
        savePath = os.path.join(hashDir, saveName)
        with open(savePath, 'wb') as f:
            f.write(_bytes)
        self.fileTable.insert({'filePath': savePath, 'filename': saveName, 'fileHash': hash}, pk='fileHash', replace=True)
        return hash
    def deleteFile(self, fileHash: str)->bool:
        try:
            result = self.fileTable.get(fileHash)
            filePath = result['filePath']
            os.remove(filePath)
            self.fileTable.delete(fileHash)
            return True
        except:
            return False
    def deleteFiles(self, fileHashes: Sequence[str]):
        for fileHash in fileHashes:
            self.deleteFile(fileHash)

    def expectedPathByHash(self, fileHash: str) -> str:
        '''if file is not saved by hash as name, the path is not correct'''
        return os.path.join(appManager.DATA_PATH, fileHash[:2], fileHash)
    def getPathByHash(self, fileHash: str) -> Union[str,None]:
        try:
            result = self.fileTable.get(fileHash)
            return result['filePath']
        except:
            return None

localDataManager = LocalDataManager()

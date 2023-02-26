import Core
from Core.DataType import FileInfo
import sqlite3, os, shutil
from typing import Optional, Tuple, Sequence

from .Manager import *
@Manager
class LocalDataManager:
    _database: sqlite3.Connection = None
    def __init__(self):
        self._database = sqlite3.connect(Core.appManager.DATABASE_PATH)
        cursor = self._database.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='file'")
        if not cursor.fetchone():
            cursor.execute("""CREATE TABLE file(
                                        filePath TEXT,
                                        filename TEXT,
                                        hash TEXT PRIMARY KEY NOT NULL
                                )""")
        cursor.close()
    def getFileInfo_ByHash(self, hash: str, readFile:bool=False) -> Optional[FileInfo]:
        cursor = self._database.cursor()
        cursor.execute("SELECT * FROM File WHERE hash=?", (hash,))
        result = cursor.fetchone()
        if result:
            fileinfo = FileInfo.FromFilePath(result[0], readFile)
            fileinfo._fileHash = result[2]
            cursor.close()
            return fileinfo
        else:
            cursor.close()
            return None
    def getFileInfos_ByName(self, filename: str, readFile:bool=False) -> Tuple[FileInfo]:
        cursor = self._database.cursor()
        cursor.execute("SELECT * FROM File WHERE filename=?", (filename,))
        result = cursor.fetchall()
        output = []
        if result:
            for r in result:
                fileinfo = FileInfo.FromFilePath(r[0], readFile)
                fileinfo._fileHash = r[2]
                output.append(fileinfo)
            cursor.close()
            return tuple(output)
        else:
            cursor.close()
            return tuple()
    def getFileInfos_ByPureName(self, pureName: str, readFile:bool=False) -> Tuple[FileInfo]:
        cursor = self._database.cursor()
        cursor.execute("SELECT * FROM File WHERE filename LIKE ?", (pureName + "%",))
        result = cursor.fetchall()
        output = []
        if result:
            for r in result:
                fileinfo = FileInfo.FromFilePath(r[0], readFile)
                fileinfo._fileHash = r[2]
                output.append(fileinfo)
            cursor.close()
            return tuple(output)
        else:
            cursor.close()
            return tuple()
    def hasTable(self, tableName: str) -> bool:
        cursor = self._database.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tableName,))
        output = bool(cursor.fetchone())
        cursor.close()
        return output
    def createTable(self, tableName: str, columns: Sequence[Tuple[str,str]]):
        cursor = self._database.cursor()
        cursor.execute(f"CREATE TABLE {tableName}({', '.join([' '.join(col) for col in columns])})")
        cursor.close()
    @property
    def database(self) -> sqlite3.Connection:
        return self._database
    def databaseExecute(self, sql: str, params: tuple = None):
        cursor = self._database.cursor()
        cursor.execute(sql, params)
        cursor.close()
    def saveFile(self, fileinfo: FileInfo):
        fileHash = fileinfo.getFileHash()
        #save file to directory which hash is first 2 char
        hashDir = os.path.join(Core.appManager.DATABASE_PATH , "/" , fileHash[:2])
        if not os.path.exists(hashDir):
            os.mkdir(hashDir)
        savePath = os.path.join(hashDir, fileinfo.fileName)
        shutil.copy(fileinfo.filePath, savePath)
        cursor = self._database.cursor()
        cursor.execute("INSERT INTO File VALUES(?, ?, ?)", (savePath, fileinfo.fileName, fileHash))
        cursor.close()
    def saveFiles(self, fileinfos: Sequence[FileInfo]):
        for fileinfo in fileinfos:
            self.saveFile(fileinfo)
    def deleteFile(self, fileHash: str):
        cursor = self._database.cursor()
        result = cursor.execute("SELECT filePath FROM File WHERE hash=?", (fileHash,)).fetchone()
        if result:
            filePath = result[0]
        else:
            return
        cursor.execute("DELETE FROM File WHERE hash=?", (fileHash,))
        cursor.close()
        os.remove(filePath)
    def deleteFiles(self, fileHashes: Sequence[str]):
        for fileHash in fileHashes:
            self.deleteFile(fileHash)


localDataManager = LocalDataManager()

import sqlite_utils, os, shutil
from typing import Optional, Tuple, Sequence, Literal, Union

def find(table, *args, toTuple:bool=False):
    '''pattern: (column, method[equal/like], value)'''
    if len(args) == 3 and not isinstance(args[0], tuple) and not isinstance(args[0], list):
        return find(table, tuple(args), toTuple=toTuple)
    else:
        sql = f"SELECT * FROM {table.name} WHERE "
        for i, pattern in enumerate(args):
            if i > 0:
                sql += " AND "
            if pattern[1].lower() != "like" and pattern[1].lower() != "equal" and pattern[1].lower() != "=" and \
                    pattern[1].lower() != "==":
                raise ValueError("method must be 'like' or 'equal'")
            method = "LIKE" if pattern[1].lower() == "like" else "="
            sql += f"{pattern[0]} {method} '{pattern[2]}'"
        if not toTuple:
            return table.db.query(sql)
        else:
            output = []
            for data in table.db.query(sql):
                output.append(data)
            return output
def printTable(table):
    print("table:", table.name)
    for row in table.rows:
        print(row)
    print('-----------------')
class TableHint(sqlite_utils.db.Table):
    def find(table, *args) -> Union[sqlite_utils.db.Generator, Tuple[dict]]:
        '''pattern: (column, method[equal/like], value)'''
        pass
    def printTable(table) -> None:
        '''print all rows in table'''
        pass
    def add_trigger(table, name, event: Literal["INSERT", "DELETE", "UPDATE"], sql: str,
                    time: Literal["BEFORE", "UPDATE"] = "AFTER", column: str = None):
        pass
    def remove_trigger(table, name):
        pass
class Database(sqlite_utils.Database):
    def add_trigger(self, name, event:Literal["INSERT","DELETE","UPDATE"], table:Union[sqlite_utils.db.Table, str],
                    sql:str, time:Literal["BEFORE","UPDATE"]="AFTER", column:str=None):
        _tableName = table.name if isinstance(table, sqlite_utils.db.Table) else table
        if column is None:
            self.execute(f"CREATE TRIGGER {name} {time} {event} ON {_tableName} FOR EACH ROW BEGIN {sql} END;")
        else:
            self.execute(f"CREATE TRIGGER {name} {time} {event} OF {column} ON {_tableName} BEGIN {sql} END;")
    def remove_trigger(self, name):
        self.execute(f"DROP TRIGGER IF EXISTS {name};")
    def printTables(self):
        for table in self.tables:
            print("table:", table.name)
            for row in table.rows:
                print(row)
        print('-----------------')
    def table(self, *args, **kwargs) -> Union["Table", "View", 'TableHint']:
        return super().table(*args, **kwargs)
    def __getitem__(self, item)->Union["Table", "View", 'TableHint']:
        return super().__getitem__(item)
    def hasTable(self, tableName: str) -> bool:
        return tableName in [t.name for t in self.tables]
def add_trigger(table, name, event:Literal["INSERT","DELETE","UPDATE"], sql:str, time:Literal["BEFORE","UPDATE"]="AFTER", column:str=None):
    _name = table.name + "_" + name
    table.db.add_trigger(_name, event, table, sql, time, column)
def remove_trigger(table, name):
    _name = table.name + "_" + name
    table.db.remove_trigger(_name)

from Core import appManager
from Core.DataType import FileInfo
from .Manager import *
@Manager
class LocalDataManager:
    def __init__(self):
        setattr(sqlite_utils.db.Table, "find", find)
        setattr(sqlite_utils.db.Table, "printTable", printTable)
        setattr(sqlite_utils.db.Table, "add_trigger", add_trigger)
        setattr(sqlite_utils.db.Table, "remove_trigger", remove_trigger)
        self._database = Database(appManager.DATABASE_PATH)
        self._database.create_table(name='file',
                                    columns={'filePath': str, 'filename': str, 'fileHash': str},
                                    pk=['fileHash'],
                                    not_null=['filePath', "filename", "fileHash"],
                                    if_not_exists=True)
    @property
    def database(self) -> Database:
        return self._database
    @property
    def fileTable(self) -> TableHint:
        return self._database['file']

    def getFileInfo_ByHash(self, hash: str, readFile:bool=False) -> Optional[FileInfo]:
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

    def saveFile(self, fileinfo: FileInfo):
        fileHash = fileinfo.getFileHash()
        #save file to directory which hash is first 2 char
        hashDir = os.path.join(appManager.DATABASE_PATH, fileHash[:2])
        if not os.path.exists(hashDir):
            os.mkdir(hashDir)
        savePath = os.path.join(hashDir, fileinfo.fileName)
        shutil.copy(fileinfo.filePath, savePath)
        self.fileTable.insert({'filePath': savePath, 'filename': fileinfo.fileName, 'fileHash': fileHash}, pk='fileHash', replace=True)
    def saveFiles(self, fileinfos: Sequence[FileInfo]):
        for fileinfo in fileinfos:
            self.saveFile(fileinfo)
    def deleteFile(self, fileHash: str):
        try:
            result = self.fileTable.get(fileHash)
            filePath = result['filePath']
            os.remove(filePath)
            self.fileTable.delete(fileHash)
        except:
            return
    def deleteFiles(self, fileHashes: Sequence[str]):
        for fileHash in fileHashes:
            self.deleteFile(fileHash)

localDataManager = LocalDataManager()

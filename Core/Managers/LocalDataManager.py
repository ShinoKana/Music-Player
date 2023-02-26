import Core
import sqlite3
import hashlib

from .Manager import *
@Manager
class LocalDataManager:
    def __init__(self):
        self._database = sqlite3.connect(Core.appManager.DATABASE_PATH)
        cursor = self._database.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='File'")
        if not cursor.fetchone():
            cursor.execute("""CREATE TABLE File(
                                        filename TEXT,
                                        filesize INTEGTER ,
                                        hash TEXT PRIMARY KEY NOT NULL)""")
        cursor.close()



localDataManager = LocalDataManager()

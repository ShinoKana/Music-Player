import sqlite3
class DatabaseFile:
    def __init__(self, path):
        self.path = path
        self.db = sqlite3.connect(path)
        self.cursor = self.db.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS data (id INTEGER PRIMARY KEY, key TEXT, value TEXT)")
        self.db.commit()

    def get(self, key):
        self.cursor.execute("SELECT value FROM data WHERE key = ?", (key,))
        result = self.cursor.fetchone()
        if result is None:
            return None
        return result[0]

    def set(self, key, value):
        self.cursor.execute("INSERT OR REPLACE INTO data (key, value) VALUES (?, ?)", (key, value))
        self.db.commit()

    def delete(self, key):
        self.cursor.execute("DELETE FROM data WHERE key = ?", (key,))
        self.db.commit()

    def close(self):
        self.db.close()
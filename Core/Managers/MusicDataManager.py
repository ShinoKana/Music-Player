from PySide2.QtCore import QUrl
from PySide2.QtMultimedia import QMediaContent, QMediaPlaylist
from PySide2.QtGui import QIcon
from ExternalPackage.sqlite_utils import Table
from .LocalDataManager import localDataManager
from typing import Union, Dict, cast, Iterable
from .Manager import *
from Core.DataType import FileType, FileInfo
import Core
from tinytag import TinyTag

_allMusics:Dict[int, 'Music'] = {}
_allMusicLists:Dict[int, 'MusicList'] = {}

class Music(QMediaContent, FileInfo):
    _id: int = None
    _title: str = None
    _artist: str = None
    _album: str = None
    _albumArtist: str = None
    _duration: int = None
    _coverPath: str = None
    _lyricPath: str = None

    def __new__(cls, hash, id, *args, **kwargs):
        if id in _allMusics:
            return _allMusics[id]
        else:
            return super().__new__(cls)
    def __init__(self, hash, id, title: str = "", artist: str = "", duration: int = 0, album: str = "",
                 albumArtist="", fileExt: str = "", coverHash=None, lyricHash=None):

        self._filePath = localDataManager.expectedPathByHash(hash)
        self._fileHash = hash
        self._fileType = FileType.AUDIO
        self._fileName = f'{title}.{fileExt}'
        self._pureFileName = title
        self._fileSize = 0
        self._fileExt = fileExt
        self._fileIcon = QIcon(Core.appManager.getUIImagePath("audio.png"))

        QMediaContent.__init__(self, QUrl.fromLocalFile(self.filePath))
        self._id = id
        self._title = title
        self._artist = artist
        self._duration = duration
        self._album = album
        self._albumArtist = albumArtist
        if coverHash:
            self._coverPath = localDataManager.expectedPathByHash(coverHash)
        if lyricHash:
            self._lyricPath = localDataManager.expectedPathByHash(lyricHash)
        _allMusics[id] = self
        self.__init__ = lambda *args, **kwargs: None
    @property
    def id(self)->int:
        return self._id
    @property
    def title(self)->str:
        return self._title
    @property
    def artist(self)->str:
        return self._artist
    @property
    def album(self)->str:
        return self._album
    @property
    def albumArtist(self)->str:
        return self._albumArtist
    @property
    def duration(self)->int:
        return self._duration
    @property
    def duration_formatted(self)->str:
        return '{}:{}'.format(self._duration // 60, self._duration % 60)
    @property
    def coverPath(self)->str:
        return self._coverPath
    @property
    def lyricPath(self)->str:
        return self._lyricPath
class MusicList(QMediaPlaylist):
    _id: int = None
    _name: str = ""
    def __new__(cls, id, name, musicIDs: Iterable[int] = None):
        if id in _allMusicLists:
            _allMusicLists[id].__init__ = lambda *args, **kwargs: None
            return _allMusicLists[id]
        else:
            lst = QMediaPlaylist.__new__(cls)
            cls.__init__(lst, id, name, musicIDs)
            lst.__init__ = lambda *args, **kwargs: None
            _allMusicLists[id] = lst
            return lst
    def __init__(self, id, name, musicIDs: Iterable[int] = None):
        QMediaPlaylist.__init__(self)
        self._id = id
        self._name = name
        if musicIDs:
            for musicID in musicIDs:
                music = _allMusics.get(musicID, None)
                self.addMedia(music) if music else None

class MusicDataManager(Manager):
    _musicTable: Table = None
    _musicListTable: Table = None
    def __init__(self):
        localDataManager.database.create_table(
           name='music',
           columns={'id':int, 'title': str, 'artist': str, 'duration': int, 'album':str, 'albumArtist':str,
                    'fileExt':str, 'musicHash': str, 'coverHash': str, 'lyricHash': str},
           not_null=['id','musicHash'],
           pk=['id'],
           foreign_keys=[('musicHash', 'file', 'fileHash'),
                         ('coverHash', 'file', 'fileHash'),
                         ('lyricHash', 'file', 'fileHash')],
           if_not_exists=True,
           foreign_key_cascade=['musicHash', 'coverHash', 'lyricHash'],
           autoincrement='id'
        )
        self._musicTable = localDataManager.database['music']
        self._musicTable.create_index(['id','title','musicHash'], if_not_exists=True)
        localDataManager.database.create_table(
              name='musicList',
              columns={'id':int, 'name': str, 'musicList': str},
              pk=['id'],
              not_null=['id', 'name'],
              if_not_exists=True,
              autoincrement='id'
        )
        self._musicListTable = localDataManager.database['musicList']
        self._musicListTable.create_index(['id','name'], if_not_exists=True)
        #load data
        for row in self._musicTable.rows:
            _allMusics[row['id']] = Music(hash=row['musicHash'],id=row['id'], title=row['title'], artist=row['artist'], duration=row['duration'],
                                                    album=row['album'], albumArtist=row['albumArtist'], fileExt=row['fileExt'], coverHash=row['coverHash'], lyricHash=row['lyricHash'])
        for row in self._musicListTable.rows:
            _musicList = [int(s) for s in row['musicList'].split(',')]
            _allMusicLists[row['id']] = MusicList(row['id'], row['name'], _musicList)

    @property
    def musicTable(self) -> Table:
        return self._musicTable
    @property
    def musicListTable(self) -> Table:
        return self._musicListTable

    @property
    def allMusics(self) -> Dict[int, 'Music']:
        return _allMusics
    @property
    def allMusicLists(self) -> Dict[int, 'MusicList']:
        return _allMusicLists
    def getMusic(self, id:int)-> Union[None, 'Music']:
        try:
            return self._allMusics[id]
        except KeyError:
            return None
    def getMusicList(self, id:int)-> Union[None, 'MusicList']:
        try:
            return self._allMusicLists[id]
        except KeyError:
            return None

    #save & delete
    def saveMusic(self, fileInfo:'FileInfo')-> Union[None, 'Music']:
        if fileInfo.fileType != FileType.AUDIO and fileInfo.fileType != Core.FileType.AUDIO:
            return None
        if localDataManager.hasFile(fileInfo.fileHash):
            return None
        localDataManager.saveFile(fileInfo)
        tag = TinyTag.get(fileInfo.filePath, image=True)
        title = tag.title if tag.title else fileInfo.pureFileName
        artist = tag.artist
        duration = int(tag.duration)
        album = tag.album
        albumArtist = tag.albumartist
        coverImg = tag.get_image()
        if coverImg:
            coverHash = localDataManager.saveData(coverImg)
        else:
            coverHash = None
        self.musicTable.insert({'title': title, 'artist': artist, 'duration': duration, 'album':album,
                                'albumArtist':albumArtist, 'fileExt':fileInfo.extension,'musicHash': fileInfo.fileHash, 'coverHash': coverHash})
        addedID = self.musicTable.getTableSequence()
        music = Music(hash=fileInfo.fileHash, id=addedID, title=title, artist=artist, duration=duration, album=album,
                          albumArtist=albumArtist, coverHash=coverHash, fileExt=fileInfo.extension)
        _allMusics[addedID] = music
        return music
    def saveCover(self, fileInfo:'FileInfo', music:Union[int, 'Music']):
        if fileInfo.fileType != Core.FileType.IMG and fileInfo.fileType != Core.FileType.IMG:
            return
        if localDataManager.hasFile(fileInfo.fileHash):
            return
        localDataManager.saveFile(fileInfo)
        _musicID = music.id if isinstance(music, Music) else music
        self.musicTable.update(_musicID, {'coverHash': fileInfo.fileHash})
    def saveCover_byData(self, data, music:Union[int, 'Music']):
        hash = localDataManager.saveData(data)
        if hash is None:
            return
        _musicID = music.id if isinstance(music, Music) else music
        self.musicTable.update(_musicID, {'coverHash': hash})
        try:
            _allMusics[_musicID]._coverPath = localDataManager.expectedPathByHash(hash)
        except KeyError:
            pass
    def saveLyric(self, fileInfo:'FileInfo', music:Union[int, 'Music']):
        hash = localDataManager.saveFile(fileInfo)
        if hash is None:
            return
        _musicID = music.id if isinstance(music, Music) else music
        self.musicTable.update(_musicID, {'lyricHash': hash})
        try:
            _allMusics[_musicID]._lyricPath = localDataManager.expectedPathByHash(hash)
        except KeyError:
            pass

musicDataManager = MusicDataManager()
from PySide2.QtCore import QUrl
from PySide2.QtMultimedia import QMediaContent, QMediaPlaylist
from PySide2.QtGui import QIcon
from ExternalPackage.sqlite_utils import Table
from .LocalDataManager import localDataManager
from typing import Union, Dict, List, Sequence, Tuple, Callable
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
    def __eq__(self, other):
        if isinstance(other, Music):
            return self.id == other.id
        elif isinstance(other, QMediaContent):
            return QMediaContent.__eq__(self, other)
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
        min = self._duration // 60
        sec = self._duration % 60
        return '{}:{}'.format(min, sec if sec >= 10 else '0' + str(sec))
    @property
    def coverPath(self)->str:
        return self._coverPath
    @property
    def lyricPath(self)->str:
        return self._lyricPath
class MusicList(QMediaPlaylist):
    def __new__(cls, id, name, musicIDs: Sequence[int] = None):
        if id in _allMusicLists:
            _allMusicLists[id].__init__ = lambda *args, **kwargs: None
            return _allMusicLists[id]
        else:
            lst = QMediaPlaylist.__new__(cls)
            _allMusicLists[id] = lst
            return lst
    def __init__(self, id, name, musicIDs: Sequence[int] = None):
        super().__init__()
        self._musicIDs = list(musicIDs) if musicIDs else []
        self._id = id
        self._name = name
        for musicID in musicIDs:
            music = _allMusics.get(musicID, None)
            self.addMedia(music) if music else None
    @property
    def currentMusic(self)->Music:
        return musicDataManager.getMusic(self.musicIDs[self.currentIndex()])
    @property
    def id(self)->int:
        return self._id
    @property
    def name(self)->str:
        return self._name
    @property
    def musicIDs(self)->Tuple[int]:
        return tuple(self._musicIDs)
    def deleteMusic(self, musicID:int):
        if musicID in self._musicIDs:
            self.removeMedia(self._musicIDs.index(musicID))
            self._musicIDs.remove(musicID)
            if self.id !=-1: # -1 is the default playlist for all songs
                musicDataManager.musicTable.update(self.id, {'musicList': ','.join(map(str, self._musicIDs))})
class MusicDataManager(Manager):
    _musicTable: Table = None
    _musicListTable: Table = None
    _onMusicAdded: List[Callable[[Music], any]] = []
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
           foreign_key_cascade=['musicHash'],
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
        _allMusicLists[-1] = MusicList(-1, 'allSong', _allMusics.keys()) #allSong list, can't be deleted and modified
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
            return _allMusics[id]
        except KeyError:
            return None
    def getMusicList(self, id:int)-> Union[None, 'MusicList']:
        try:
            return _allMusicLists[id]
        except KeyError:
            return None

    def addOnMusicAddedCallback(self, callback: Callable[['Music'], any]):
        self._onMusicAdded.append(callback)
    def removeOnMusicAddedCallback(self, callback: Callable[['Music'], any]):
        self._onMusicAdded.remove(callback)

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
        for callback in self._onMusicAdded:
            callback(music)
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
    def deleteMusic(self, music:Union[int, 'Music']):
        _musicID = music if isinstance(music, int) else music.id
        _musicData = self.musicTable.get(_musicID)
        localDataManager.deleteFile(_musicData.get('lyricHash',None)) if _musicData.get('lyricHash',None) else None
        localDataManager.deleteFile(_musicData.get('coverHash',None)) if _musicData.get('coverHash',None) else None
        localDataManager.deleteFile(_musicData.get('musicHash'))
        for musicList in _allMusicLists.values():
            musicList.deleteMusic(_musicID) # try all
        from Core import musicPlayerManager, appManager
        if musicPlayerManager.currentMusic.id == _musicID:
            musicPlayerManager.clear()
        if appManager.record.lastSongIndex.value == _musicID:
            appManager.record.lastSongIndex.value = 0
            appManager.record.lastSongTime.value = 0
        try:
            del _allMusics[_musicID]
        except KeyError:
            pass
    def deleteLyric(self, music:Union[int, 'Music']):
        _musicID = music if isinstance(music, int) else music.id
        _musicData = self.musicTable.get(_musicID)
        succ = (localDataManager.deleteFile(_musicData.get('lyricHash',None)) if _musicData.get('lyricHash',None) else None)
        if succ:
            self.musicTable.update(_musicID, {'lyricHash':None})
            try:
                _allMusics[_musicID]._lyricPath = None
            except KeyError:
                pass
    def deleteCover(self, music:Union[int, 'Music']):
        _musicID = music if isinstance(music, int) else music.id
        _musicData = self.musicTable.get(_musicID)
        succ = (localDataManager.deleteFile(_musicData.get('coverHash',None)) if _musicData.get('coverHash',None) else None)
        if succ:
            self.musicTable.update(_musicID, {'coverHash':None})
            try:
                _allMusics[_musicID]._coverPath = None
            except KeyError:
                pass

musicDataManager = MusicDataManager()
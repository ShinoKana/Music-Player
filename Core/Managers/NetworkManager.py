import json, GlobalValue
from Core import appManager, musicDataManager, MusicList, SingleEnum, AutoTranslateWord
import socketio, socket, netifaces, stun, asyncio
from PySide2.QtCore import QRunnable, Signal, QObject, QThreadPool
from typing import Optional, Callable, Iterable, Union, Literal, List, Dict, Tuple
from .Manager import *

_SERVER_URL = 'http://localhost:9192'
class NATtype(SingleEnum):
    Unknown = 0
    Blocked = 1
    OpenInternet = 2
    FullCone = 3
    SymmetricUDPFirewall = 4
    RestricNAT = 5
    RestricPortNAT = 6
    SymmetricNAT = 7
class NetworkManager(socketio.AsyncClient, Manager):

    _threadPool = None

    _nodeProcess = None
    _nodeProcessQueue = None
    _nodePort = None

    _serverConnected = False

    _TURN_connected = []

    def __init__(self):
        super().__init__()
        self._nodePort = GlobalValue.GetGlobalValue('NODE_PORT')
        self._nodeProcess = GlobalValue.GetGlobalValue('NODE_PROCESS')
        self._nodeProcessQueue = GlobalValue.GetGlobalValue('NODE_QUEUE')
        print('nodePort:', self._nodePort)

        #register events
        self.on('connect', self._connect_handler)
        self.on('disconnect', self._disconnect_handler)
        self.on('direct_connect', self.direct_connect)
        self.on('udpHolePunch_repeat', self.udpHolePunch_repeat)
        self.on('udpHolePunch_once', self.udpHolePunch_once)
        self.on('TURN_connect', self.TURN_connect)
        self.on('TURN_disconnect', self.TURN_disconnect)
        musicDataManager.addOnMusicAddedCallback(self.onUploadSong)
        musicDataManager.addOnMusicDeletedCallback(self.onDeleteSong)

        #pool for threadings
        self._threadPool = QThreadPool()

        async def connect_to_server(callback):
            print('connecting to server...')
            print('getting network info...')
            tasks = [self.get_globalIP_and_NATtype(), self.getLocalIP(), self.getSubMask()]
            result = await asyncio.gather(*tasks)
            (globalIP, natType), localIP, submask = result
            print(
                    'network info:',
                    'ip:',globalIP,' / ',
                    'localIP:',localIP,' / ',
                    'submask:',submask,' / ',
                    'natType:',natType
                  )
            id = appManager.record.userID.value
            try:
                await self.connect(
                    url = _SERVER_URL,
                    headers = {'id': id, 'ip': globalIP, 'localIP': localIP,
                            'port': str(self.nodePort), 'submask': submask, 'natType': str(natType.value)},
                    wait_timeout = 5
                )
                print('connect to server success')
                callback(True)
            except Exception as e:
                print('connect to server failed, error:', e)
                callback(False)
        appManager.goLoading(AutoTranslateWord('connecting to server...'))
        def onConnectionDone(result):
            appManager.stopLoading()
            if result:
                appManager.toast(AutoTranslateWord('connect to server success'))
            else:
                appManager.toast(AutoTranslateWord('connect to server failed'))
        class ForeverThread(QRunnable):
            def run(self):
                loop = asyncio.new_event_loop()
                loop.create_task(connect_to_server(onConnectionDone))
                loop.run_forever()
        self._threadPool.start(ForeverThread())

    def _connect_handler(self):
        self._serverConnected = True
    def _disconnect_handler(self):
        self._serverConnected = False
    @property
    def serverConnected(self):
        return self._serverConnected

    #song related
    def onUploadSong(self, newMusic:'Music'):
        '''add user to song's holders'''
        data ={'hash': newMusic.fileHash, 'name': newMusic.title, 'artist': newMusic.artist,
               'fileExt': newMusic.extension, 'fileSize': str(newMusic.fileSize), 'album': newMusic.album}
        print('uploadSong to server:', data)
        asyncio.run(self.emit('uploadSong', data))
    def onDeleteSong(self, hash:str):
        '''remove user from song's holders'''
        print('deleteSong holder from server:', hash)
        asyncio.run(self.emit('deleteSong', {'hash': hash}))
    async def findSong(self, keywords:str, mode:Literal['name', 'artist','album'])->Optional[Tuple[Dict]]:
        '''return: (song1, song2, ...)'''
        ret:Tuple[Dict] = None
        def setReturnValue(*data):
            nonlocal ret
            ret = tuple(data)
        await self.emit('findSong', {'keywords': keywords, 'mode': mode}, callback=setReturnValue)
        async def waitReturnValue():
            nonlocal ret
            while ret is None:
                await asyncio.sleep(0.5)
        await asyncio.wait_for(waitReturnValue(), timeout=10)
        if ret is None:
            print('findSong timeout')
            return None
        return ret

    #node related
    def orderNode(self, funcName, *args, needOutput=False, **kwargs):
        if self._nodeProcessQueue is None or self._nodeProcess is None:
            return
        self._nodeProcessQueue.put((funcName, args, kwargs))
    def try_connect_to(self, userID:str):
        self.emit('help_connect_to', {'targetID': userID})
    def direct_connect(self, data):
        ip = data['ip']
        port = data['port']
        return self.orderNode('connect_to', ip, port)
    def udpHolePunch_repeat(self, data):
        self.orderNode('udp_send_repeatly', data=b' ', port=data['port'], addr=data['ip'])
    def udpHolePunch_once(self, data):
        self.orderNode('udp_send', data=b' ', port=data['port'], addr=data['ip'])
    def TURN_connect(self, data):
        self._TURN_connected.append(data['ip']) if data['ip'] not in self._TURN_connected else None
    def TURN_disconnect(self, data):
        self._TURN_connected.remove(data['ip']) if data['ip'] in self._TURN_connected else None

    @property
    def sessionID(self):
        return self.get_sid()
    @property
    def nodePort(self):
        return self._nodePort

    async def getLocalIP(self):
        # 获取本地IP地址
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    async def get_globalIP_and_NATtype(self) -> (str, NATtype):
        # 获取NAT类型
        natType, ip, _ = stun.get_ip_info()
        if natType == stun.Blocked:
            natType = NATtype.Blocked
        elif natType == stun.OpenInternet:
            natType = NATtype.OpenInternet
        elif natType == stun.FullCone:
            natType = NATtype.FullCone
        elif natType == stun.SymmetricUDPFirewall:
            natType = NATtype.SymmetricUDPFirewall
        elif natType == stun.RestricNAT:
            natType = NATtype.RestricNAT
        elif natType == stun.RestricPortNAT:
            natType = NATtype.RestricPortNAT
        elif natType == stun.SymmetricNAT:
            natType = NATtype.SymmetricNAT
        else:
            natType = NATtype.Unknown
        return ip, natType
    async def getSubMask(self):
        ip_address = await self.getLocalIP()
        # 遍历所有网卡获取子网掩码
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    if addr['addr'] == ip_address:
                        return addr['netmask']
        return None

    def create_thread(self,
                      func:Callable,
                      args:Optional[Tuple]=None,
                      kwargs:Optional[Dict]=None,
                      returnCallbacks:Optional[Union[Iterable[Callable[[object], None]],Callable[[object], None]]]=None,
                      errorCallbacks:Optional[Union[Iterable[Callable[[Exception], None]],Callable[[Exception], None]]]=None,
                      start:bool=True):
        class WorkerSignals(QObject):
            finished = Signal(object)
            error = Signal(Exception)

        class Worker(QRunnable):
            def __init__(self):
                super().__init__()
                self.signals = WorkerSignals()
                if returnCallbacks is not None:
                    if isinstance(returnCallbacks, Iterable):
                        for callback in returnCallbacks:
                            self.signals.finished.connect(callback)
                    else:
                        self.signals.finished.connect(returnCallbacks)
                if errorCallbacks is not None:
                    if isinstance(errorCallbacks, Iterable):
                        for callback in errorCallbacks:
                            self.signals.error.connect(callback)
                    else:
                        self.signals.error.connect(errorCallbacks)
            def run(self):
                try:
                    if args is None and kwargs is None:
                        result = func()
                    elif args is None:
                        result = func(**kwargs)
                    elif kwargs is None:
                        result = func(*args)
                    else:
                        result = func(*args, **kwargs)
                    self.signals.finished.emit(result)
                except Exception as e:
                    self.signals.error.emit(e)
        if start:
            worker = Worker()
            self._threadPool.start(worker)
            return worker
        else:
            return Worker()
    def create_async_thread(self,
                            func:Callable,
                            args: Optional[Tuple] = None,
                            kwargs: Optional[Dict] = None,
                            returnCallbacks:Optional[Union[Iterable[Callable[[object], None]],Callable[[object], None]]]=None,
                            errorCallbacks:Optional[Union[Iterable[Callable[[Exception], None]],Callable[[Exception], None]]]=None,
                            start:bool=True):
        class WorkerSignals(QObject):
            finished = Signal(object)
            error = Signal(Exception)
        class Worker(QRunnable):
            def __init__(self):
                super().__init__()
                self.signals = WorkerSignals()
                if returnCallbacks is not None:
                    if isinstance(returnCallbacks, Iterable):
                        for callback in returnCallbacks:
                            self.signals.finished.connect(callback)
                    else:
                        self.signals.finished.connect(returnCallbacks)
                if errorCallbacks is not None:
                    if isinstance(errorCallbacks, Iterable):
                        for callback in errorCallbacks:
                            self.signals.error.connect(callback)
                    else:
                        self.signals.error.connect(errorCallbacks)
            def __del__(self):
                print('worker is deleted')
            def run(self):
                try:
                    if args is None and kwargs is None:
                        result = asyncio.run(func())
                    elif args is None:
                        result = asyncio.run(func(**kwargs))
                    elif kwargs is None:
                        result = asyncio.run(func(*args))
                    else:
                        result = asyncio.run(func(*args, **kwargs))
                    self.signals.finished.emit(result)
                except Exception as e:
                    self.signals.error.emit(e)
        if start:
            worker = Worker()
            self._threadPool.start(worker)
            return worker
        else:
            return Worker()

networkManager = NetworkManager()
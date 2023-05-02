from Core import appManager, musicDataManager, MusicList, SingleEnum, AutoTranslateWord
import socketio, socket, requests, netifaces, stun, asyncio, pythonp2p
from PySide2.QtCore import QRunnable, Signal, QObject, QThreadPool
from typing import Optional, Callable, Iterable, Union
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

    _node: pythonp2p.Node = None
    _threadPool = None

    def __init__(self):
        super().__init__()
        self._threadPool = QThreadPool()
        async def connect_to_server():
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
            self._node = pythonp2p.Node()
            try:
                await self.connect(
                    url = _SERVER_URL,
                    headers = {'id': id, 'ip': globalIP, 'localIP': localIP,
                            'port': str(self.node.port), 'submask': submask, 'natType': str(natType.value)},
                    wait_timeout = 5
                )
                self.node.start()
                print('connect to server success')
                return True
            except Exception as e:
                print('connect to server failed, error:', e)
                return False

        appManager.goLoading(AutoTranslateWord('connecting to server...'))
        def onConnectionDone(result):
            appManager.stopLoading()
            if result:
                appManager.toast(AutoTranslateWord('connect to server success'))
            else:
                appManager.toast(AutoTranslateWord('connect to server failed'))
        self.create_async_thread(func = connect_to_server,
                                 returnCallbacks = onConnectionDone)

    @property
    def sessionID(self):
        return self.get_sid()
    @property
    def node(self):
        return self._node
    @property
    def port(self):
        if self._node is None:
            return None
        return self._node.port

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
                      func:Callable[[], object],
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
                    result = func()
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
                            func:Callable[[], object],
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
                    result = asyncio.run(func())
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
from Core import appManager, musicDataManager, MusicList, SingleEnum, AutoTranslateWord
import socketio, socket, requests, netifaces, stun, asyncio, pythonp2p, threading
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

    def __init__(self):
        super().__init__()
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
                #appManager.toast(AutoTranslateWord('connect to server success'))
            except Exception as e:
                print('connect to server failed, error:', e)
                #appManager.toast(AutoTranslateWord('connect to server failed'))
                return

        #appManager.goLoading(AutoTranslateWord('connecting to server...'))
        #threading.Thread(target=lambda: asyncio.run(connect_to_server())).start()

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

networkManager = NetworkManager()
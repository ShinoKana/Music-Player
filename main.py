import multiprocessing
def runNode(inQueue, outQueue, eventQueue):
    try:
        import pythonp2p
    except ModuleNotFoundError:
        import sys, crypto
        sys.modules['Crypto'] = crypto
        import pythonp2p
    import threading, time
    class Node(pythonp2p.Node):

        #local events
        on_connected = []
        on_disconnected = []
        on_message_received = []

        def __init__(self, *args, inQueue: multiprocessing.Queue = None, outQueue: multiprocessing.Queue = None,
                     eventQueue:multiprocessing.Queue = None, **kwargs):
            super().__init__()
            self.inQueue = inQueue
            self.outQueue = outQueue
            self.eventQueue = eventQueue
            outQueue.put(self.port)
            outQueue.put(self.id)
            self.stop_UDP_send_repeat = False

            def get_command_from_queue():
                if self.inQueue is not None:
                    while True:
                        command = self.inQueue.get()
                        funcName, args, kwargs = command
                        needOutput = kwargs.pop('needOutput', False)
                        print('received command:', funcName, 'args:', args, 'kwargs:', kwargs)
                        try:
                            ret = getattr(self, funcName)(*args, **kwargs)
                            if self.outQueue is not None and needOutput:
                                self.outQueue.put(ret)
                        except Exception as e:
                            print('Error when executing command:', e)

            threading.Thread(target=get_command_from_queue, daemon=True).start()

        def udp_send(self, data: bytes, addr: tuple, port: int):
            self.sock.sendto(data, (addr, port))
        def udp_send_repeatly(self, data: bytes, addr: tuple, port: int, targetNodeID:str, interval: float = 0.25, time_limit: float = 10):
            def stopSendingOnConnected(nodeID):
                if nodeID == targetNodeID:
                    self.stop_udp_send_repeatly()
            self.on_connected.append(stopSendingOnConnected)
            def _send():
                timeCount = 0
                while timeCount < time_limit and not self.stop_UDP_send_repeat:
                    self.sock.sendto(data, (addr, port))
                    time.sleep(interval)
                    timeCount += interval
                self.stop_UDP_send_repeat = False
                self.on_connected.remove(stopSendingOnConnected)
                print('stop sending')
            threading.Thread(target=_send, daemon=True).start()
        def stop_udp_send_repeatly(self):
            self.stop_UDP_send_repeat = True

        def on_message(self, data, senderID, private):
            super().on_message(data, senderID, private)
            for func in tuple(self.on_message_received):
                func(data, senderID, private)
            self.eventQueue.put(('on_node_message_received', (data, senderID, private)))
        def node_connected(self, nodeID):
            super().node_connected(nodeID)
            for func in tuple(self.on_connected):
                func(nodeID)
            self.eventQueue.put(('on_node_connected', (nodeID,)))
        def node_disconnected(self, nodeID):
            super().node_disconnected(nodeID)
            for func in tuple(self.on_disconnected):
                func(nodeID)
            self.eventQueue.put(('on_node_disconnected', (nodeID,)))

    node = Node(inQueue=inQueue, outQueue=outQueue, eventQueue=eventQueue)
    node.start()

if __name__ == '__main__':
    multiprocessing.freeze_support()
    import GlobalValue, threading

    NODE_IN_QUEUE = multiprocessing.Queue()
    NODE_OUT_QUEUE = multiprocessing.Queue()
    NODE_EVENT_QUEUE = multiprocessing.Queue()
    NODE_PROCESS = multiprocessing.Process(target=runNode, args=(NODE_IN_QUEUE, NODE_OUT_QUEUE, NODE_EVENT_QUEUE))

    NODE_PROCESS.start()
    NODE_PORT = NODE_OUT_QUEUE.get()
    NODE_ID = NODE_OUT_QUEUE.get()
    print('node started at port', NODE_PORT, 'with id:', NODE_ID)

    GlobalValue.SetGlobalValue('NODE_PORT', NODE_PORT)
    GlobalValue.SetGlobalValue('NODE_ID', NODE_ID)
    GlobalValue.SetGlobalValue('NODE_IN_QUEUE', NODE_IN_QUEUE)
    GlobalValue.SetGlobalValue('NODE_OUT_QUEUE', NODE_OUT_QUEUE)
    GlobalValue.SetGlobalValue('NODE_EVENT_QUEUE', NODE_EVENT_QUEUE)
    GlobalValue.SetGlobalValue('NODE_PROCESS', NODE_PROCESS)

    import os
    import sys

    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "Core"))
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ExternalPackage"))
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UI"))

    from ExternalPackage import dpi_manager
    from PySide2.QtCore import Qt
    from PySide2.QtWidgets import QApplication

    # enable high dpi scale
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(max(1, dpi_manager.scale-0.25))
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    from Core import *
    from UI import *
    mainWin = MainWindow(app)
    mainWin.show()

    ret = app.exec_()
    Manager.OnAppEnd()
    sys.exit(ret)

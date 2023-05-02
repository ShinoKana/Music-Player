import multiprocessing
def runNode(queue: multiprocessing.Queue):
    try:
        import pythonp2p
    except ModuleNotFoundError:
        import sys, crypto
        sys.modules['Crypto'] = crypto
        import pythonp2p
    import threading, time
    class Node(pythonp2p.Node):
        def __init__(self, *args, queue: multiprocessing.Queue = None, **kwargs):
            super().__init__()
            self.queue = queue
            queue.put(self.port)
            self.stop_UDP_send_repeat = False

            def get_command_from_queue():
                if self.queue is not None:
                    while True:
                        command = self.queue.get()
                        funcName, args, kwargs = command
                        print('received command:', funcName, 'args:', args, 'kwargs:', kwargs)
                        try:
                            getattr(self, funcName)(*args, **kwargs)
                        except Exception as e:
                            print('Error when executing command:', e)

            threading.Thread(target=get_command_from_queue, daemon=True).start()

        def udp_send(self, data: bytes, addr: tuple, port: int):
            self.sock.sendto(data, (addr, port))
        def udp_send_repeatly(self, data: bytes, addr: tuple, port: int, interval: float = 0.25, time_limit: float = 10):
            def _send():
                timeCount = 0
                while timeCount < time_limit and not self.stop_UDP_send_repeat:
                    self.sock.sendto(data, (addr, port))
                    time.sleep(interval)
                    timeCount += interval
                self.stop_UDP_send_repeat = False
                print('stop sending')

            threading.Thread(target=_send, daemon=True).start()
        def stop_udp_send_repeatly(self):
            self.stop_UDP_send_repeat = True
    node = Node(queue=queue)
    node.start()

if __name__ == '__main__':
    multiprocessing.freeze_support()

    NODE_QUEUE = multiprocessing.Queue()
    NODE_PROCESS = multiprocessing.Process(target=runNode, args=(NODE_QUEUE,))
    NODE_PROCESS.start()
    NODE_PORT = NODE_QUEUE.get()
    print('node started at port', NODE_PORT)
    import GlobalValue
    GlobalValue.SetGlobalValue('NODE_PORT', NODE_PORT)
    GlobalValue.SetGlobalValue('NODE_QUEUE', NODE_QUEUE)
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

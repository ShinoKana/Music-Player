import platform
from enum import Enum
import copy

class OSType(Enum):
    win = 1
    mac = 2
    @staticmethod
    def CurrentOS():
        if platform.system() == 'Windows':
            return OSType.win
        elif platform.system() == 'Darwin':
            return OSType.mac
        else:
            return None
class OSfunction:
    _OSfunctions = {}
    def __new__(cls, OS:OSType, func):
        if func.__qualname__ in OSfunction._OSfunctions.keys():
            return OSfunction._OSfunctions[func.__qualname__]
        else:
            thisObj = super().__new__(cls)
            thisObj.funcName = func.__qualname__
            thisObj.thisFuncs = {}
            OSfunction._OSfunctions[func.__qualname__] = thisObj
            return thisObj
    def __init__(self, OS:OSType, func):
        self.thisFuncs[OS.value] = copy.copy(func)
    def __call__(self, *args, **kwargs):
        try:
            return self.thisFuncs[OSType.CurrentOS().value](*args, **kwargs)
        except KeyError:
            self.thisFuncs[OSType.CurrentOS().value] = lambda *args, **kwargs: print(f"{self.funcName} is not implemented on {OSType.CurrentOS().name}")
            return self.thisFuncs[OSType.CurrentOS().value](*args, **kwargs)
    def __get__(self, instance=None, owner=None):
        if instance is None:
            pass
        else:
            try:
                return self.thisFuncs[OSType.CurrentOS().value].__get__(instance, owner)
            except:
                self.thisFuncs[OSType.CurrentOS().value] = lambda *args, **kwargs: print(f"{self.funcName} is not implemented on {OSType.CurrentOS().name}")
                return self.thisFuncs[OSType.CurrentOS().value].__get__(instance, owner)
def WinFunction(func):
    return OSfunction(OSType.win, func)
def StaticWinFunction(func):
    return staticmethod(OSfunction(OSType.win, func))
def MacFunction(func):
    return OSfunction(OSType.mac, func)
def StaticMacFunction(func):
    return staticmethod(OSfunction(OSType.mac, func))

class Manager:
    __inited = []
    def __new__(cls, targetClass):
        if not isinstance(targetClass, type):
            raise TypeError("Manager can only be used on class")
        if targetClass.__qualname__ in Manager.__inited:
            return targetClass
        else:
            targetClass._instance =  targetClass.__call__()
            Manager.__inited.append(targetClass.__qualname__)
            targetClass.__init__ = lambda *args: None
            targetClass.__call__ = lambda *args: targetClass._instance
            targetClass.__new__ = lambda *args: targetClass._instance
            return targetClass

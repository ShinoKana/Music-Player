# -*- coding: utf-8 -*-
import sys
from typing import Dict

_globalValues: Dict[str, object] = {}
for module in sys.modules.keys():
    if module.endswith("GlobalValue"):
        _globalValues = sys.modules[module]._globalValues
        break

def SetGlobalValue(key: str, value: object):
    _globalValues[key] = value
def GetGlobalValue(key: str):
    try:
        return _globalValues[key]
    except KeyError:
        return None
def RemoveGlobalValue(key: str):
    try:
        _globalValues.pop(key)
    except KeyError:
        pass
def HasGlobalValue(key: str):
    return key in _globalValues
def ClearGlobalValue():
    _globalValues.clear()
def GetGlobalValueKeys():
    return tuple(_globalValues.keys())
def GetGlobalValueValues():
    return tuple(_globalValues.values())
def GetGlobalValueItems():
    return tuple(_globalValues.items())
def GetGlobalValueDict():
    '''Return a copy of global value dict.'''
    return _globalValues.copy()
def GetOrAddGlobalValue(key: str, defaultValue:object):
    if key in _globalValues:
        return _globalValues[key]
    else:
        _globalValues[key] = defaultValue
        return defaultValue

__all__ = [ 'SetGlobalValue', 'GetGlobalValue', 'RemoveGlobalValue', 'ClearGlobalValue', 'GetGlobalValueKeys', 'GetGlobalValueValues', 'GetGlobalValueItems', 'GetGlobalValueDict',
            'HasGlobalValue', 'GetOrAddGlobalValue' ]
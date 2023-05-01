# -*- coding: utf-8 -*-
from enum import Enum
class SingleEnum(Enum):
    def __eq__(self, other):
        if self.__class__.__qualname__ != other.__class__.__qualname__:
            return False
        if self.value != other.value:
            return False
        if self.name != other.name:
            return False
        return True


__all__ = ["SingleEnum"]
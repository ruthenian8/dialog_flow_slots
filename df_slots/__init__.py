# -*- coding: utf-8 -*-
from .handlers import *
from .slot_types import GroupSlot, ValueSlot, RegexpSlot, FunctionSlot
from .slot_utils import AutoRegisterMixin
from .root import *
from . import conditions
from . import response
from . import processing

__author__ = "Denis Kuznetsov"
__email__ = "ruthenian8@gmail.com"
__version__ = "0.1.0"


class ValueSlot(AutoRegisterMixin, ValueSlot):
    pass


class GroupSlot(AutoRegisterMixin, GroupSlot):
    pass


class RegexpSlot(AutoRegisterMixin, RegexpSlot):
    pass


class FunctionSlot(AutoRegisterMixin, FunctionSlot):
    pass

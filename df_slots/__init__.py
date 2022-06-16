# -*- coding: utf-8 -*-
from logging import root
from df_slots.root import auto_register
from .handlers import *
from .slot_types import *
from .root import *
from . import conditions
from . import response
from . import processing

GroupSlot = auto_register(root)(GroupSlot)
RegexpSlot = auto_register(root)(RegexpSlot)
FunctionSlot = auto_register(root)(FunctionSlot)

__author__ = "Denis Kuznetsov"
__email__ = "ruthenian8@gmail.com"
__version__ = "0.1.0"

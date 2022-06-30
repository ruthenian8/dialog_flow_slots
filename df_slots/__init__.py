# -*- coding: utf-8 -*-
from .handlers import *
from .types import GroupSlot, ValueSlot, RegexpSlot, FunctionSlot
from .utils import register_storage
from .root import root_slot, RootSlot
from .forms import Form, FormState
from . import conditions
from . import response
from . import processing

__author__ = "Denis Kuznetsov"
__email__ = "ruthenian8@gmail.com"
__version__ = "0.1.0"

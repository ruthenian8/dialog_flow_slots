"""
Root
---------------------------
This module contains the root slot and the corresponding type. 
This instance is a singleton, so it will be shared each time you use the add-on.
"""
from typing import List, Union

from .types import BaseSlot, GroupSlot
from .utils import flatten_slot_tree


def singleton(cls: type):
    def singleton_inner(*args, **kwargs):
        if singleton_inner.instance is None:
            singleton_inner.instance = cls(*args, **kwargs)
        return singleton_inner.instance

    singleton_inner.instance = None
    return singleton_inner


@singleton
class RootSlot(GroupSlot):
    def register_slots(self, slots: Union[List[BaseSlot], BaseSlot]) -> dict:
        if isinstance(slots, BaseSlot):
            slots = [slots]
        for slot in slots:
            add_nodes, _ = flatten_slot_tree(slot)
            self.children.update(add_nodes)


root_slot = RootSlot(name="root_slot")

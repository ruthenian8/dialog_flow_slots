"""
Root
---------------------------
This module contains the root slot and the corresponding type. 
This instance is a singleton, so it will be shared each time you use the add-on.
"""
from typing import List, Union, Tuple, Dict

from .types import BaseSlot, GroupSlot


def singleton(cls: type):
    def singleton_inner(*args, **kwargs):
        if singleton_inner.instance is None:
            singleton_inner.instance = cls(*args, **kwargs)
        return singleton_inner.instance

    singleton_inner.instance = None
    return singleton_inner


def flatten_slot_tree(node: BaseSlot) -> Tuple[Dict[str, BaseSlot], Dict[str, BaseSlot]]:
    add_nodes = {node.name: node}
    remove_nodes = {}
    if node.has_children():
        for name, child in node.children.items():
            remove_nodes.update({child.name: child})
            child.name = "/".join([node.name, name])
            child_add_nodes, child_remove_nodes = flatten_slot_tree(child)
            add_nodes.update(child_add_nodes)
            remove_nodes.update(child_remove_nodes)
    return add_nodes, remove_nodes


@singleton
class RootSlot(GroupSlot):
    def register_slots(self, slots: Union[List[BaseSlot], BaseSlot]) -> dict:
        if isinstance(slots, BaseSlot):
            slots = [slots]
        for slot in slots:
            add_nodes, _ = flatten_slot_tree(slot)
            self.children.update(add_nodes)


root_slot = RootSlot(name="root_slot")

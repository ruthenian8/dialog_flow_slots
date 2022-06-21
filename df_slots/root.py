from typing import List, Union, Dict, Tuple

from .slot_types import BaseSlot, GroupSlot
from .slot_utils import flatten_slot_tree


def singleton(cls: type):
    def singleton_inner(*args, **kwargs):
        if singleton_inner.instance is None:
            singleton_inner.instance = cls(*args, **kwargs)
        return singleton_inner.instance
    
    singleton_inner.instance = None
    return singleton_inner


@singleton
class RootSlot(GroupSlot):
    freeze: bool = False

    def register_slots(self, slots: Union[List[BaseSlot], BaseSlot]) -> dict:
        if isinstance(slots, BaseSlot):
            slots = [slots]
        for slot in slots:
            add_nodes, _ = flatten_slot_tree(slot)
            self.children.update(add_nodes)

    def keep_slots(self, slots: List[BaseSlot]):
        new_root_children = dict()
        for slot in slots:
            if not slot.has_children():
                new_root_children[slot.name] = self.children[slot.name]
            else:
                new_root_children.update({name: _slot for name, _slot in self.children.items() if name.startswith(slot.name)})
        self.children = new_root_children


root = RootSlot(name="root_slot")


class AutoRegisterMixin:
    def __init__(self, *, name: str, **data) -> None:
        super().__init__(name=name, **data)
        if root.freeze:
            return
        add_nodes, remove_nodes = flatten_slot_tree(self)
        for key in remove_nodes.keys():
            if key in root.children:
                root.children.pop(key)
        root.children.update(add_nodes)

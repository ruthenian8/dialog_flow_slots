import functools
from typing import List, Union, Dict, Tuple

from df_engine.core import Context, Actor
from df_engine.core.actor import ActorStage
from .slot_types import BaseSlot

root = dict()
freeze_root = False


def register_storage(actor: Actor, storage: Dict[str, str] = None) -> None:
    if not storage:
        storage = dict()

    def create_slot_storage_inner(ctx: Context, actor: Actor, *args, **kwargs) -> None:
        if "slots" in ctx.framework_states:
            return
        ctx.framework_states["slots"] = storage
        return

    actor.handlers[ActorStage.CONTEXT_INIT] = actor.handlers.get(ActorStage.CONTEXT_INIT, []) + [
        create_slot_storage_inner
    ]


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


def register_slots(slots: Union[List[BaseSlot], BaseSlot], root: dict = root) -> dict:
    if isinstance(slots, BaseSlot):
        slots = [slots]
    for slot in slots:
        add_nodes, _ = flatten_slot_tree(slot)
        root.update(add_nodes)
    return root


def register_root_slots(slots: List[BaseSlot], root: dict = root):
    new_root = dict()
    for slot in slots:
        if not slot.has_children():
            new_root[slot.name] = root[slot.name]
        else:
            new_root.update({name: _slot for name, _slot in root.items() if name.startswith(slot.name)})
    return new_root


def auto_register(root: dict = root):
    def auto_register_decorator(cls):
        @functools.wraps(cls)
        def registry_wrapper(*args, **kwargs):
            slot_instance = cls(*args, **kwargs)
            registry_wrapper.freeze = freeze_root
            if registry_wrapper.freeze:
                return slot_instance

            add_nodes, remove_nodes = flatten_slot_tree(slot_instance)
            for key in remove_nodes.keys():
                root.pop(key)
            root.update(add_nodes)
            return slot_instance

        registry_wrapper.freeze = False

        return registry_wrapper

    return auto_register_decorator

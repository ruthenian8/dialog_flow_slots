import functools
from typing import List, Union, Dict

from df_engine.core import Context, Actor
from df_engine.core.actor import ActorStage
from .slot_types import BaseSlot

root = dict()
freeze_root = False


def register_root(actor: Actor, root: Dict[str, BaseSlot] = root) -> None:
    def create_slot_storage_inner(ctx: Context, actor: Actor, *args, **kwargs) -> None:
        if "slots" in ctx.framework_states:
            return
        ctx.framework_states["slots"] = root
        return

    actor.handlers[ActorStage.CONTEXT_INIT] = actor.handlers.get(ActorStage.CONTEXT_INIT, []) + [
        create_slot_storage_inner
    ]


def flatten_slot_tree(node: BaseSlot) -> Dict[str, BaseSlot]:
    nodes = {node.name: node}
    if node.has_children():
        for name, child in node.children.items():
            old_child_name = child.name
            child.name = ".".join([node.name, name])
            nodes.update(flatten_slot_tree(child))
            child.name = old_child_name
    return nodes


def register_slots(slots: Union[List[BaseSlot], BaseSlot], root: dict = root) -> dict:
    if isinstance(slots, BaseSlot):
        slots = [slots]
    for slot in slots:
        root.update(flatten_slot_tree(slot))
    return root


def register_root_slots(slots: List[BaseSlot], root: dict = root):
    names = [slot.name for slot in slots]
    root = {name: slot for name, slot in root.items() if any(map(lambda x: name.startswith(x), names))}
    return root


def auto_register(root: dict = root):
    def auto_register_decorator(cls):
        @functools.wraps(cls)
        def registry_wrapper(*args, **kwargs):
            slot_instance = cls(*args, **kwargs)
            registry_wrapper.freeze = freeze_root
            if registry_wrapper.freeze:
                return slot_instance

            children_mapping = flatten_slot_tree(slot_instance)
            root.update(children_mapping)
            return slot_instance

        registry_wrapper.freeze = False

        return registry_wrapper

    return auto_register_decorator

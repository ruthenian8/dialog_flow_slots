import functools
from typing import Callable, List, Union, Dict, Tuple

from pydantic.main import ModelMetaclass

from df_engine.core import Context, Actor
from df_engine.core.actor import ActorStage
from .slot_types import BaseSlot

root = dict()
freeze_root = False


def register_storage(actor: Actor, storage: Dict[str, str] = None) -> None:
    """
    Add a callback for context processing to the :py:class:`~Actor` class.
    
    Parameters
    ----------
    actor: :py:class:`~Actor`
        DF engine Actor instance.
    storage: dict
        A dictionary that holds slot values. Typically, you don't need to override this parameter.
    """
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
    """
    Utility function to flatten a nested slot structure.
    Returns a dictionary of slot names that should be added to the root namespace
    and a dictionary of old slot names to expel from the root namespace.

    Parameters
    -----------
    node: :py:class:`~BaseSlot`
        Parent node that should be flattened.
    """
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
    """
    Manually add slots to the slot root. Overrides slots that have been set previously.

    Parameters
    ----------
    slots: List[:py:class:`~BaseSlot`]
        Slot instances to add to the slot root.
    """
    if isinstance(slots, BaseSlot):
        slots = [slots]
    for slot in slots:
        add_nodes, _ = flatten_slot_tree(slot)
        root.update(add_nodes)
    return root


def register_root_slots(slots: List[BaseSlot], root: dict = root) -> dict:
    """
    Filter slots in the slot root, leaving only the specified slots. Returns a new slot root.

    Parameters
    ----------
    slots: List[:py:class:`~BaseSlot`]
        Slot instances to kkep in the slot root.    
    """
    new_root = dict()
    for slot in slots:
        if not slot.has_children():
            new_root[slot.name] = root[slot.name]
        else:
            new_root.update({name: _slot for name, _slot in root.items() if name.startswith(slot.name)})
    return new_root

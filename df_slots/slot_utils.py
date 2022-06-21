from typing import Dict, Tuple

from df_engine.core import Context, Actor
from df_engine.core.actor import ActorStage

from .slot_types import BaseSlot


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



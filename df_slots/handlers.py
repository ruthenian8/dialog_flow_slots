from typing import Dict, Optional, List

from df_engine.core import Context, Actor

from .slot_types import BaseSlot, GroupSlot
from .root import root


def extract(ctx: Context, actor: Actor, slots: Optional[List[str]] = None, root: dict = root) -> list:
    storage = ctx.framework_states.get("slots")
    if not storage:
        raise ValueError("Failed to get slot values: root slot not in context")

    target_names = slots or list(root.keys())
    results = []
    for name in target_names:
        if name not in root:
            results.append(None)
            continue
        target_slot: BaseSlot = root.get(name)
        val = target_slot.extract_value(ctx, actor)
        if isinstance(target_slot, GroupSlot):
            ctx.framework_states["slots"].update(val)
        else:
            ctx.framework_states["slots"][name] = val
        results.append(val)

    return results


def get_values(ctx: Context, actor: Actor, slots: Optional[List[str]] = None) -> list:
    storage = ctx.framework_states.get("slots")
    if not storage:
        raise ValueError("Failed to get slot values: storage slot not in context")

    target_names = slots or list(storage.keys())
    return [storage.get(name).value for name in target_names if name in storage]


def get_filled_template(template: str, ctx: Context, actor: Actor, slots: Optional[List[str]] = None) -> str:

    filler_nodes: Dict[str, BaseSlot]
    if slots:
        filler_nodes = {key: value for key, value in root.items() if key in root}
    else:
        filler_nodes = {key: value for key, value in root.items() if "/" not in key}

    for _, slot in filler_nodes.items():
        template = slot.fill_template(template)(ctx, actor)

    return template

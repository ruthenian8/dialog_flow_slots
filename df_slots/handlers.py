from typing import Optional, List
import logging

from df_engine.core import Context, Actor

from .slot_types import BaseSlot, GroupSlot
from .root import root

logger = logging.getLogger(__name__)


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


def get_filled_template(
    template: str, ctx: Context, actor: Actor, slots: Optional[List[str]] = None
) -> str:
    storage = ctx.framework_states.get("slots")
    if not storage:
        logger.info("Failed to get slot values: storage slot not in context")
        return template
    
    if slots:
        filler = {key: value for key, value in storage.items() if key in slots}
    else:
        filler = slots

    return template.format(**filler)

from typing import Optional, List
import logging

from df_engine.core import Context, Actor

from .slot_types import BaseSlot
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
        val = root.get(name).extract_value(ctx, actor)
        storage[name] = val
        results.append(val)

    return results


def get_values(ctx: Context, actor: Actor, slots: Optional[List[str]] = None) -> list:
    storage = ctx.framework_states.get("slots")
    if not storage:
        raise ValueError("Failed to get slot values: storage slot not in context")

    target_names = slots or list(storage.keys())
    return [storage.get(name).value for name in target_names if name in storage]


def get_filled_template(
    template: str, ctx: Context, actor: Actor, slot: Optional[str] = None, root: dict = root
) -> str:
    if not slot:
        return template.format(**root)
    target_slot: BaseSlot = root.get(slot)
    if not target_slot:
        logger.info("Failed to fill the template: target slot not in context")
    return target_slot.fill_template(template)(ctx, actor)

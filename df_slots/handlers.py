from typing import Optional, List
import logging

from df_engine.core import Context, Actor

from .slot_types import BaseSlot

logger = logging.getLogger(__name__)


def extract(ctx: Context, actor: Actor, slots: Optional[List[str]] = None) -> list:
    root = ctx.framework_states.get("slots")
    if not root:
        raise ValueError("Failed to get slot values: root slot not in context")

    target_names = slots or list(root.keys())
    results = [root.get(name).extract_value(ctx, actor) for name in target_names if name in root]
    return results


def get_values(ctx: Context, actor: Actor, slots: Optional[List[str]] = None) -> list:
    root = ctx.framework_states.get("slots")
    if not root:
        raise ValueError("Failed to get slot values: root slot not in context")

    target_names = slots or list(root.keys())
    return [root.get(name).value for name in target_names if name in root]


def get_filled_template(template: str, ctx: Context, actor: Actor, slot: Optional[str] = None) -> str:
    root = ctx.framework_states.get("slots")
    if not root:
        logger.info("Failed to fill the template: root slot not in context")
        return template

    if not slot:
        return template.format(**root)
    target_slot: BaseSlot = root.get(slot)
    if not target_slot:
        logger.info("Failed to fill the template: target slot not in context")
    return target_slot.fill_template(template)(ctx, actor)

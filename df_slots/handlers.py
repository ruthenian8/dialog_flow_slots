from typing import Optional, List
import logging

from df_engine.core import Context, Actor

from .slot_types import BaseSlot


def extract(ctx: Context, actor: Actor, slots: Optional[List[str]]=None) -> list:
    root = ctx.framework_states.get("slots")
    if not root:
        raise ValueError("Failed to get slot values: root slot not in context")
    
    target_names = slots or list(root.keys())
    results = [root.get(name).extract_value(ctx, actor) for name in target_names]
    return results


def get_values(ctx: Context, actor: Actor, slots: Optional[List[str]]=None) -> list:
    root = ctx.framework_states.get("slots")
    if not root:
        raise ValueError("Failed to get slot values: root slot not in context")
        
    target_names = slots or list(root.keys())
    return [item.value for key, item in root.items() if key in target_names]


def get_filled_template(template: str, ctx: Context, actor: Actor, slot: Optional[str]=None) -> str:
    root = ctx.framework_states.get("slots")
    if not root:
        logging.warning("Failed to fill the template: root slot not in context")
        return template
    
    if not slot:
        return template.format(**root)
    target_slot: BaseSlot = root.get(slot)
    if not target_slot:
        logging.warning("Failed to fill the template: target slot not in context")
    return target_slot.fill_template(template)(ctx, actor)

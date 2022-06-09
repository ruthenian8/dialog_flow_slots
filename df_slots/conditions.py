import logging
from typing import Callable

from slot_types import BaseSlot

from df_engine.core import Context, Actor


def slot_is_set(slot: str) -> Callable:
    def is_set_inner(ctx: Context, actor: Actor) -> bool:
        root = ctx.framework_states.get("slots")
        if not root:
            logging.warning("Failed to check slot: root slot not in context")
            return False
        ctx_slot: BaseSlot = root.get(slot)
        if ctx_slot is None:
            logging.warning("Slot not in root")
            return False

        return ctx_slot.is_set()

    return is_set_inner
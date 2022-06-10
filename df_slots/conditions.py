import logging
from typing import Callable, List
from functools import partial

from df_engine.core import Context, Actor

logger = logging.getLogger(__name__)


def is_set(slots: List[str], use_all: bool = True, use_any: bool = False) -> Callable:
    if use_all == use_any:
        raise ValueError("Parameters `use_all` and `use_any` are mutually exclusive.")

    def is_set_inner(ctx: Context, actor: Actor) -> bool:
        root = ctx.framework_states.get("slots")
        if not root:
            logger.info("Failed to check slot: root slot not in context")
            return False
        slots_set = [root.get(slot).is_set() if slot in root else False for slot in slots]
        if use_all:
            return all(slots_set)
        if use_any:
            return any(slots_set)

    return is_set_inner


all_set = partial(is_set, use_all=True, use_any=False)

any_set = partial(is_set, use_any=True, use_all=False)

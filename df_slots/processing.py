import logging
from typing import Union, List, Callable
from functools import partial

from df_engine.core import Context, Actor
from df_generics import Response

from df_slots.slot_types import BaseSlot, GroupSlot

from .root import root

logger = logging.getLogger(__name__)


def extract(slots: Union[None, List[str]], root: dict = root) -> Callable:
    def extract_inner(ctx: Context, actor: Actor):
        storage = ctx.framework_states.get("slots")
        if storage is None:
            logger.warning("Failed to extract slots: storage not in context")
            return ctx

        target_names = slots or list(root.keys())
        for key in target_names:
            if not key in root:
                continue
            target_slot: BaseSlot = root.get(key)
            val = target_slot.extract_value(ctx, actor)
            if isinstance(target_slot, GroupSlot):
                ctx.framework_states["slots"].update(val)
            else:
                ctx.framework_states["slots"][key] = val
        return ctx

    return extract_inner


def fill_template(root: dict = root):
    def fill_inner(ctx: Context, actor: Actor):

        response = ctx.framework_states["actor"]["processed_node"].response
        if callable(response):
            response = response(ctx, actor)
        if isinstance(response, str):
            ctx.framework_states["actor"]["processed_node"].response = response.format(**root)
        elif isinstance(response, Response):
            response.text = response.text.format(**root)
            ctx.framework_states["actor"]["processed_node"].response = response

        return ctx

    return fill_inner


def is_set(slots: List[str], use_all: bool = True, use_any: bool = False, root: dict = root) -> Callable:
    if use_all == use_any:
        raise ValueError("Parameters `use_all` and `use_any` are mutually exclusive.")

    def is_set_inner(ctx: Context, actor: Actor) -> bool:
        slots_set = [root.get(slot).is_set() if slot in root else False for slot in slots]
        if use_all:
            return all(slots_set)
        if use_any:
            return any(slots_set)

    return is_set_inner


is_set_all = partial(is_set, use_all=True, use_any=False)

is_set_any = partial(is_set, use_any=True, use_all=False)

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
    def fill_inner(ctx: Context, actor: Actor) -> Union[Response, str]:

        # get current node response
        response = ctx.framework_states["actor"]["processed_node"].response
        if callable(response):
            response = response(ctx, actor)

        # process response
        filler_nodes = {key: value for key, value in root.items() if "/" not in key}
        new_template = response if isinstance(response, str) else response.text
        for _, slot in filler_nodes.items():
            new_template = slot.fill_template(new_template)(ctx, actor)

        # assign to node
        if isinstance(response, str):
            ctx.framework_states["actor"]["processed_node"].response = new_template
        elif isinstance(response, Response):
            response.text = new_template
            ctx.framework_states["actor"]["processed_node"].response = response

        return ctx

    return fill_inner

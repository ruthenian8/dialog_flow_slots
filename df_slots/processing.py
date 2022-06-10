import logging
from typing import Union, List, Callable

from df_engine.core import Context, Actor
from df_generics import Response

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
            val = root.get(key).extract_value(ctx, actor)
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

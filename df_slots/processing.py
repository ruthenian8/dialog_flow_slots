import logging
from typing import Union, List, Callable

from df_engine.core import Context, Actor
from df_generics import Response


def extract(slots: Union[None, List[str]]) -> Callable:
    def extract_inner(ctx: Context, actor: Actor):
        root = ctx.framework_states.get("slots")
        if not root:
            logging.warning("Failed to extract slots: root slot not in context")
            return ctx
        
        target_names = slots or list(root.keys())
        for key in target_names:
            ctx.framework_states.get("slots").get(key).init_value(ctx, actor)
        return ctx

    return extract_inner


def fill_template():
    def fill_inner(ctx: Context, actor: Actor):
        root = ctx.framework_states.get("slots")
        if not root:
            logging.warning("Failed to fill the template: root slot not in context")
            return ctx

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

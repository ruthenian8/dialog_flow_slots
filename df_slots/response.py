from typing import Union

from df_generics import Response
from df_engine.core import Context, Actor

from .root import root


def fill_template(template: Union[str, Response]):
    def fill_inner(ctx: Context, actor: Actor):

        filler_nodes = {key: value for key, value in root.items() if "/" not in key}

        new_template = template if isinstance(template, str) else template.text
        for _, slot in filler_nodes.items():
            new_template = slot.fill_template(new_template)(ctx, actor)

        if isinstance(template, Response):
            template.text = new_template
            return template

        return new_template

    return fill_inner

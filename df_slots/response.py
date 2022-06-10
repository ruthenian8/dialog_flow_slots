from typing import Union
import logging

from df_generics import Response
from df_engine.core import Context, Actor

from .root import root

logger = logging.getLogger(__name__)


def fill_template(template: Union[str, Response], root: dict = root):
    def fill_inner(ctx: Context, actor: Actor):
        if isinstance(template, Response):
            template.text = template.text.format(**root)
            return template
        return template.format(**root)

    return fill_inner

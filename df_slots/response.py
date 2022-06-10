from typing import Union
import logging

from df_generics import Response
from df_engine.core import Context, Actor

logger = logging.getLogger(__name__)


def fill_template(template: Union[str, Response]):
    def fill_inner(ctx: Context, actor: Actor):
        root = ctx.framework_states.get("slots")
        if not root:
            logger.info("Failed to fill the template: root slot not in context")
            return template
        if isinstance(template, Response):
            template.text = template.text.format(**root)
            return template
        return template.format(**root)

    return fill_inner

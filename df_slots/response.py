from typing import Union
import logging

from df_generics import Response
from df_engine.core import Context, Actor

logger = logging.getLogger(__name__)


def fill_template(template: Union[str, Response]):
    def fill_inner(ctx: Context, actor: Actor):
        storage = ctx.framework_states.get("slots")
        if not storage:
            logger.info("Failed to get slot values: storage slot not in context")
            return template

        if isinstance(template, Response):
            template.text = template.text.format(**storage)
            return template
        return template.format(**storage)

    return fill_inner

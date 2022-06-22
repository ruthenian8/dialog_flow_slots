from typing import Union

from df_generics import Response
from df_engine.core import Context, Actor

from .root import root


def fill_template(template: Union[str, Response]):
    """
    Fill a template with slot values.
    Response should be an instance of :py:class:`~str` or of the :py:class:`~Response` class from df_generics add-on.

    Arguments
    ---------
    template: Union[str, :py:class:`~Response`]
        Template to fill. Names of slots to be used should be placed in curly braces: 'Username is {profile/username}'.
    """
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

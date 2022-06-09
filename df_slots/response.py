import logging

from df_engine.core import Context, Actor


def fill_template(template: str):
    def fill_inner(ctx: Context, actor: Actor):
        root = ctx.framework_states.get("slots")
        if not root:
            logging.warning("Failed to fill the template: root slot not in context")
            return template
        return template.format(**root)
    
    return fill_inner
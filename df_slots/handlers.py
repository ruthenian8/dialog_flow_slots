"""
Handlers
---------------------------
This module is for general functions that can be used in processing, conditions, or responses.
"""
import logging
from typing import Dict, Optional, List

from df_engine.core import Context, Actor

from .types import BaseSlot, GroupSlot
from .root import root_slot as root

logger = logging.getLogger(__name__)


def extract(ctx: Context, actor: Actor, slots: Optional[List[str]] = None) -> list:
    """
    Extract the specified slots and return the received values as a list.
    If the value of a particular slot cannot be extracted, None is included instead.
    If `slots` argument is not provided, all slots will be extracted and returned.

    Parameters
    ----------

    ctx: :py:class:`~Context`
        DF engine context
    actor: :py:class:`~Actor`
        DF engine actor
    slots: Optional[List[str]]
        List of slot names to extract.
        Names of slots inside groups should be prefixed with group names, separated by '/': profile/username.
    """
    target_names = slots or [key for key in root.children.keys() if "/" not in key]

    storage = ctx.framework_states.get("slots")
    if storage is None or ctx.validation is True:
        logger.warning("Failed to extract slot values: storage missing.")
        return [None] * len(target_names)

    results = []
    for name in target_names:
        if name not in root.children:
            results.append(None)
            continue
        target_slot: BaseSlot = root.children.get(name)
        val = target_slot.extract_value(ctx, actor)
        if isinstance(target_slot, GroupSlot):
            ctx.framework_states["slots"].update(val)
        else:
            ctx.framework_states["slots"][name] = val
        results.append(val)

    return results


def get_values(ctx: Context, actor: Actor, slots: Optional[List[str]] = None) -> list:
    """
    Get values of the specified slots, assuming that they have been extracted beforehand.
    If slot argument is omitted, values of all slots will be returned.

    Parameters
    ----------

    ctx: :py:class:`~Context`
        DF engine context
    actor: :py:class:`~Actor`
        DF engine actor
    slots: Optional[List[str]]
        List of slot names to extract.
        Names of slots inside groups should be prefixed with group names, separated by '/': profile/username.
    """
    target_names = slots or list(root.children.keys())

    storage = ctx.framework_states.get("slots")
    if storage is None or ctx.validation is True:
        return [None] * len(target_names)

    return [storage.get(name) for name in target_names if name in storage]


def get_filled_template(template: str, ctx: Context, actor: Actor, slots: Optional[List[str]] = None) -> str:
    """
    Fill a template string with slot values.

    Parameters
    ----------

    template: str
        Template to fill. Names of slots to be used should be placed in curly braces: 'Username is {profile/username}'.
    ctx: :py:class:`~Context`
        DF engine context
    actor: :py:class:`~Actor`
        DF engine actor
    slots: Optional[List[str]]
        List of slot names to extract.
        Names of slots inside groups should be prefixed with group names, separated by '/': profile/username.
    """
    filler_slots: Dict[str, BaseSlot]
    if slots:
        filler_slots = {key: value for key, value in root.children.items() if key in slots}
    else:
        filler_slots = {key: value for key, value in root.children.items() if "/" not in key}

    if not filler_slots:
        raise ValueError(
            "Given subset does not intersect with slots in root: {}".format(", ".join(slots) if slots else str(None))
        )

    for _, slot in filler_slots.items():
        template = slot.fill_template(template)(ctx, actor)

    return template

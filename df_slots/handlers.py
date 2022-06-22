from typing import Dict, Optional, List

from df_engine.core import Context, Actor
from df_generics import Response

from .slot_types import BaseSlot, GroupSlot
from .root import root


def extract(ctx: Context, actor: Actor, slots: Optional[List[str]] = None, root: dict = root) -> list:
    """
    Extract the specified slots and return the received values as a list.
    If the value of a particular slot cannot be extracted, None is included instead.
    If `slots` argument is not provided, all slots will be extracted and returned.

    Arguments
    ---------
    ctx: :py:class:`~Context`
        DF engine context
    actor: :py:class:`~Actor`
        DF engine actor
    slots: Optional[List[str]]
        List of slot names to extract. 
        Names of slots inside groups should be prefixed with group names, separated by '/': profile/username.
    """
    storage = ctx.framework_states.get("slots")
    if storage is None:
        raise ValueError("Failed to get slot values: root slot not in context")

    target_names = slots or [key for key in root.keys() if "/" not in key]
    results = []
    for name in target_names:
        if name not in root:
            results.append(None)
            continue
        target_slot: BaseSlot = root.get(name)
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

    Arguments
    ---------
    ctx: :py:class:`~Context`
        DF engine context
    actor: :py:class:`~Actor`
        DF engine actor
    slots: Optional[List[str]]
        List of slot names to extract. 
        Names of slots inside groups should be prefixed with group names, separated by '/': profile/username.
    """
    storage = ctx.framework_states.get("slots")
    if storage is None:
        raise ValueError("Failed to get slot values: storage slot not in context")

    target_names = slots or list(root.keys())
    return [storage.get(name) for name in target_names if name in storage]


def get_filled_template(template: str, ctx: Context, actor: Actor, slots: Optional[List[str]] = None) -> str:
    """
    Fill a template string with slot values.

    Arguments
    ---------
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
    filler_nodes: Dict[str, BaseSlot]
    if slots:
        filler_nodes = {key: value for key, value in root.items() if key in slots}
    else:
        filler_nodes = {key: value for key, value in root.items() if "/" not in key}

    if not filler_nodes:
        raise ValueError(
            "Given subset does not intersect with slots in root: {}".format(", ".join(slots) if slots else str(None))
        )

    for _, slot in filler_nodes.items():
        template = slot.fill_template(template)(ctx, actor)

    return template

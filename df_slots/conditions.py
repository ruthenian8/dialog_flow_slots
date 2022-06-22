from typing import List, Callable
from functools import partial

from df_engine.core import Context, Actor

from .root import root


def is_set(slots: List[str], use_all: bool = True, use_any: bool = False) -> Callable:
    """
    Check, if any of the passed slots have been set.
    Any or all slot names from the list can be considered.

    Arguments
    ---------
    slots: List[str]
        List of slot names to extract. 
        Names of slots inside groups should be prefixed with group names, separated by '/': profile/username.
    """
    if use_all == use_any:
        raise ValueError("Parameters `use_all` and `use_any` are mutually exclusive.")

    def is_set_inner(ctx: Context, actor: Actor) -> bool:
        slots_set = [ctx.framework_states.get("slots", {}).get(slot) for slot in slots]
        if use_all:
            return all(slots_set)
        if use_any:
            return any(slots_set)

    return is_set_inner


is_set_all = partial(is_set, use_all=True, use_any=False)
is_set_all.__doc__ = is_set.__doc__

is_set_any = partial(is_set, use_any=True, use_all=False)
is_set_any.__doc__ = is_set.__doc__

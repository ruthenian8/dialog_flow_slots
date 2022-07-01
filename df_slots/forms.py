"""
Forms
---------------------------
This module holds the :class:`~Form` class that can be used to create a global form-filling policy.
"""
from typing import Optional, Callable, List, Dict
from enum import Enum, auto
from random import choice
from math import inf
from collections import Counter

import df_engine.labels as lbl
from pydantic import BaseModel, Field, PrivateAttr, validate_arguments

from df_engine.core import Context, Actor
from df_engine.core.types import NodeLabel3Type, NodeLabel2Type

from .root import root_slot
from .handlers import get_values
from .conditions import is_set_all
from .utils import requires_storage, FORM_STORAGE_KEY


class FormState(Enum):
    INACTIVE = auto()
    ACTIVE = auto()
    COMPLETE = auto()
    FAILED = auto()


class FormPolicy(BaseModel):
    """
    This class holds a mapping between slots and nodes that are required to set them.
    To make this policy affect the dialogue and enforce transitions to required nodes,
    you should include `to_next_slot` method into `GLOBAL` `TRANSITIONS` of your :py:class:`~Script`,
    while `update_form_state` should be included into `GLOBAL` `PRE_TRANSITION_PROCESSING`.
    Check out the method documentation for details.

    .. code-block::
        :caption: Sample form class usage.

        slot_1 = RegexpSlot(...)
        form_1 = Form(name=..., mapping={slot_1.name: [("flow_1", "node_1")]})

        script = {
            GLOBAL: {
                TRANSITIONS: {
                    form_1.to_next_slot(0.1): cnd.true()
                },
                PRE_TRANSITION_PROCESSING: {
                    "proc_1": form_1.update_form_state()
                }
            }
            "flow_1": {
                "node_1": {
                    RESPONSE: "Some response",
                    PRE_TRANSITION_PROCESSING: {
                        "extraction": slot_proc.extract([slot_1.name])
                    }
                }
            }
        }

    """

    name: str
    mapping: Dict[str, List[NodeLabel2Type]] = Field(default_factory=dict)
    allowed_repeats: int = Field(default=0, gt=-1)
    _is_fillable: bool = PrivateAttr(default=True)
    _node_cache: Dict[NodeLabel2Type, int] = PrivateAttr(default_factory=Counter)

    def __init__(self, name: str, mapping: Dict[str, List[NodeLabel2Type]], *, allowed_repeats: int = 0, **data):
        """
        Create a new form.

        Parameters
        ----------

        name: str
            The name of the form. It is used to save states of the form to the current context and keep track of them.
        mapping: Dict[str, List[:class:`~NodeLabel2Type`]]
            A dictionary that maps slot names to nodes. Nodes should be described with (flow_name, node_name) tuples.
            In case one node should set multiple slots, include them in a common group slot
            and use the name of the group slot as a key.
            Since `dict` type is ordered since python 3.6, slots will be iterated over in the order
            that you pass them in.
        allowed_repeats: int = 0
            This parameter regulates, how many times the policy can return to an already visited node.
            If the limit on allowed repeats has been reached, the policy will stop to affect transitions.
        """
        super().__init__(name=name, mapping=mapping, allowed_repeats=allowed_repeats, **data)

    def to_next_label(self, priority: Optional[float] = None) -> Callable[[Context, Actor], NodeLabel3Type]:
        """
        This method checks, if all slots from the form have been set and returns transitions to required nodes,
        if there remain any. Returns an always ignored transition otherwise.

        Parameters
        ----------

        priority: Optional[float] = None
            The weight that will be assigned to the transition.
            Defaults to 1 (default priority in df_engine :py:class:`~Actor`).

        """

        def to_next_slot_inner(ctx: Context, actor: Actor) -> NodeLabel3Type:
            current_priority = priority or actor.label_priority
            for slot_name, node_list in self.mapping.items():
                is_set = root_slot.children[slot_name].is_set()(ctx, actor)
                if is_set is True:
                    continue
                print("nodes for slot: ", node_list, sep=" ")
                print("node cache: ", self._node_cache, sep=" ")
                filtered_node_list = [
                    node for node in node_list if self._node_cache.get(node, 0) <= self.allowed_repeats
                ]  # assert that the visit limit has not been reached for all of the nodes.
                print("nodes not in cache: ", filtered_node_list, sep=" ")
                # if len(filtered_node_list) == 0:
                #     self._is_fillable = False
                #     return lbl.to_fallback(-inf)(ctx, actor)

                # chosen_node = choice(filtered_node_list)
                chosen_node = choice(filtered_node_list or node_list)
                if not ctx.validation:
                    self._node_cache.update([chosen_node])  # update visit counts
                print((*chosen_node, current_priority))
                return (*chosen_node, current_priority)

        return to_next_slot_inner

    def is_active(self):
        """
        This method produces a df_engine condition that yields `True` if the state of the form has been set to
        'active' or `False` otherwise.
        """

        @requires_storage("Form storage has not been registered.", storage_key=FORM_STORAGE_KEY, return_val=False)
        def is_active_inner(ctx: Context, actor: Actor) -> bool:
            state = ctx.framework_states[FORM_STORAGE_KEY].get(self.name, FormState.INACTIVE)
            return state == FormState.ACTIVE

        return is_active_inner

    @validate_arguments
    def update_form_state(self, state: Optional[FormState] = None):
        """
        This method updates the form state that is stored in the context.
        It has a twofold application.

        Firstly, it should be called in `GLOBAL` `PRE_TRANSITION_PROCESSING` without any arguments
        to keep track of the form state.

        Secondly, it should be called in `PRE_TRANSITION_PROCESSING of any node
        with `FormState.active` as an argument to activate the form.

        """

        def update_inner(ctx: Context, actor: Actor) -> Context:
            if not ctx.validation and FORM_STORAGE_KEY not in ctx.framework_states:
                raise ValueError("Form storage has not been registered.")

            if state:
                ctx.framework_states[FORM_STORAGE_KEY][self.name] = state
                return ctx

            if self.name not in ctx.framework_states[FORM_STORAGE_KEY]:
                ctx.framework_states[FORM_STORAGE_KEY][self.name] = FormState.INACTIVE
                return ctx

            if self._is_fillable is False:
                ctx.framework_states[FORM_STORAGE_KEY][self.name] = FormState.FAILED
                return ctx

            if is_set_all(list(self.mapping.keys()))(ctx, actor) is True:
                ctx.framework_states[FORM_STORAGE_KEY][self.name] = FormState.COMPLETE
            return ctx

        return update_inner

    def get_values(self):
        def get_values_inner(ctx: Context, actor: Actor):
            slots = list(self.mapping.keys())
            return get_values(ctx, actor, slots)

        return get_values_inner

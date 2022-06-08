from typing import Union, Callable, Optional, List
from copy import copy

from pydantic import BaseModel, Extra

from df_engine.core import Context, Actor
from df_engine.core.types import ActorStage

from df_generics import Response

from .slot_types import BaseSlot, ValueSlot, GroupSlot


class SlotHandler(BaseModel):
    class Config:
        extra = Extra.allow

    def __deepcopy__(self, *args, **kwargs):
        return copy(self)

    def has_slot(self, slot: str) -> bool:
        target = self
        for subslot in slot.split("."):
            try:
                target = getattr(target, subslot)
            except AttributeError:
                return False
        return True

    def slot_is_set(self, slot: str) -> bool:
        slot = self.get_slot(slot)
        if not slot:
            return False
        return slot.is_set()

    def add_slot(self, slot: BaseSlot) -> None:
        setattr(self, slot.name, slot)

    def get_slot(self, slot: str) -> BaseSlot:
        target = self
        for subslot in slot.split("."):
            try:
                target = getattr(target, subslot)
            except AttributeError:
                return None
        return target


def create_slot_handler(actor: Actor, slots: Optional[List[BaseSlot]] = None) -> None:
    if slots is None:
        slots = []

    def create_slot_storage_inner(ctx: Context, actor: Actor, *args, **kwargs) -> None:
        if "slots" in ctx.framework_states:
            return
        handler = SlotHandler()
        for slot in slots:
            handler.add_slot(slot)
        ctx.framework_states["slots"] = handler
        return

    actor.handlers[ActorStage.CONTEXT_INIT] = actor.handlers.get(ActorStage.CONTEXT_INIT, []) + [create_slot_storage_inner]



def add_slot(slot: BaseSlot) -> Callable:
    def add_slot_inner(ctx: Context, actor: Actor) -> Context:
        handler: SlotHandler = ctx.framework_states["slots"]
        handler.add_slot(slot)
        return ctx

    return add_slot_inner


def get_slot(ctx: Context, slot: Union[BaseSlot, str]) -> Optional[BaseSlot]:
    ctx_slot: Union[None, GroupSlot, ValueSlot] = (
        "slots" in ctx.framework_states
        and ctx.framework_states["slots"].has_slot(slot)
        and ctx.framework_states["slots"].get_slot(slot)
    )
    return ctx_slot if ctx_slot else None


def extract_slot(slot: BaseSlot) -> Callable:
    def extract_slot_inner(ctx: Context, actor: Actor) -> Context:
        ctx_slot: Union[None, GroupSlot, ValueSlot] = get_slot(ctx, slot)
        print("extracting")
        if ctx_slot is not None:
            print("not none")
            ctx_slot.extract_value(ctx, actor)
        return ctx
    
    return extract_slot_inner


def slot_is_set(slot: Union[BaseSlot, str]) -> Callable:
    def is_set_inner(ctx: Context, actor: Actor) -> bool:
        ctx_slot: Union[None, GroupSlot, ValueSlot] = get_slot(ctx, slot)
        if ctx_slot is None: 
            return False
        return ctx_slot.is_set()

    return is_set_inner


def fill_slots(ctx: Context, actor: Actor, *args, **kwargs) -> None:
    response = ctx.framework_states["actor"]["response"]
    if callable(response):
        response = response(ctx, actor)
    
    if isinstance(response, str):
        ctx.framework_states["actor"]["response"] = response.format(**dict(ctx.framework_states["slots"]))
    
    elif isinstance(response, Response):
        response.text = response.text.format(**dict(ctx.framework_states["slots"]))
        ctx.framework_states["actor"]["response"] = response

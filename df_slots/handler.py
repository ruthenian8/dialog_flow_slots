from typing import Union

from pydantic import BaseModel, Extra

from df_engine.core import Context, Actor
from df_engine.core.types import ActorStage

from df_generics import Response

from slot_types import BaseSlot


class SlotHandler(BaseModel):
    class Config:
        extra = Extra.allow
    
    def has_slot(self, slot: Union[BaseSlot, str]) -> bool:
        if isinstance(slot, str):
            return hasattr(self, slot)
        return hasattr(self, slot.name)

    def slot_is_set(self, slot: Union[BaseSlot, str]) -> bool:
        slot = self.get_slot(slot)
        if not slot:
            return False
        return slot.is_set()

    def set_slot(self, slot: BaseSlot):
        setattr(self, slot.name, slot)

    def get_slot(self, slot: Union[BaseSlot, str]) -> BaseSlot:
        if not self.has_slot(slot):
            return None
        name = slot if isinstance(slot, str) else slot.name
        return getattr(self, name)

def create_slot_storage(actor: Actor):
    def create_slot_storage_inner(ctx: Context, actor: Actor, *args, **kwargs):
        if "slots" not in ctx.framework_states:
            ctx.framework_states["slots"] = SlotHandler()
    actor.handlers[ActorStage.CONTEXT_INIT] = create_slot_storage_inner


def set_slot(slot: BaseSlot):
    def set_slot_inner(ctx: Context, actor: Actor):
        slot.extract_value(ctx, actor)
        if not slot.is_set():
            return ctx
        ctx.framework_states["slots"].set_slot(slot)
        return ctx

    return set_slot_inner


def slot_is_set(slot: BaseSlot):
    def is_set_inner(ctx: Context, actor: Actor):
        return bool(
            "slots" in ctx.framework_states
            and ctx.framework_states["slots"].has_slot(slot)
            and ctx.framework_states["slots"].get_slot(slot).is_set()
        )

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

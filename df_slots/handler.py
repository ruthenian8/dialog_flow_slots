from pydantic import BaseModel, validate_arguments
import logging

from df_engine.core import Context, Actor
from df_engine.core.types import ActorStage

from df_generics import Response

from .types import Slots


class SlotHandler(BaseModel):
    @validate_arguments
    def _update_handlers(self, actor: Actor, stage: ActorStage, handler) -> Actor:
        actor.handlers[stage] = actor.handlers.get(stage, []) + [handler]
        return actor

    def fill_slots(self, ctx: Context, actor: Actor, *args, **kwargs):
        response = ctx.framework_states["actor"]["response"]
        if isinstance(response, str):
            ctx.framework_states["actor"]["response"] = response.format(**dict(ctx.framework_states["slots"]))
        elif isinstance(response, Response):
            response.text = response.text.format(**dict(ctx.framework_states["slots"]))
            ctx.framework_states["actor"]["response"] = response

    def create_slot_storage(self, ctx: Context, actor: Actor, *args, **kwargs):
        if "slots" not in ctx.framework_states:
            ctx.framework_states["slots"] = Slots()

    def set_slot(self, slot_type: type):
        def set_slot_inner(ctx: Context, actor: Actor):
            value = slot_type.get_value(ctx, actor)
            slot = slot_type.parse_obj({"name": slot_type.name, "value": value})
            ctx.framework_states["slots"].set_slot(slot)
            sl = ctx.framework_states["slots"].get_slot(slot_type)
            print("slot set: {}".format(sl))
            print(f"slot value: {sl.value}")
            print(f"is set: {sl.is_set()}")
            return ctx

        return set_slot_inner

    def slot_is_set(self, slot: type):
        def is_set_inner(ctx: Context, actor: Actor):
            if "slots" in ctx.framework_states:
                sl = ctx.framework_states["slots"].get_slot(slot)
                print("slot: {}".format(sl))
            return bool(
                "slots" in ctx.framework_states
                and ctx.framework_states["slots"].has_slot(slot)
                and ctx.framework_states["slots"].get_slot(slot).is_set()
            )

        return is_set_inner

    def update_actor_handlers(self, actor: Actor, *args, **kwargs):
        self._update_handlers(actor, ActorStage.CREATE_RESPONSE, self.fill_slots)
        self._update_handlers(actor, ActorStage.CONTEXT_INIT, self.create_slot_storage)

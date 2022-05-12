from tokenize import group
from typing import Any

try:
    from typing import ClassVar
except ImportError:
    from typing_extensions import ClassVar

from df_engine.core import Context, Actor

from pydantic import BaseModel, Extra

SlotName = ClassVar[str]
SlotGroup = ClassVar[str]


class Slot(BaseModel):
    group: SlotGroup = "common"
    name: SlotName = ...
    value: Any = None

    def is_set(self):
        return self.value is not None

    def __str__(self):
        return str(self.value)

    @classmethod
    def get_value(cls, ctx: Context, actor: Actor):
        raise NotImplementedError


class Slots(BaseModel):
    class Config:
        extra = Extra.allow

    def has_slot(self, slot: type) -> bool:
        return hasattr(self, slot.name)

    def slot_is_set(self, slot: type) -> bool:
        slot = self.get_slot(slot)
        if not slot:
            return False
        return slot.is_set()

    def set_slot(self, slot: Slot):
        setattr(self, slot.name, slot)

    def get_slot(self, slot: type) -> Slot:
        try:
            val = getattr(self, slot.name)
        except AttributeError:
            val = None
        return val

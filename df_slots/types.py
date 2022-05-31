import re
import json
import weakref
from typing import Optional, Any

from df_engine.core import Context, Actor

from pydantic import BaseModel, Field, Required, validator
from pydantic.dataclasses import dataclass
from pydantic.typing import ForwardRef

Slot = ForwardRef("Slot")


@dataclass
class Slot():
    _children: weakref.WeakValueDictionary[str, Slot] =  weakref.WeakValueDictionary()
    _parent: Optional[Slot] = None
    _name: str = Required
    _value: Any = None

    def __post_init__(self):
        for child in self.children.values():
            child.parent = self

    def add_child(self, child: Slot):
        child.parent = self
        self.children[child.name] = child

    def remove_child(self, child: Slot):
        self.children.pop(child.name)

    def has_children(self):
        return len(self.children) > 0

    def __eq__(self, other: Slot):
        return self.dict(exclude={"name"}) == other.dict(exclude={"name"})

    def __str__(self):
        if not self.has_children():
            return str(self.value) if self.value else ""
        else:
            return json.dumps(self.children)

    @validator("children", pre=True)
    def validate_children(cls, children):
        is_dict = isinstance(children, weakref.WeakValueDictionary)
        is_list = isinstance(children, list)
        if not is_list and not is_dict:
            raise ValueError(f"Inappropriate type: {str(type(children))}")
        if is_list:
            new_children = weakref.WeakValueDictionary()
            item: Slot
            for item in children:
                new_children[item.name] = item
            return new_children
        return children

    def extract_value(self, ctx: Context, actor: Actor):
        for child in self.children.values():
            child.extract_value(ctx, actor)
        self.init_value(ctx, actor)
        return self.value

    def init_value(self, ctx: Context, actor: Actor):
        raise NotImplementedError("")

    def is_set(self):
        raise NotImplementedError("")

    def fill_template(self):
        raise NotImplementedError("")



class RegexpSlot(Slot):
    _regexp: Optional[re.Pattern] = Field(default=None, alias="regexp")

    def init_value(self, ctx: Context, actor: Actor):
        super(RegexpSlot, self).extract_value(ctx, actor)
        search = re.search(self._regexp, ctx.last_request)
        self.value = search.group() if search else None

    def is_set(self):
        return self.value is not None

    def fill_template(self, template: str):
        return template.format(**{self._name:self.value})

class GroupSlot(Slot):
    def init_value(self, ctx: Context, actor: Actor):
        pass

    def is_set(self):
        return all(map(lambda child: child.is_set(), self.children.values()))

s1, s2 = None,None
gs = GroupSlot(name="group_slot",children=[s1, s2])

def extract(ctx, actor):
    return ctx

def processing(ctx, actor):
    ctx.misc["gs"] = gs.extract_value(ctx, actor)
    ctx = extract(gs, ctx, actor)

    gs.fill("{group_slot}{group_slot.s1}{group_slot.s2}", ctx, actor)


gs.fill("{group_slot.s1}")

gs.s1


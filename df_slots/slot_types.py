import re
import json
import weakref
from typing import Optional, Any

from df_engine.core import Context, Actor

from pydantic import BaseModel, Field, validator, Extra
from pydantic.dataclasses import dataclass
from pydantic.typing import ForwardRef

BaseSlot = ForwardRef("BaseSlot")


class SlotStorage(BaseModel):
    class Config():
        extra = Extra.allow


@dataclass
class BaseSlot():
    name: str
    children: weakref.WeakValueDictionary[str, BaseSlot] =  weakref.WeakValueDictionary()
    parents: weakref.WeakValueDictionary[str, BaseSlot] =  weakref.WeakValueDictionary()
    value: Any = None

    def __post_init__(self):
        for parent in self.parents.values():
            parent.children[self.name] = self

    def add_parent(self, parent: BaseSlot):
        parent.children[self.name] = self
        self.parents[parent.name] = parent

    def remove_parent(self, parent: BaseSlot):
        self.parents[parent.name].children.pop(self.name)
        self.parents.pop(parent.name)

    def has_parents(self):
        return len(self.parents) > 0

    @validator("children", pre=True)
    def validate_children(cls, children):
        is_dict = isinstance(children, weakref.WeakValueDictionary)
        is_list = isinstance(children, list)
        if not is_list and not is_dict:
            raise ValueError(f"Inappropriate type: {str(type(children))}")
        if is_list:
            new_children = weakref.WeakValueDictionary()
            item: BaseSlot
            for item in children:
                new_children[item.name] = item
            return new_children
        return children

    @validator("parents", pre=True)
    def validate_parents(cls, parents):
        is_dict = isinstance(parents, weakref.WeakValueDictionary)
        is_list = isinstance(parents, list)
        if not is_list and not is_dict:
            raise ValueError(f"Inappropriate type: {str(type(parents))}")
        if is_list:
            new_parents = weakref.WeakValueDictionary()
            item: BaseSlot
            for item in parents:
                new_parents[item.name] = item
            return new_parents
        return parents

    def __eq__(self, other: BaseSlot):
        return self.dict(exclude={"name"}) == other.dict(exclude={"name"})

    def extract_value(self, ctx: Context, actor: Actor):
        self.init_value(ctx, actor)
        return self.value

    def is_set(self):
        return self.value is not None

    def has_children(self):
        raise NotImplementedError("")

    def init_value(self, ctx: Context, actor: Actor):
        raise NotImplementedError("")

    def is_set(self):
        raise NotImplementedError("")

    def fill_template(self):
        raise NotImplementedError("")


class GroupSlot(BaseSlot):
    def __post_init__(self):
        super().__post_init__()
        for child in self.children.values():
            child.parents[self.name] = self        

    def __str__(self):
        return json.dumps(dict(self.value)) if self.value else ""

    def add_child(self, child: BaseSlot):
        child.parents[self.name] = self
        self.children[child.name] = child

    def remove_child(self, child: BaseSlot):
        self.children[child.name].parents.pop(self.name)
        self.children.pop(child.name)

    def init_value(self, ctx: Context, actor: Actor):
        values = SlotStorage()
        for child in self.children.values():
            if not child.value:
                val = child.extract_value(ctx, actor)
                if not val:
                    self.value = None
                    break
            setattr(values, child.name, child.value)
        self.value = values

    def has_children(self):
        return len(self.children) > 0

    def fill_template(self, template: str):
        if not self.is_set():
            return template
        return template.format(**dict(self.value))

    def dict(self, *args, **kwargs):
        return self.value.dict(*args, **kwargs)
    
    def json(self, *args, **kwargs):
        return self.value.json(*args, *kwargs)


class ValueSlot(BaseSlot):
    def __str__(self):
        return str(self.value) if self.value else ""    

    def has_children(self):
        return False

    def fill_template(self, template: str):
        return template.format(**{self.name: self.value})

    def dict(self, *args, **kwargs):
        return {self.name: self.value}

    def json(self, *args, **kwargs):
        return json.dumps({self.name, self.value})


class RegexpSlot(ValueSlot):
    regexp: Optional[re.Pattern] = Field(default=None, alias="regexp")

    def init_value(self, ctx: Context, actor: Actor):
        search = re.search(self.regexp, ctx.last_request)
        self.value = search.group() if search else None





# s1, s2 = None,None
# gs = GroupSlot(name="group_slot",children=[s1, s2])

# def extract(ctx, actor):
#     return ctx

# def processing(ctx, actor):
#     ctx.misc["gs"] = gs.extract_value(ctx, actor)
#     ctx = extract(gs, ctx, actor)

#     gs.fill("{group_slot}{group_slot.s1}{group_slot.s2}", ctx, actor)


# gs.fill("{group_slot.s1}")

# gs.s1


import re
from copy import copy
from collections.abc import Iterable
from typing import Callable, Optional, Any, Dict

from df_engine.core import Context, Actor

from pydantic import Field, BaseModel, validator
from pydantic.typing import ForwardRef

BaseSlot = ForwardRef("BaseSlot")


class BaseSlot(BaseModel):
    name: str

    class Config:
        arbitrary_types_allowed = True

    def __deepcopy__(self, *args, **kwargs):
        return copy(self)

    def __eq__(self, other: BaseSlot):
        return self.dict(exclude={"name"}) == other.dict(exclude={"name"})

    def has_children(self):
        return hasattr(self, "children") and len(self.children) > 0

    def is_set(self):
        raise NotImplementedError("Base class has no attribute 'value'")

    def fill_template(self):
        raise NotImplementedError("Base class has no attribute 'value'")

    def extract_value(self, ctx: Context, actor: Actor):
        self.init_value(ctx, actor)
        return self.value

    def init_value(self, ctx: Context, actor: Actor):
        raise NotImplementedError("Base class has no attribute 'value'")


class GroupSlot(BaseSlot):
    children: Dict[str, BaseSlot] = Field(default_factory=dict)

    @validator("children", pre=True)
    def validate_children(cls, children):
        if not isinstance(children, dict) and isinstance(children, Iterable):
            new_children = {child.name: child for child in children}
            return new_children
        return children

    @property
    def value(self):
        return {name: child.value for name, child in self.children.items()}

    def __getattr__(self, attr: str):
        try:
            value = self.__getattribute__(attr)
        except AttributeError:
            value = self.children.get(attr) or ""  # for slot filling
        return value

    def __str__(self):
        return f":Slot group {self.name}:"

    def is_set(self):
        return all(child.is_set() for child in self.children.values())

    def fill_template(self, template: str) -> Callable:
        def fill_inner(ctx: Context, actor: Actor):
            if not self.is_set():
                return template
            return template.format(**self.value)

        return fill_inner

    def init_value(self, ctx: Context, actor: Actor):
        for child in self.children.values():
            if not child.value:
                child.init_value(ctx, actor)


class ValueSlot(BaseSlot):
    value: Any = None

    def __str__(self):
        return str(self.value) if self.value else ""

    def is_set(self):
        return self.value is not None

    def fill_template(self, template: str):
        def fill_inner(ctx: Context, actor: Actor):
            if not self.is_set():
                return template
            return template.format(**{self.name: self.value})

        return fill_inner


class RegexpSlot(ValueSlot):
    regexp: Optional[re.Pattern] = Field(default=None, alias="regexp")

    @validator("regexp", pre=True)
    def val_regexp(cls, reg):
        if isinstance(reg, str):
            return re.compile(reg)
        return reg

    def init_value(self, ctx: Context, actor: Actor):
        search = re.search(self.regexp, ctx.last_request)
        self.value = search.group() if search else None


class FunctionSlot(ValueSlot):
    func: Callable[[str], str]

    def init_value(self, ctx: Context, actor: Actor):
        self.value = self.func(ctx.last_request)


BaseSlot.update_forward_refs()

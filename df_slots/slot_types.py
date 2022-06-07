import re
from typing import Callable, List, Optional, Any, Dict

from df_engine.core import Context, Actor

from pydantic import Field, BaseModel, validator
from pydantic.typing import ForwardRef

BaseSlot = ForwardRef("BaseSlot")


class BaseSlot(BaseModel):
    name: str
    parent: Optional[BaseSlot] = None
    value: Any = None

    class Config():
        arbitrary_types_allowed = True

    def __eq__(self, other: BaseSlot):
        return self.dict(exclude={"name"}) == other.dict(exclude={"name"})

    def __getattr__(self, attr: str):
        try:
            value = self.__getattribute__(attr)
        except AttributeError:
            value = self.children.get(attr) or "" # for slot filling
        return value

    def has_children(self):
        raise NotImplementedError("Base class has no attribute 'value'")

    def is_set(self):
        raise NotImplementedError("Base class has no attribute 'value'")

    def fill_template(self):
        raise NotImplementedError("Base class has no attribute 'value'")

    def extract_value(self, ctx: Context, actor: Actor):
        raise NotImplementedError("Base class has no attribute 'value'")

    def init_value(self, ctx: Context, actor: Actor):
        raise NotImplementedError("Base class has no attribute 'value'")


class GroupSlot(BaseSlot):
    children: Dict[str, BaseSlot] = Field(default_factory=dict)

    def __str__(self):
        return f":Slot group {self.name}:"

    def add_child(self, child: BaseSlot):
        self.children[child.name] = child
        child.parent = self

    def add_children(self, children: Optional[List[BaseSlot]]):
        for child in children:
            self.add_child(child=child)

    def remove_child(self, child: BaseSlot):
        self.children.pop(child.name)
        child.parent = None

    def has_children(self):
        return len(self.children) > 0

    def is_set(self):
        return all(child.is_set() for child in self.children.values())

    def fill_template(self, template: str) -> Callable:
        def fill_inner(ctx: Context, actor: Actor):
            if not self.is_set():
                return template
            return template.format(**self.children)

        return fill_inner

    def extract_value(self, ctx: Context, actor: Actor):
        self.init_value(ctx, actor)
        return self.children

    def init_value(self, ctx: Context, actor: Actor):
        for child in self.children.values():
            if not child.value:
                child.extract_value(ctx, actor)


class ValueSlot(BaseSlot):
    def __str__(self):
        return str(self.value) if self.value else ""    

    def has_children(self):
        return False

    def fill_template(self, template: str):
        def fill_inner(ctx: Context, actor: Actor):
            if not self.is_set():
                return template
            return template.format(**{self.name: self.value})

        return fill_inner

    def is_set(self):
        return self.value is not None


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


BaseSlot.update_forward_refs()
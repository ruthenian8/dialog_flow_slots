import re
import logging
from copy import copy
from collections.abc import Iterable
from typing import Callable, Optional, Any, Dict

from df_engine.core import Context, Actor

from pydantic import Field, BaseModel, validator
from pydantic.typing import ForwardRef

logger = logging.getLogger(__name__)

BaseSlot = ForwardRef("BaseSlot")


class BaseSlot(BaseModel):
    name: str

    @validator("name", pre=True)
    def validate_name(cls, name: str):
        if "/" in name:
            raise ValueError("separator `/` cannot be used in slot names")
        return name

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

    def fill_template(self, template: str) -> Callable[[Context, Actor], str]:
        raise NotImplementedError("Base class has no attribute 'value'")

    def extract_value(self, ctx: Context, actor: Actor):
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
        values = dict()
        for name, child in self.children.items():
            if isinstance(child, GroupSlot):
                values.update({key: value for key, value in child.value.items()})
            else:
                values.update({child.name: child.value})
        return values

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
        def fill_inner(ctx: Context, actor: Actor) -> str:
            new_template = template
            for _, child in self.children.items():
                new_template = child.fill_template(new_template)(ctx, actor)

            return new_template

        return fill_inner

    def extract_value(self, ctx: Context, actor: Actor):
        for child in self.children.values():
            val = child.extract_value(ctx, actor)
        return self.value


class ValueSlot(BaseSlot):
    value: Any = None

    def __str__(self):
        return str(self.value) if self.value else ""

    def is_set(self):
        return self.value is not None

    def fill_template(self, template: str) -> Callable:
        def fill_inner(ctx: Context, actor: Actor) -> str:
            if not self.name in template:
                return template
            
            storage = ctx.framework_states.get("slots")
            if storage is None or self.name not in storage:
                logger.warning("storage or storage entry missing")
                return template

            value = storage.get(self.name)
            if value is None:
                return template
            return template.replace("{" + self.name + "}", value)

        return fill_inner


class RegexpSlot(ValueSlot):
    regexp: Optional[re.Pattern] = Field(default=None, alias="regexp")

    @validator("regexp", pre=True)
    def val_regexp(cls, reg):
        if isinstance(reg, str):
            return re.compile(reg)
        return reg

    def extract_value(self, ctx: Context, actor: Actor):
        search = re.search(self.regexp, ctx.last_request)
        self.value = search.group() if search else None
        return self.value


class FunctionSlot(ValueSlot):
    func: Callable[[str], str]

    def extract_value(self, ctx: Context, actor: Actor):
        self.value = self.func(ctx.last_request)
        return self.value


BaseSlot.update_forward_refs()

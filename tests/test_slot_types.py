import sys

import pytest

from df_slots import RegexpSlot, GroupSlot, FunctionSlot, flatten_slot_tree

@pytest.mark.parametrize(
    ("input", "regexp", "expected", "_set"),
    [("I am Groot", "(?<=am ).+", "Groot", True),
    ("My email is groot@gmail.com", "(?<=email is ).+", "groot@gmail.com", True),
    ("I won't tell you my name", "(?<=name is ).+$", None, False)]
)
def test_regexp(input, regexp, expected, _set, testing_context, testing_actor):
    testing_context.add_request(input)
    slot = RegexpSlot(name="test", regexp=regexp)
    slot.init_value(testing_context, testing_actor)
    assert slot.value == expected
    assert slot.is_set() == _set
    result = slot.extract_value(testing_context, testing_actor)
    assert result == expected


@pytest.mark.parametrize(
    ("input", "children", "expected", "is_set"),
    [(
        "I am Groot. My email is groot@gmail.com",
        [RegexpSlot(name="name", regexp=r"(?<=am ).+?(?=\.)"), RegexpSlot(name="email", regexp=r"[a-zA-Z\.]+@[a-zA-Z\.]+")],
        {"name": "Groot", "email": "groot@gmail.com"},
        True
    ),
    ("I am Groot. I won't tell you my name",
        [RegexpSlot(name="name", regexp=r"(?<=am ).+?(?=\.)"), RegexpSlot(name="email", regexp=r"[a-zA-Z\.]+@[a-zA-Z\.]+")],
        {"name": "Groot", "email": None},
        False
    )]
)
def test_group(input, children, expected, is_set, testing_context, testing_actor):
    testing_context.add_request(input)
    slot = GroupSlot(name="test", children=children)
    slot.init_value(testing_context, testing_actor)
    assert slot.value == expected
    assert slot.is_set() == is_set
    result = slot.extract_value(testing_context, testing_actor)
    assert result == expected
    template = "{name} {email}"
    assert (slot.fill_template(template)(testing_context, testing_actor) != template) == is_set


@pytest.mark.parametrize(
    ("input", "func", "expected", "_set"),
    [("I am Groot", lambda msg: msg.split(" ")[2], "Groot", True),
    ("My email is groot@gmail.com", lambda msg: [i for i in msg.split(" ") if "@" in i][0], "groot@gmail.com", True),
    ("I won't tell you my name", lambda msg: [i for i in msg.split(" ") if "@" in i] or None, None, False)]
)
def test_function(input, func, expected, _set, testing_context, testing_actor):
    testing_context.add_request(input)
    slot = FunctionSlot(name="test", func=func)
    slot.init_value(testing_context, testing_actor)
    assert slot.value == expected
    assert slot.is_set() == _set
    result = slot.extract_value(testing_context, testing_actor)
    assert result == expected


def test_children():
    slot = GroupSlot(name="test", children=[RegexpSlot(name="test", regexp="(?<=am ).+")])
    assert slot.test is slot.children["test"]
    assert slot.has_children() == True
    slot.children.pop("test")
    assert slot.has_children() == False


@pytest.mark.parametrize(
    ("root_name","length","children", "names"),
    [("root", 3, [
        RegexpSlot(name="name", regexp=r"(?<=am ).+?(?=\.)"),
        RegexpSlot(name="email", regexp=r"[a-zA-Z\.]+@[a-zA-Z\.]+")
    ], [
        "root.name",
        "root.email",
        "root"
    ]),
    ("root", 4, [
        GroupSlot(
        name="person",
        children=[
            RegexpSlot(name="name", regexp=r"(?<=am ).+?(?=\.)"),
            RegexpSlot(name="email", regexp=r"[a-zA-Z\.]+@[a-zA-Z\.]+")
        ])
    ], [
        "root.person.name",
        "root.person.email",
        "root.person",
        "root"
    ]),
    ("root", 7, [
        GroupSlot(
        name="person_1",
        children=[
            RegexpSlot(name="name", regexp=r"(?<=am ).+?(?=\.)"),
            RegexpSlot(name="email", regexp=r"[a-zA-Z\.]+@[a-zA-Z\.]+")
        ]),
        GroupSlot(
        name="person_2",
        children=[
            RegexpSlot(name="name", regexp=r"(?<=am ).+?(?=\.)"),
            RegexpSlot(name="email", regexp=r"[a-zA-Z\.]+@[a-zA-Z\.]+")
        ])
    ], None)]
)
def test_flatten(root_name, length, children, names):
    slot = GroupSlot(
        name=root_name,
        children=children
    )
    flatten_result = flatten_slot_tree(slot)
    assert len(flatten_result) == length
    assert all(map(lambda x: x.startswith(root_name), flatten_result.keys()))
    if names:
        assert all(map(lambda x: x in flatten_result, names))


def test_slot_root(root):
    slot = RegexpSlot(name="test", regexp=r".+")
    assert slot.name in root
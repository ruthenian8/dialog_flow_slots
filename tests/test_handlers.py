import sys

import pytest

from df_slots.handlers import get_values, get_filled_template, extract
from df_slots import FunctionSlot, register_root_slots


@pytest.mark.parametrize(
    ["input", "noparams", "expected"],
    [
        ("my name is Groot", False, ["Groot"]),
        ("my name ain't Groot", False, [None]),
        ("my name is Groot", True, ["Groot"]),
        ("my name ain't Groot", True, [None]),
    ],
)
def test_get_template(input, noparams, expected, testing_context, testing_actor, root):
    testing_context.add_request(input)
    slot_name = "creature_name"
    template = "{" + slot_name + "}"
    root.clear()
    slot = FunctionSlot(name=slot_name, func=lambda x: x.partition("name is ")[-1] or None)
    if noparams:
        result_1 = extract(testing_context, testing_actor)
        result_2 = get_values(testing_context, testing_actor)
        result_3 = get_filled_template(template, testing_context, testing_actor)
    else:
        result_1 = extract(testing_context, testing_actor, [slot_name])
        result_2 = get_values(testing_context, testing_actor, [slot_name])
        result_3 = get_filled_template(template, testing_context, testing_actor, [slot_name])
    if result_3 == template:
        result_3 = None
    assert result_1 == result_2 == [result_3] == expected


def test_error(testing_context, testing_actor):
    with pytest.raises(ValueError):
        result = get_filled_template("{non-existent_slot}", testing_context, testing_actor, ["non-existent_slot"])
    assert True

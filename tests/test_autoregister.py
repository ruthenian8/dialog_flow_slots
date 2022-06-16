import sys

import pytest

from df_slots import GroupSlot, RegexpSlot, register_root_slots


def test_nesting(root):
    f_name = RegexpSlot(name="f_name", regexp="(?<=name )[a-z]+")
    l_name = RegexpSlot(name="l_name", regexp=".+")
    name = GroupSlot(name="name", children=[f_name, l_name])
    cat_data = GroupSlot(name="cat_data", children=[name])
    cat = GroupSlot(name="cat", children=[cat_data])
    root = register_root_slots([cat], root)
    print(str(root))
    assert sorted(root.keys()) == [
        'cat', 'cat/cat_data', 'cat/cat_data/name', 'cat/cat_data/name/f_name', 'cat/cat_data/name/l_name'
    ]
    # assert False

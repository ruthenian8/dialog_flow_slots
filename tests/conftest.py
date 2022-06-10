import sys

import pytest

from df_engine.core import Context

sys.path.insert(0, "../")

from examples.slot_example import actor

from df_slots.root import root as slot_root


@pytest.fixture
def testing_context():
    ctx = Context()
    ctx.add_request("I am Groot")
    yield ctx


@pytest.fixture
def testing_actor():
    yield actor


@pytest.fixture(scope="function")
def root():
    yield slot_root

import sys
import importlib

import pytest

# uncomment the following line, if you want to run your examples during the test suite or import from them
sys.path.insert(0, "../")

from examples.example_utils import run_test

# pytest.skip(allow_module_level=True)


@pytest.mark.parametrize("module_name", ["examples.basic_example", "examples.generics_example"])
def test_examples(module_name):
    module = importlib.import_module(module_name)
    actor = getattr(module, "actor")
    testing_dialog = getattr(module, "testing_dialog")
    run_test(testing_dialog=testing_dialog, actor=actor)

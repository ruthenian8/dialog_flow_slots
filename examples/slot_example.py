import re
import logging
from typing import Optional
from datetime import date

from df_engine import conditions as cnd
from df_engine.core.keywords import RESPONSE, TRANSITIONS, PROCESSING, GLOBAL, LOCAL
from df_engine.core import Context, Actor

from df_slots import create_slot_storage, set_slot, slot_is_set, RegexpSlot
from df_generics import Response

from example_utils import run_interactive_mode


script = {
    GLOBAL: {TRANSITIONS: {("username_flow", "ask"): cnd.regexp(r"^[sS]tart")}},
    "username_flow": {
        LOCAL: {
            PROCESSING: {"get_slot": set_slot(RegexpSlot(name="username", regexp=r"username is ([a-zA-Z]+)"))},
            TRANSITIONS: {
                ("email_flow", "ask", 1.2): slot_is_set("username"),
                ("username_flow", "repeat_question", 0.8): cnd.true(),
            },
        },
        "ask": {
            RESPONSE: "Write your username (my username is ...):",
        },
        "repeat_question": {RESPONSE: "Please, type your username again (my username is ...):"},
    },
    "email_flow": {
        LOCAL: {
            PROCESSING: {"get_slot": set_slot(RegexpSlot(name="username", regexp=r"email is ([a-zA-Z]+)"))},
            TRANSITIONS: {
                ("root", "utter", 1.2): slot_is_set("username"),
                ("email_flow", "repeat_question", 0.8): cnd.true(),
            },
        },
        "ask": {
            RESPONSE: "Write your birth date (YYYY-MM-DD):",
        },
        "repeat_question": {RESPONSE: "Please, type your birth date again (YYYY-MM-DD):"},
    },
    "root": {
        "start": {RESPONSE: "", TRANSITIONS: {("username_flow", "ask"): cnd.true()}},
        "fallback": {RESPONSE: "Finishing query", TRANSITIONS: {("username_flow", "ask"): cnd.true()}},
        "utter": {
            RESPONSE: "Your username is {username}. Your birth date is {birth_date}.",
            TRANSITIONS: {("root", "fallback"): cnd.true()},
        },
    },
}

actor = Actor(script=script, start_label=("root", "start"), fallback_label=("root", "fallback"), )
create_slot_storage(actor)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s-%(name)15s:%(lineno)3s:%(funcName)20s():%(levelname)s - %(message)s",
        level=logging.INFO,
    )
    run_interactive_mode(actor)

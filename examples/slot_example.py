import re
import logging
from typing import Optional
from datetime import date

from df_engine import conditions as cnd
from df_engine.core.keywords import RESPONSE, TRANSITIONS, PROCESSING, GLOBAL, LOCAL
from df_engine.core import Context, Actor

from df_slots import Slot, SlotHandler, SlotName
from df_generics import Response

from example_utils import run_interactive_mode

slot_handler = SlotHandler()




# class UsernameSlot(Slot):
#     name: SlotName = "username"
#     value: Optional[str] = None

#     @staticmethod
#     def get_value(ctx: Context, actor: Actor):
#         match = re.search(r"username is ([a-zA-Z]+)", ctx.last_request)
#         return match.group(1) if match else match


# class EmailSlot(Slot):
#     name: SlotName = "birth_date"
#     value: Optional[date] = None

#     @staticmethod
#     def get_value(ctx: Context, actor: Actor):
#         match = re.search(r"(\d{4,}-\d{2,}-\d{2,})", ctx.last_request)
#         return match.group(1) if match else match

def set_regexp_slot(self, name: str, regexp: str):
    @classmethod
    def get_value(cls, ctx: Context, actor: Actor):
        string = ctx.last_request
        return re.search(regexp, string).group()
    slot = type(name, (), {"get_value": get_value})
    self.set_slot(slot)

slot_handler.set_regexp_slot = set_regexp_slot


script = {
    GLOBAL: {TRANSITIONS: {("username_flow", "ask"): cnd.regexp(r"^[sS]tart")}},
    "username_flow": {
        LOCAL: {
            PROCESSING: {"get_slot": slot_handler.set_regexp_slot(name="username", regexp=r"username is ([a-zA-Z]+)")},
            TRANSITIONS: {
                ("email_flow", "ask", 1.2): slot_handler.slot_is_set("username"),
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
            PROCESSING: {"get_slot": slot_handler.set_slot(EmailSlot)},
            TRANSITIONS: {
                ("root", "utter", 1.2): slot_handler.slot_is_set(EmailSlot),
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

actor = Actor(script=script, start_label=("root", "start"), fallback_label=("root", "fallback"))
slot_handler.update_actor_handlers(actor)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s-%(name)15s:%(lineno)3s:%(funcName)20s():%(levelname)s - %(message)s",
        level=logging.INFO,
    )
    run_interactive_mode(actor)

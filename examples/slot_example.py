import re
import logging
from typing import Optional
from datetime import date

from df_engine import conditions as cnd
from df_engine.core.keywords import RESPONSE, TRANSITIONS, PROCESSING, GLOBAL, LOCAL
from df_engine.core import Context, Actor

import df_slots
from df_slots import conditions as slot_cnd
from df_slots import processing as slot_procs
from df_slots import response as slot_rps

from .example_utils import run_interactive_mode

username_slot = df_slots.RegexpSlot(name="username", regexp=r"username is ([a-zA-Z]+)")
email_slot = df_slots.RegexpSlot(name="email", regexp=r"email is ([a-zA-Z]+)")
person_slot = df_slots.GroupSlot(name="person", children=[username_slot, email_slot])


#######
# import df_slots
# from df_slots import processing as slot_procs
# from df_slots import response as slot_rps

# root_hold = True
# root = {}

# ####### Slot's Structure #######
# username = df_slots.RegexpSlot(name="username", regexp=r"username is ([a-zA-Z]+)")
# username1 = df_slots.RegexpSlot(name="username", regexp=r"username is ([a-zA-Z]+)")
# email = df_slots.FuncSlot(name="email", custom_extract, custom_fill_tempalte)
# profile = df_slots.TreeSlot(name="profile", [username, email])

# df_slots.set_root_slots([profile, username]) # same names are rewrited by default

# ####### Slot Usage in Script #######
# PROCESSING: slot_procs.extract() # slot_procs.extract(["username", "profile"])
# PROCESSING: slot_procs.fill_template()
# RESPONSE: slot_rps.fill_template("{profile.username}{username}")


# ####### Slot Usage in function #######
# def response(ctx, actor):
#     ctx = df_slots.extract(ctx, actor) # df_slots.extract(ctx, actor, ["profile.username"]) 
#     # ctx = df_slots.extract(ctx, actor, ["username"])
#     profile_value, username_value = df_slots.get_values(ctx, actor) # df_slots.extract(ctx, actor, ["profile", "username"])
#     _email, _username, _p_username = df_slots.get_values(ctx, actor, ["profile.email", "username", "profile.username"]) # ???
#     response_str = df_slots.get_filled_template("{profile.username}", ctx, actor)
#     response_str = df_slots.get_filled_template("{username}", ctx, actor, "profile")
#     return response_str



script = {
    GLOBAL: {TRANSITIONS: {("username_flow", "ask"): cnd.regexp(r"^[sS]tart")}},
    "username_flow": {
        LOCAL: {
            PROCESSING: {"get_slot": extract_slot("person.username")},
            TRANSITIONS: {
                ("email_flow", "ask", 1.2): cnd.all([slot_is_set("person.username")]),
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
            PROCESSING: {"get_slot": extract_slot("person.email")},
            TRANSITIONS: {
                ("root", "utter", 1.2): cnd.all([slot_is_set("person.email")]),
                ("email_flow", "repeat_question", 0.8): cnd.true(),
            },
        },
        "ask": {
            RESPONSE: "Write your email (my email is ...):",
        },
        "repeat_question": {RESPONSE: "Please, write your email again (my email is ...):"},
    },
    "root": {
        "start": {RESPONSE: "", TRANSITIONS: {("username_flow", "ask"): cnd.true()}},
        "fallback": {RESPONSE: "Finishing query", TRANSITIONS: {("username_flow", "ask"): cnd.true()}},
        "utter": {
            RESPONSE: person_slot.fill_template("Your username is {username}"),
            TRANSITIONS: {("root", "utter_alternative"): cnd.true()}
        },
        "utter_alternative": {
            RESPONSE: "Your username is {person.username}. Your email is {person.email}.",
            PROCESSING: {"slot_filling": fill_slots},
            TRANSITIONS: {("root", "fallback"): cnd.true()},
        }
    },
}

actor = Actor(script=script, start_label=("root", "start"), fallback_label=("root", "fallback"), )
create_slot_handler(actor, slots=[person_slot])

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s-%(name)15s:%(lineno)3s:%(funcName)20s():%(levelname)s - %(message)s",
        level=logging.INFO,
    )
    run_interactive_mode(actor)

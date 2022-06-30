import logging

from df_engine import labels as lbl
from df_engine.core import Actor
from df_engine.core.keywords import LOCAL, PRE_TRANSITIONS_PROCESSING, TRANSITIONS, GLOBAL, RESPONSE
from df_engine import conditions as cnd

import df_slots
from df_slots.utils import FORM_STORAGE_KEY, SLOT_STORAGE_KEY
from df_slots import processing as slot_procs

from examples import example_utils

logger = logging.getLogger(__name__)


def is_unrelated_intent(ctx, actor):
    return False


RestaurantCuisine = df_slots.RegexpSlot(name="cuisine", regexp=r" ([A-Za-z]+) cuisine", target_group=1)
RestaurantAddress = df_slots.RegexpSlot(name="restaurantaddress", regexp=r"at (.+)|in (.+)", target_group=1)
NumberOfPeople = df_slots.RegexpSlot(name="numberofpeople", regexp=r"[0-9]+")
RestaurantForm = df_slots.Form(
    "restaurant",
    {
        RestaurantCuisine.name: [("restaurant", "cuisine")],
        RestaurantAddress.name: [("restaurant", "address")],
        NumberOfPeople.name: [("restaurant", "number")],
    },
)
df_slots.root_slot.register_slots([RestaurantCuisine, RestaurantAddress, NumberOfPeople])

script = {
    GLOBAL: {
        TRANSITIONS: {
            RestaurantForm.to_next_slot(0.7): cnd.true(),
        },
        PRE_TRANSITIONS_PROCESSING: {"update_form_state": RestaurantForm.update_form_state()},
    },
    "restaurant": {
        "cuisine": {
            RESPONSE: "What kind of cuisine would you like to have?",
            PRE_TRANSITIONS_PROCESSING: {"extraction": slot_procs.extract([RestaurantCuisine.name])},
        },
        "address": {
            RESPONSE: "In what area would you like to find a restaurant?",
            PRE_TRANSITIONS_PROCESSING: {"extraction": slot_procs.extract([RestaurantAddress.name])},
        },
        "number": {
            RESPONSE: "How many people would you like to invite?",
            PRE_TRANSITIONS_PROCESSING: {"extraction": slot_procs.extract([NumberOfPeople.name])},
        },
    },
    "chitchat": {
        LOCAL: {lbl.forward(0.9): cnd.true()},
        "chat_1": {RESPONSE: "How's life?"},
        "chat_2": {RESPONSE: "Who do you think will win the Champions League?"},
        "chat_25": {
            RESPONSE: "What kind of cuisine do you like?",
            PRE_TRANSITIONS_PROCESSING: {"extraction": slot_procs.extract([RestaurantCuisine.name])},
        },
        "chat_3": {
            RESPONSE: "Did you like the latest Star Wars film?",
            PRE_TRANSITIONS_PROCESSING: {"activate": RestaurantForm.update_form_state(df_slots.FormState.active)},
        },
    },
    "root": {
        "start": {RESPONSE: "", TRANSITIONS: {("chitchat", "chat_1", 2): cnd.true()}},
        "fallback": {RESPONSE: "Guess, I didn't get what you mean. Anyways, nice chatting with you!"},
    },
}


actor = Actor(script=script, start_label=("root", "start"), fallback_label=("root", "fallback"))
df_slots.register_storage(actor, SLOT_STORAGE_KEY)
df_slots.register_storage(actor, FORM_STORAGE_KEY)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s-%(name)15s:%(lineno)3s:%(funcName)20s():%(levelname)s - %(message)s",
        level=logging.INFO,
    )
    example_utils.run_interactive_mode(actor)

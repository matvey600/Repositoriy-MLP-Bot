import json
import os
from copy import deepcopy
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
USERS_DIR = os.path.join(MEMORY_DIR, "users")
LEGACY_STATE_FILE = os.path.join(MEMORY_DIR, "iskorka_state.json")
CURRENT_USER_ID = None


DEFAULT_STATE = {
    "current_mood": "calm",
    "mood_score": 55,
    "energy": 60,
    "curiosity": 55,
    "initiative": 35,
    "warmth": 35,
    "last_user_message_at": None,
    "last_autonomous_message_at": None,
    "last_mood_change": None
}


def set_current_user(user_id):
    global CURRENT_USER_ID

    CURRENT_USER_ID = str(user_id) if user_id is not None else None


def get_state_file():
    if CURRENT_USER_ID is None:
        return LEGACY_STATE_FILE

    return os.path.join(
        USERS_DIR,
        CURRENT_USER_ID,
        "iskorka_state.json"
    )


def now_iso():
    return datetime.now().isoformat()


def clamp(value, low=0, high=100):
    return max(
        low,
        min(
            high,
            value
        )
    )


def create_default_state():
    return deepcopy(DEFAULT_STATE)


def migrate_state(state):
    if not isinstance(state, dict):
        return create_default_state()

    default = create_default_state()

    for key, value in default.items():
        if key not in state:
            state[key] = value

    return state


def load_state():
    state_file = get_state_file()

    if not os.path.exists(state_file):
        state = create_default_state()
        save_state(state)
        return state

    try:
        with open(
            state_file,
            "r",
            encoding="utf-8"
        ) as file:
            return migrate_state(
                json.load(file)
            )

    except Exception:
        return create_default_state()


def save_state(state):
    state_file = get_state_file()

    os.makedirs(
        os.path.dirname(state_file),
        exist_ok=True
    )

    with open(
        state_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            state,
            file,
            ensure_ascii=False,
            indent=4
        )


def calculate_mood_name(state):
    mood_score = state.get(
        "mood_score",
        55
    )

    energy = state.get(
        "energy",
        60
    )

    curiosity = state.get(
        "curiosity",
        55
    )

    if mood_score < 30:
        return "sad"

    if energy < 25:
        return "tired"

    if curiosity >= 70:
        return "curious"

    if mood_score >= 70:
        return "happy"

    return "calm"


def restore_energy_from_pause(state, now):
    last_message = state.get(
        "last_user_message_at"
    )

    if not last_message:
        return state

    try:
        last_time = datetime.fromisoformat(
            last_message
        )
    except Exception:
        return state

    minutes_passed = (
        now
        -
        last_time
    ).total_seconds() / 60

    if minutes_passed < 10:
        return state

    restored = min(
        25,
        minutes_passed / 30
    )

    state["energy"] = clamp(
        state.get("energy", 60) + restored
    )

    return state


def update_state_from_event(event_type, relationship):
    state = load_state()
    now = datetime.now()

    previous_mood = state.get(
        "current_mood"
    )

    state = restore_energy_from_pause(
        state,
        now
    )

    state["last_user_message_at"] = now.isoformat()

    if event_type == "normal_conversation":
        state["energy"] -= 0.1
        state["curiosity"] += 0.5

    elif event_type == "positive":
        state["mood_score"] += 2
        state["warmth"] += 1
        state["energy"] += 1

    elif event_type == "shared_info":
        state["curiosity"] += 3
        state["warmth"] += 1.5
        state["initiative"] += 1
        state["energy"] += 0.4

    elif event_type == "help":
        state["mood_score"] += 2
        state["warmth"] += 2
        state["initiative"] += 0.5
        state["energy"] += 0.8

    elif event_type == "insult":
        state["mood_score"] -= 10
        state["warmth"] -= 6
        state["energy"] -= 5

    elif event_type == "apology":
        state["mood_score"] += 3
        state["warmth"] += 2
        state["energy"] += 1.5

    elif event_type == "flirt":
        state["mood_score"] += 1
        state["warmth"] += 1
        state["energy"] -= 0.3

    level = relationship.get(
        "level",
        "stranger"
    )

    level_initiative = {
        "stranger": 20,
        "acquaintance": 35,
        "friend": 50,
        "close_friend": 65,
        "partner": 75
    }

    state["initiative"] = max(
        state.get(
            "initiative",
            35
        ),
        level_initiative.get(
            level,
            20
        )
    )

    for key in [
        "mood_score",
        "energy",
        "curiosity",
        "initiative",
        "warmth"
    ]:
        state[key] = clamp(
            state.get(
                key,
                DEFAULT_STATE[key]
            )
        )

    state["current_mood"] = calculate_mood_name(state)

    if state["current_mood"] != previous_mood:
        state["last_mood_change"] = now_iso()

    save_state(state)

    return state


def mark_autonomous_message_sent():
    state = load_state()
    state["last_autonomous_message_at"] = now_iso()
    state["energy"] = clamp(
        state.get("energy", 60) - 2
    )
    save_state(state)
    return state


def get_state_context():
    state = load_state()

    mood_labels = {
        "calm": "спокойное",
        "happy": "радостное",
        "curious": "заинтересованное",
        "tired": "уставшее",
        "sad": "грустное"
    }

    return f"""
ВНУТРЕННЕЕ СОСТОЯНИЕ ИСКОРКИ:

Настроение: {mood_labels.get(state.get("current_mood"), state.get("current_mood"))}
Энергия: {state.get("energy")}/100
Любопытство: {state.get("curiosity")}/100
Инициативность: {state.get("initiative")}/100
Теплота: {state.get("warmth")}/100

Используй это состояние мягко. Не объясняй пользователю цифры и не говори, что у тебя есть внутреннее состояние.
"""

import json
import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
USERS_DIR = os.path.join(MEMORY_DIR, "users")
LEGACY_EVENTS_FILE = os.path.join(MEMORY_DIR, "bot_events.log")
CURRENT_USER_ID = None


def set_current_user(user_id):
    global CURRENT_USER_ID

    CURRENT_USER_ID = str(user_id) if user_id is not None else None


def get_events_file():
    if CURRENT_USER_ID is None:
        return LEGACY_EVENTS_FILE

    return os.path.join(
        USERS_DIR,
        CURRENT_USER_ID,
        "bot_events.log"
    )


def safe_relationship_snapshot(relationship):
    if not relationship:
        return None

    keys = [
        "level",
        "relationship_type",
        "relationship_score",
        "trust",
        "friendship",
        "respect",
        "comfort",
        "attachment",
        "interest",
        "resentment",
        "romance",
        "mood",
        "anger",
        "sadness",
        "interaction_count",
        "days_known",
        "last_interaction"
    ]

    return {
        key: relationship.get(key)
        for key in keys
    }


def log_event(event_type, **payload):
    events_file = get_events_file()

    os.makedirs(
        os.path.dirname(events_file),
        exist_ok=True
    )

    event = {
        "time": datetime.now().isoformat(),
        "user_id": CURRENT_USER_ID,
        "event_type": event_type,
        **payload
    }

    with open(
        events_file,
        "a",
        encoding="utf-8"
    ) as file:
        file.write(
            json.dumps(
                event,
                ensure_ascii=False
            )
            + "\n"
        )

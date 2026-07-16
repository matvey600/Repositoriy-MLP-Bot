import json
import os
import re
from copy import deepcopy
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
USERS_DIR = os.path.join(MEMORY_DIR, "users")
LEGACY_MEMORY_FILE = os.path.join(MEMORY_DIR, "memory.json")
CURRENT_USER_ID = None
MAX_EMOTIONS = 40
MAX_MEMORIES_IN_CONTEXT = 20
MAX_RELEVANT_ITEMS = 8


def set_current_user(user_id):
    global CURRENT_USER_ID

    CURRENT_USER_ID = str(user_id) if user_id is not None else None


def get_user_memory_dir():
    if CURRENT_USER_ID is None:
        return MEMORY_DIR

    return os.path.join(USERS_DIR, CURRENT_USER_ID)


def get_memory_file():
    if CURRENT_USER_ID is None:
        return LEGACY_MEMORY_FILE

    return os.path.join(get_user_memory_dir(), "memory.json")


def now_iso():
    return datetime.now().isoformat()


def normalize_text(value):
    if value is None:
        return ""

    return " ".join(str(value).strip().lower().split())


def tokenize(value):
    stop_words = {
        "а",
        "без",
        "бы",
        "в",
        "во",
        "вот",
        "да",
        "для",
        "до",
        "же",
        "за",
        "и",
        "из",
        "или",
        "как",
        "к",
        "ко",
        "ли",
        "мне",
        "мой",
        "моя",
        "мы",
        "на",
        "не",
        "но",
        "о",
        "об",
        "он",
        "она",
        "по",
        "с",
        "со",
        "то",
        "ты",
        "у",
        "что",
        "это",
        "я"
    }

    words = re.findall(r"[а-яёa-z0-9]+", normalize_text(value))

    return {
        word
        for word in words
        if len(word) > 2 and word not in stop_words
    }


def tokens_overlap(left_tokens, right_tokens):
    for left in left_tokens:
        for right in right_tokens:
            if left == right:
                return True

            if len(left) >= 4 and len(right) >= 4:
                if left.startswith(right[:4]) or right.startswith(left[:4]):
                    return True

    return False


def count_token_matches(left_tokens, right_tokens):
    matches = 0

    for left in left_tokens:
        if tokens_overlap({left}, right_tokens):
            matches += 1

    return matches


def create_default_memory():
    return {
        "version": 2,
        "user": {
            "name": None,
            "gender": None,
            "orientation": None,
            "age": None,
            "city": None,
            "location": None,
            "work": None,
            "study": None,
            "profession": None,
            "occupation": None,
            "hobbies": [],
            "interests": [],
            "likes": [],
            "dislikes": [],
            "goals": [],
            "dreams": [],
            "traits": [],
            "identity": []
        },
        "memories": [],
        "emotions": [],
        "events": [],
        "relationship_notes": []
    }


def merge_defaults(memory, default):
    if not isinstance(memory, dict):
        return deepcopy(default)

    for key, value in default.items():
        if key not in memory:
            memory[key] = deepcopy(value)
        elif isinstance(value, dict):
            memory[key] = merge_defaults(memory.get(key), value)
        elif isinstance(value, list) and not isinstance(memory.get(key), list):
            memory[key] = deepcopy(value)

    return memory


def normalize_memory_item(item):
    if not isinstance(item, dict):
        return None

    text = item.get("text") or item.get("reason")
    if not text:
        return None

    first_seen = item.get("first_seen") or item.get("date") or now_iso()
    last_seen = item.get("last_seen") or item.get("date") or first_seen

    return {
        "category": item.get("category", "general"),
        "text": text,
        "importance": item.get("importance", 1),
        "times_mentioned": item.get("times_mentioned", 1),
        "first_seen": first_seen,
        "last_seen": last_seen
    }


def normalize_emotion_item(item):
    if not isinstance(item, dict):
        return None

    text = item.get("text") or item.get("reason")
    emotion = item.get("emotion")

    if not emotion and not text:
        return None

    date = item.get("date") or item.get("last_seen") or now_iso()

    return {
        "emotion": emotion or "emotion",
        "text": text or emotion,
        "importance": item.get("importance", 1),
        "date": date,
        "times_mentioned": item.get("times_mentioned", 1)
    }


def migrate_memory(memory):
    default = create_default_memory()
    memory = merge_defaults(memory, default)

    user = memory["user"]

    if user.get("city") is None and user.get("location"):
        user["city"] = user["location"]

    if user.get("location") is None and user.get("city"):
        user["location"] = user["city"]

    if user.get("work") is None and user.get("occupation"):
        user["work"] = user["occupation"]

    if user.get("occupation") is None and user.get("work"):
        user["occupation"] = user["work"]

    memory["memories"] = [
        item for item in (normalize_memory_item(item) for item in memory["memories"])
        if item
    ]

    memory["emotions"] = [
        item for item in (normalize_emotion_item(item) for item in memory["emotions"])
        if item
    ][-MAX_EMOTIONS:]

    memory["version"] = default["version"]

    return memory


def load_memory():
    memory_file = get_memory_file()

    if not os.path.exists(memory_file):
        memory = create_default_memory()
        save_memory(memory)
        return memory

    try:
        with open(memory_file, "r", encoding="utf-8") as file:
            memory = json.load(file)

        return migrate_memory(memory)

    except Exception:
        return create_default_memory()


def save_memory(memory):
    memory_file = get_memory_file()

    os.makedirs(os.path.dirname(memory_file), exist_ok=True)

    with open(memory_file, "w", encoding="utf-8") as file:
        json.dump(memory, file, ensure_ascii=False, indent=4)


def add_to_list(category, value):
    memory = load_memory()

    if category not in memory["user"] or not isinstance(memory["user"][category], list):
        return

    normalized_value = normalize_text(value)

    if not normalized_value:
        return

    existing_values = {
        normalize_text(item)
        for item in memory["user"][category]
    }

    if normalized_value not in existing_values:
        memory["user"][category].append(str(value).strip())

    save_memory(memory)


def set_user_name(name):
    set_user_data("name", name)


def get_user_name():
    memory = load_memory()
    return memory["user"].get("name")


def set_user_data(field, value):
    memory = load_memory()

    if field not in memory["user"]:
        return

    if isinstance(memory["user"][field], list):
        add_to_list(field, value)
        return

    clean_value = str(value).strip() if value is not None else None
    memory["user"][field] = clean_value

    if field == "city":
        memory["user"]["location"] = clean_value
    elif field == "location":
        memory["user"]["city"] = clean_value
    elif field == "work":
        memory["user"]["occupation"] = clean_value
    elif field == "occupation":
        memory["user"]["work"] = clean_value

    save_memory(memory)


def upsert_record(records, new_record):
    new_key = normalize_text(new_record.get("text"))

    for record in records:
        if normalize_text(record.get("text")) == new_key:
            record["importance"] = max(
                record.get("importance", 1),
                new_record.get("importance", 1)
            )
            record["times_mentioned"] = record.get("times_mentioned", 1) + 1
            record["last_seen"] = now_iso()
            return False

    records.append(new_record)
    return True


def add_memory(category, text, importance=1):
    memory = load_memory()
    clean_text = str(text).strip()

    if not clean_text:
        return

    record = {
        "category": category,
        "text": clean_text,
        "importance": importance,
        "times_mentioned": 1,
        "first_seen": now_iso(),
        "last_seen": now_iso()
    }

    upsert_record(memory["memories"], record)
    save_memory(memory)


def add_event(category, text, importance=1):
    memory = load_memory()
    clean_text = str(text).strip()

    if not clean_text:
        return

    record = {
        "category": category,
        "text": clean_text,
        "importance": importance,
        "times_mentioned": 1,
        "first_seen": now_iso(),
        "last_seen": now_iso()
    }

    upsert_record(memory["events"], record)
    save_memory(memory)


def add_emotion(emotion, text, importance=1):
    memory = load_memory()
    clean_text = str(text).strip()

    if not clean_text:
        return

    normalized_text = normalize_text(clean_text)

    for item in memory["emotions"]:
        if (
            normalize_text(item.get("emotion")) == normalize_text(emotion)
            and normalize_text(item.get("text")) == normalized_text
        ):
            item["importance"] = max(item.get("importance", 1), importance)
            item["times_mentioned"] = item.get("times_mentioned", 1) + 1
            item["date"] = now_iso()
            save_memory(memory)
            return

    memory["emotions"].append(
        {
            "emotion": emotion,
            "text": clean_text,
            "importance": importance,
            "date": now_iso(),
            "times_mentioned": 1
        }
    )

    memory["emotions"] = memory["emotions"][-MAX_EMOTIONS:]
    save_memory(memory)


def add_relationship_note(text):
    memory = load_memory()
    clean_text = str(text).strip()

    if not clean_text:
        return

    existing_notes = {
        normalize_text(note)
        for note in memory["relationship_notes"]
    }

    if normalize_text(clean_text) not in existing_notes:
        memory["relationship_notes"].append(clean_text)

    save_memory(memory)


def get_memory():
    return load_memory()


def format_user_field(key, value):
    labels = {
        "name": "Имя",
        "gender": "Род обращения",
        "orientation": "Ориентация",
        "age": "Возраст",
        "city": "Город",
        "work": "Работа",
        "study": "Учёба",
        "profession": "Профессия",
        "hobbies": "Хобби",
        "interests": "Интересы",
        "likes": "Любимые вещи",
        "dislikes": "Нелюбимые вещи",
        "goals": "Цели",
        "dreams": "Мечты",
        "traits": "Черты характера",
        "identity": "Личная идентичность"
    }

    label = labels.get(key, key)

    if isinstance(value, list):
        return f"{label}: {', '.join(value)}"

    return f"{label}: {value}"


def score_memory_item(item, query_tokens):
    item_tokens = tokenize(item.get("text", ""))
    matches = count_token_matches(query_tokens, item_tokens)

    if matches == 0:
        return 0

    importance = item.get("importance", 1)
    mentions = item.get("times_mentioned", 1)

    return matches * 10 + importance + min(mentions, 5)


def get_relevant_items(items, user_message, limit=MAX_RELEVANT_ITEMS):
    query_tokens = tokenize(user_message)

    if not query_tokens:
        return []

    scored_items = []

    for item in items:
        score = score_memory_item(item, query_tokens)

        if score > 0:
            scored_items.append((score, item))

    scored_items.sort(
        key=lambda pair: (
            pair[0],
            pair[1].get("importance", 1),
            pair[1].get("last_seen", pair[1].get("date", ""))
        ),
        reverse=True
    )

    return [
        item
        for _, item in scored_items[:limit]
    ]


def get_recent_emotions(memory, limit=5):
    return sorted(
        memory["emotions"],
        key=lambda item: item.get("date", ""),
        reverse=True
    )[:limit]


def is_emotion_related_message(user_message):
    text = normalize_text(user_message)

    emotion_markers = [
        "груст",
        "печал",
        "устал",
        "тяжел",
        "тяжёл",
        "стресс",
        "нерв",
        "тревож",
        "злю",
        "зол",
        "злая",
        "бесит",
        "рад",
        "счаст",
        "настроение",
        "самочувствие",
        "как дела",
        "как я",
        "как мне",
        "поддерж",
        "плохо",
        "хорошо"
    ]

    return any(marker in text for marker in emotion_markers)


def get_relevant_user_facts(memory, user_message):
    user = memory["user"]
    query_tokens = tokenize(user_message)
    result = []

    always_use = [
        "name",
        "gender",
        "orientation"
    ]

    thematic_fields = [
        "age",
        "city",
        "work",
        "study",
        "profession",
        "hobbies",
        "interests",
        "likes",
        "dislikes",
        "goals",
        "dreams",
        "traits",
        "identity"
    ]

    for key in always_use:
        value = user.get(key)

        if value:
            result.append(format_user_field(key, value))

    for key in thematic_fields:
        value = user.get(key)

        if not value:
            continue

        if isinstance(value, list):
            relevant_values = [
                item for item in value
                if tokens_overlap(query_tokens, tokenize(item))
            ]

            if relevant_values:
                result.append(format_user_field(key, relevant_values))
        elif tokens_overlap(query_tokens, tokenize(value)):
            result.append(format_user_field(key, value))

    return result


def get_relevant_memory_context(user_message):
    memory = load_memory()
    result = []

    user_facts = get_relevant_user_facts(memory, user_message)
    relevant_memories = get_relevant_items(memory["memories"], user_message)
    relevant_events = get_relevant_items(memory["events"], user_message, limit=5)
    recent_emotions = []

    if is_emotion_related_message(user_message):
        recent_emotions = get_recent_emotions(memory)

    result.append("ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ:")

    if user_facts:
        result.extend(user_facts)
    else:
        result.append("Нет устойчивых фактов, связанных с текущим сообщением.")

    if relevant_memories:
        result.append("\nРЕЛЕВАНТНЫЕ ВОСПОМИНАНИЯ:")

        for item in relevant_memories:
            result.append(f"- {item['text']}")

    if relevant_events:
        result.append("\nСВЯЗАННЫЕ СОБЫТИЯ:")

        for item in relevant_events:
            result.append(f"- {item['text']}")

    if recent_emotions:
        result.append("\nНЕДАВНЕЕ ЭМОЦИОНАЛЬНОЕ СОСТОЯНИЕ:")

        for emotion in recent_emotions:
            result.append(f"- {emotion['emotion']}: {emotion['text']}")

    result.append(
        "\nПРАВИЛО ИСПОЛЬЗОВАНИЯ ПАМЯТИ:\n"
        "Используй воспоминания естественно и только если они действительно подходят к разговору. "
        "Не говори, что ты записала или обновила память. "
        "Если род обращения не указан в памяти, не угадывай его и избегай гендерных форм."
    )

    return "\n".join(result)


def get_memory_context():
    memory = load_memory()
    result = []

    user = memory["user"]
    user_fields = [
        "name",
        "gender",
        "orientation",
        "age",
        "city",
        "work",
        "study",
        "profession",
        "hobbies",
        "interests",
        "likes",
        "dislikes",
        "goals",
        "dreams",
        "traits",
        "identity"
    ]

    result.append("ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ:")

    for key in user_fields:
        value = user.get(key)

        if value:
            result.append(format_user_field(key, value))

    memories = sorted(
        memory["memories"],
        key=lambda item: item.get("importance", 1),
        reverse=True
    )

    if memories:
        result.append("\nВАЖНЫЕ ВОСПОМИНАНИЯ:")

        for item in memories[:MAX_MEMORIES_IN_CONTEXT]:
            result.append(f"- {item['text']}")

    if memory["emotions"]:
        result.append("\nЭМОЦИОНАЛЬНЫЕ ВОСПОМИНАНИЯ:")

        for emotion in memory["emotions"][-8:]:
            result.append(f"- {emotion['emotion']}: {emotion['text']}")

    events = sorted(
        memory["events"],
        key=lambda item: item.get("importance", 1),
        reverse=True
    )

    if events:
        result.append("\nСОБЫТИЯ:")

        for event in events[:10]:
            result.append(f"- {event['text']}")

    if memory["relationship_notes"]:
        result.append("\nЗАМЕТКИ ОБ ОБЩЕНИИ:")

        for note in memory["relationship_notes"]:
            result.append("- " + note)

    return "\n".join(result)

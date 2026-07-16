import json
import os

from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
USERS_DIR = os.path.join(MEMORY_DIR, "users")
LEGACY_RELATIONSHIP_FILE = os.path.join(MEMORY_DIR, "relationship.json")
CURRENT_USER_ID = None

RELATIONSHIP_LEVELS = [
    "stranger",
    "acquaintance",
    "friend",
    "close_friend",
    "partner"
]

RELATIONSHIP_LEVEL_RANK = {
    level: index
    for index, level in enumerate(RELATIONSHIP_LEVELS)
}


def set_current_user(user_id):
    global CURRENT_USER_ID

    CURRENT_USER_ID = str(user_id) if user_id is not None else None


def get_relationship_file():
    if CURRENT_USER_ID is None:
        return LEGACY_RELATIONSHIP_FILE

    return os.path.join(
        USERS_DIR,
        CURRENT_USER_ID,
        "relationship.json"
    )



# ==================================================
# DEFAULT
# ==================================================

DEFAULT_RELATIONSHIP = {


    "level": "stranger",

    "auto_level": "stranger",

    "correct_level": "stranger",

    "manual_level": None,

    "custom_level": None,

    "manual_level_set_at": None,

    "manual_level_note": None,

    "relationship_type": "stranger",



    # главный показатель

    "relationship_score": 0,



    # основные параметры

    "trust": 0,

    "friendship": 0,

    "respect": 0,



    # скрытые

    "comfort": 0,

    "attachment": 0,

    "interest": 0,

    "resentment": 0,



    # романтика

    "romance": 0,



    # эмоции

    "mood": 50,

    "anger": 0,

    "sadness": 0,



    # статистика

    "interaction_count": 0,

    "days_known": 0,


    "first_interaction": None,

    "last_interaction": None

}





# ==================================================
# LOAD
# ==================================================


def load_relationship():
    relationship_file = get_relationship_file()


    if not os.path.exists(
        relationship_file
    ):


        data = DEFAULT_RELATIONSHIP.copy()

        save_relationship(data)

        return data



    try:


        with open(
            relationship_file,
            "r",
            encoding="utf-8"
        ) as file:


            data = json.load(file)



        # добавляем новые поля

        for key, value in DEFAULT_RELATIONSHIP.items():


            if key not in data:


                data[key] = value


        if data.get("correct_level") is None:
            data["correct_level"] = data.get(
                "auto_level",
                data.get("level", "stranger")
            )

        if data.get("custom_level") is None and data.get("manual_level"):
            data["custom_level"] = data.get("manual_level")

        if data.get("manual_level") is None and data.get("custom_level"):
            data["manual_level"] = data.get("custom_level")


        return data



    except Exception:


        return DEFAULT_RELATIONSHIP.copy()







# ==================================================
# SAVE
# ==================================================


def save_relationship(data):
    relationship_file = get_relationship_file()


    os.makedirs(
        os.path.dirname(relationship_file),
        exist_ok=True
    )



    with open(
        relationship_file,
        "w",
        encoding="utf-8"
    ) as file:


        json.dump(

            data,

            file,

            ensure_ascii=False,

            indent=4

        )








# ==================================================
# LIMIT
# ==================================================


def clamp(value):


    return max(

        0,

        min(

            500,

            value

        )

    )


def normalize_level(level):
    if level is None:
        return None

    value = str(level).strip().lower()

    aliases = {
        "stranger": "stranger",
        "незнакомец": "stranger",
        "незнакомка": "stranger",
        "незнакомые": "stranger",
        "acquaintance": "acquaintance",
        "знакомый": "acquaintance",
        "знакомая": "acquaintance",
        "знакомые": "acquaintance",
        "friend": "friend",
        "друг": "friend",
        "подруга": "friend",
        "close_friend": "close_friend",
        "close friend": "close_friend",
        "близкий друг": "close_friend",
        "близкая подруга": "close_friend",
        "близкий_друг": "close_friend",
        "partner": "partner",
        "партнер": "partner",
        "партнёр": "partner",
        "пара": "partner"
    }

    return aliases.get(value)


def apply_effective_level(r):
    auto_level = normalize_level(
        r.get("auto_level")
    ) or "stranger"

    correct_level = normalize_level(
        r.get("correct_level")
    ) or auto_level

    effective_level = correct_level

    r["auto_level"] = auto_level
    r["correct_level"] = correct_level

    r["level"] = effective_level

    if effective_level == "partner":
        r["relationship_type"] = "partner"
    elif r.get("romance", 0) >= 50:
        r["relationship_type"] = "romantic_interest"
    else:
        r["relationship_type"] = effective_level

    return r








# ==================================================
# UPDATE
# ==================================================


def update_relationship(event_type):


    r = load_relationship()


    now = datetime.now()



    # первое знакомство


    if r["first_interaction"] is None:


        r["first_interaction"] = now.isoformat()



    first = datetime.fromisoformat(

        r["first_interaction"]

    )


    r["days_known"] = (

        now.date()

        -

        first.date()

    ).days





    # ==================================================
    # СОБЫТИЯ
    # ==================================================


    if event_type == "normal_conversation":


        r["comfort"] += 0.2

        r["interest"] += 0.1





    elif event_type == "positive":


        r["friendship"] += 1

        r["trust"] += 0.5

        r["comfort"] += 1





    elif event_type == "shared_info":


        r["trust"] += 1.5

        r["friendship"] += 1

        r["interest"] += 1.5

        r["comfort"] += 1





    elif event_type == "help":


        r["trust"] += 2

        r["friendship"] += 2

        r["respect"] += 1.5

        r["attachment"] += 0.5





    elif event_type == "insult":


        r["trust"] -= 10

        r["friendship"] -= 8

        r["respect"] -= 5


        r["resentment"] += 15

        r["anger"] += 25

        r["comfort"] -= 10





    elif event_type == "apology":


        r["trust"] += 1.5

        r["respect"] += 1.5


        r["resentment"] -= 10

        r["anger"] -= 15





    elif event_type == "flirt":


        r["comfort"] += 0.5



        if (

            r["trust"] >= 50

            and

            r["attachment"] >= 30

        ):


            r["romance"] += 1







    # ==================================================
    # ЕСТЕСТВЕННЫЕ ИЗМЕНЕНИЯ
    # ==================================================


    if event_type != "insult":


        r["anger"] -= 1

        r["resentment"] -= 0.2




    # привязанность


    if (

        r["trust"] >= 30

        and

        r["comfort"] >= 30

    ):


        r["attachment"] += 0.1






    # ==================================================
    # LIMITS
    # ==================================================


    for key in [

        "trust",

        "friendship",

        "respect",

        "comfort",

        "attachment",

        "interest",

        "resentment",

        "romance",

        "anger"

    ]:


        r[key] = clamp(

            r[key]

        )




    # ==================================================
    # SCORE
    # ==================================================


    r["relationship_score"] = (

        r["trust"]

        +

        r["friendship"]

        +

        r["respect"]

        +

        r["comfort"]

        +

        r["attachment"]

        +

        r["interest"]

        +

        r["romance"]

        -

        r["resentment"]

    )



    if r["relationship_score"] < 0:

        r["relationship_score"] = 0




    r["interaction_count"] += 1


    r["last_interaction"] = now.isoformat()






    r = calculate_level(r)



    save_relationship(r)


    return r







# ==================================================
# LEVEL
# ==================================================


def calculate_level(r):


    score = r.get(

        "relationship_score",

        0

    )


    days = r.get(

        "days_known",

        0

    )



    # =========================
    # ПАРА
    # =========================


    if (

        score >= 500

        and

        days >= 90

        and

        r["romance"] >= 100

        and

        r["attachment"] >= 100

    ):


        r["level"] = "partner"

        r["auto_level"] = "partner"

        r["correct_level"] = "partner"

        r["relationship_type"] = "partner"


        return apply_effective_level(r)






    # =========================
    # БЛИЗКИЙ ДРУГ
    # =========================


    if (

        score >= 300

        and

        days >= 30

    ):


        r["level"] = "close_friend"






    # =========================
    # ДРУГ
    # =========================


    elif (

        score >= 150

        and

        days >= 7

    ):


        r["level"] = "friend"






    # =========================
    # ЗНАКОМЫЙ
    # =========================


    elif (

        score >= 50

        and

        days >= 1

    ):


        r["level"] = "acquaintance"






    else:


        r["level"] = "stranger"







    r["auto_level"] = r["level"]

    r["correct_level"] = r["level"]


    if r["romance"] >= 50:


        r["relationship_type"] = "romantic_interest"


    else:


        r["relationship_type"] = r["level"]




    return apply_effective_level(r)


def set_manual_relationship_level(level, note=None):
    normalized_level = normalize_level(level)

    if normalized_level is None:
        raise ValueError("Unknown relationship level")

    r = load_relationship()
    r["manual_level"] = normalized_level
    r["custom_level"] = normalized_level
    r["manual_level_set_at"] = datetime.now().isoformat()
    r["manual_level_note"] = note

    r = calculate_level(r)
    save_relationship(r)

    return r


def clear_manual_relationship_level():
    r = load_relationship()
    r["manual_level"] = None
    r["custom_level"] = None
    r["manual_level_set_at"] = None
    r["manual_level_note"] = None

    r = calculate_level(r)
    save_relationship(r)

    return r







# ==================================================
# GET
# ==================================================


def get_relationship():


    return load_relationship()

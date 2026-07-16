import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
USERS_DIR = os.path.join(MEMORY_DIR, "users")
LEGACY_HISTORY_FILE = os.path.join(MEMORY_DIR, "chat_history.json")
CURRENT_USER_ID = None


MAX_MESSAGES = 10


def set_current_user(user_id):
    global CURRENT_USER_ID

    CURRENT_USER_ID = str(user_id) if user_id is not None else None


def get_history_file():
    if CURRENT_USER_ID is None:
        return LEGACY_HISTORY_FILE

    return os.path.join(
        USERS_DIR,
        CURRENT_USER_ID,
        "chat_history.json"
    )



def load_history():
    history_file = get_history_file()

    if not os.path.exists(history_file):
        return []


    try:
        with open(
            history_file,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)


    except Exception:

        return []




def save_history(history):
    history_file = get_history_file()

    os.makedirs(
        os.path.dirname(history_file),
        exist_ok=True
    )


    with open(
        history_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            history,
            file,
            ensure_ascii=False,
            indent=4
        )




def add_message(
    user_message: str,
    bot_message: str
):

    history = load_history()


    history.append(
        {
            "user": user_message,
            "bot": bot_message
        }
    )


    # оставляем только последние сообщения

    history = history[-MAX_MESSAGES:]


    save_history(history)




def get_history_text():

    history = load_history()


    if not history:
        return "Истории разговора пока нет."


    text = ""


    for item in history:

        text += f"""
Пользователь:
{item["user"]}

Искорка:
{item["bot"]}

"""


    return text

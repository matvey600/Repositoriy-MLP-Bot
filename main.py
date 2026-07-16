from aiogram import Bot, Dispatcher

from aiogram.types import Message

from aiogram.client.session.aiohttp import AiohttpSession



from dotenv import load_dotenv



from ai.ai_manager import (

    ask_ai,

    ask_ai_with_image,

    ask_ai_with_images,

    ask_gemini_random_message

)



from memory_manager import (

    get_memory_context,

    get_relevant_memory_context,

    set_current_user as set_current_memory_user

)



from chat_history import (

    add_message,

    get_history_text,

    set_current_user as set_current_history_user

)



from memory.relationship_brain import (

    get_relationship,

    set_manual_relationship_level,

    clear_manual_relationship_level,

    update_relationship,

    set_current_user as set_current_relationship_user

)



from memory.relationship_events import (

    analyze_relationship_event

)



from memory.relationship_personality import (

    get_relationship_personality

)



from memory.memory_brain import (

    analyze_memory

)



from memory.iskorka_state import (

    get_state_context,

    load_state,

    mark_autonomous_message_sent,

    set_current_user as set_current_state_user,

    update_state_from_event

)



from bot_events import (

    log_event,

    safe_relationship_snapshot,

    set_current_user as set_current_events_user

)





import asyncio
from io import BytesIO

import os

import json

import random

import re



from datetime import datetime, timedelta







# =====================================================

# SETTINGS

# =====================================================





load_dotenv()





BOT_TOKEN = os.getenv(

    "BOT_TOKEN"

)





BASE_DIR = os.path.dirname(

    os.path.abspath(__file__)

)

USER_FILE = os.path.join(

    BASE_DIR,

    "memory",

    "user_settings.json"

)

AUTONOMOUS_MESSAGE_COOLDOWN_HOURS = 6

MEDIA_GROUP_WAIT_SECONDS = 2.0

MEDIA_GROUPS = {}

RELATIONSHIP_LEVEL_LABELS = {
    "stranger": "незнакомцы",
    "acquaintance": "знакомые",
    "friend": "друзья",
    "close_friend": "близкие друзья",
    "partner": "пара"
}

RELATIONSHIP_LEVEL_ALIASES = {
    "незнакомец": "stranger",
    "незнакомка": "stranger",
    "незнакомые": "stranger",
    "stranger": "stranger",
    "знакомый": "acquaintance",
    "знакомая": "acquaintance",
    "знакомые": "acquaintance",
    "acquaintance": "acquaintance",
    "друг": "friend",
    "друзья": "friend",
    "friend": "friend",
    "близкий друг": "close_friend",
    "близкие друзья": "close_friend",
    "близкий_друг": "close_friend",
    "close_friend": "close_friend",
    "close friend": "close_friend",
    "партнер": "partner",
    "партнёр": "partner",
    "пара": "partner",
    "partner": "partner"
}


def get_relationship_level_label(level):
    return RELATIONSHIP_LEVEL_LABELS.get(
        level,
        level or "неизвестно"
    )


def parse_relationship_status_command(text):
    value = text.strip().lower()

    if value in [
        "/статус",
        "/relationship",
        "/отношения"
    ]:
        return "show", None

    for prefix in [
        "/статус ",
        "/relationship ",
        "/отношения "
    ]:
        if value.startswith(prefix):
            argument = value[len(prefix):].strip()

            if argument in [
                "авто",
                "auto",
                "правильный",
                "правильная",
                "настоящий",
                "настоящая",
                "true",
                "correct",
                "сброс",
                "reset"
            ]:
                return "clear", None

            for personal_prefix in [
                "мой ",
                "моя ",
                "моё ",
                "мое "
            ]:
                if argument.startswith(personal_prefix):
                    argument = argument[len(personal_prefix):].strip()

            level = RELATIONSHIP_LEVEL_ALIASES.get(argument)

            if level is not None:
                return "show", None

    return None, None


def build_relationship_status_text(relationship):
    current_level = get_relationship_level_label(
        relationship.get("level")
    )

    correct_level = get_relationship_level_label(
        relationship.get(
            "correct_level",
            relationship.get("auto_level")
        )
    )

    return (
        "Сейчас фактический статус: "
        f"{current_level}.\n"
        "Он считается только правильной системой: "
        f"{correct_level}."
    )


def set_current_bot_user(user_id):

    set_current_memory_user(

        user_id

    )

    set_current_history_user(

        user_id

    )

    set_current_relationship_user(

        user_id

    )

    set_current_events_user(

        user_id

    )

    set_current_state_user(

        user_id

    )











# =====================================================

# BOT

# =====================================================





session = AiohttpSession(

    proxy="http://127.0.0.1:10809"

)





bot = Bot(

    token=BOT_TOKEN,

    session=session

)





dp = Dispatcher()











# =====================================================

# USER ID

# =====================================================





def dedupe_user_ids(user_ids):

    result = []

    seen = set()

    for user_id in user_ids:

        if user_id is None:

            continue

        key = str(user_id)

        if key in seen:

            continue

        seen.add(key)

        result.append(user_id)

    return result


def save_user_id(user_id):



    os.makedirs(

        os.path.dirname(USER_FILE),

        exist_ok=True

    )





    user_ids = []



    try:

        with open(

            USER_FILE,

            "r",

            encoding="utf-8"

        ) as file:

            old_data = json.load(file)

            if isinstance(old_data, dict):

                user_ids.extend(

                    old_data.get(

                    "user_ids",

                    []

                    )

                )

                old_user_id = old_data.get(

                    "user_id"

                )

                if old_user_id:

                    user_ids.append(

                        old_user_id

                    )

    except:

        pass



    user_ids.append(

        user_id

    )


    data = {

        "user_id": user_id,

        "user_ids": dedupe_user_ids(

            user_ids

        )

    }



    with open(

        USER_FILE,

        "w",

        encoding="utf-8"

    ) as file:



        json.dump(

            data,

            file,

            ensure_ascii=False,

            indent=4

        )











def get_saved_user_id():



    try:



        with open(

            USER_FILE,

            "r",

            encoding="utf-8"

        ) as file:



            data = json.load(file)



            return data.get(

                "user_id"

            )





    except:



        return None



def get_saved_user_ids():



    try:



        with open(

            USER_FILE,

            "r",

            encoding="utf-8"

        ) as file:



            data = json.load(file)

            user_ids = data.get(

                "user_ids",

                []

            )

            if not user_ids and data.get("user_id"):

                user_ids = [

                    data.get("user_id")

                ]

            if data.get("user_id"):

                user_ids.append(

                    data.get("user_id")

                )

            return dedupe_user_ids(

                user_ids

            )



    except:



        return []











# =====================================================

# CONTEXT FOR AI

# =====================================================





def is_memory_recall_request(user_message):

    text = user_message.lower().strip()

    recall_phrases = [

        "что ты помнишь",

        "что помнишь",

        "что ты знаешь обо мне",

        "что знаешь обо мне",

        "что ты обо мне знаешь",

        "что вообще обо мне знаешь",

        "что вообще помнишь",

        "расскажи что ты помнишь",

        "расскажи что знаешь обо мне",

        "какая у тебя память обо мне",

        "вспоминай все",

        "вспоминай всё",

        "вспомни все",

        "вспомни всё",

        "вспомни обо мне",

        "вспоминай обо мне",

        "всю память",

        "полную память"

    ]

    return any(

        phrase in text

        for phrase in recall_phrases

    )


def build_memory_context(user_message=None):


    recall_request = bool(

        user_message

        and

        is_memory_recall_request(

            user_message

        )

    )


    if recall_request:

        memory = get_memory_context()

    elif user_message:

        memory = get_relevant_memory_context(

            user_message

        )

    else:

        memory = get_memory_context()


    if recall_request:

        memory += (

            "\n\nЗАПРОС ПОЛНОЙ ПАМЯТИ:\n"

            "Пользователь прямо просит вспомнить, что ты о нём знаешь. "

            "Перечисли реальные факты из памяти: хобби, интересы, любимые вещи, цели, важные воспоминания и недавние эмоции. "

            "Не говори, что почти ничего не знаешь, если в памяти есть факты. "

            "Можно звучать живо, но не пропускай сохранённые факты."

        )



    relationship = get_relationship()





    personality = get_relationship_personality(

        relationship

    )

    iskorka_state = get_state_context()





    return f"""



========================

ПАМЯТЬ ПОЛЬЗОВАТЕЛЯ

========================





{memory}







========================

ОТНОШЕНИЯ

========================





Уровень:

{relationship.get("level")}





Тип:

{relationship.get("relationship_type")}





Доверие:

{relationship.get("trust")}/100





Дружба:

{relationship.get("friendship")}/100





Уважение:

{relationship.get("respect")}/100





Комфорт:

{relationship.get("comfort")}/100





Привязанность:

{relationship.get("attachment")}/100





Интерес:

{relationship.get("interest")}/100





Обида:

{relationship.get("resentment")}/100





Романтика:

{relationship.get("romance")}/100





Настроение:

{relationship.get("mood")}/100





Злость:

{relationship.get("anger")}/100





Количество сообщений:

{relationship.get("interaction_count")}





Дней знакомства:

{relationship.get("days_known")}



========================

СОСТОЯНИЕ ИСКОРКИ

========================



{iskorka_state}







========================

ПОВЕДЕНИЕ ИСКОРКИ

========================





{personality}



"""


# =====================================================

# MESSAGE SPLITTING

# =====================================================



MAX_TELEGRAM_PART_LENGTH = 550



def split_long_sentence(sentence, max_length):

    words = sentence.split()

    parts = []

    current = ""



    for word in words:

        candidate = f"{current} {word}".strip()

        if len(candidate) <= max_length:

            current = candidate

        else:

            if current:

                parts.append(current)

            current = word



    if current:

        parts.append(current)



    return parts



def split_bot_answer(text, max_length=MAX_TELEGRAM_PART_LENGTH):

    if not text:

        return []



    clean_text = str(text).strip()

    if len(clean_text) <= max_length:

        return [clean_text]



    raw_blocks = [

        block.strip()

        for block in re.split(r"\n\s*\n", clean_text)

        if block.strip()

    ]



    pieces = []



    for block in raw_blocks:

        if len(block) <= max_length:

            pieces.append(block)

            continue



        sentences = [

            sentence.strip()

            for sentence in re.split(r"(?<=[.!?…])\s+", block)

            if sentence.strip()

        ]



        for sentence in sentences:

            if len(sentence) <= max_length:

                pieces.append(sentence)

            else:

                pieces.extend(

                    split_long_sentence(

                        sentence,

                        max_length

                    )

                )



    messages = []

    current = ""



    for piece in pieces:

        candidate = f"{current}\n\n{piece}".strip()

        if len(candidate) <= max_length:

            current = candidate

        else:

            if current:

                messages.append(current)

            current = piece



    if current:

        messages.append(current)



    return messages



async def answer_in_parts(message, text):

    parts = split_bot_answer(text)



    for index, part in enumerate(parts):

        await message.answer(

            part

        )



        if index < len(parts) - 1:

            await asyncio.sleep(

                random.uniform(

                    0.7,

                    1.4

                )

            )



async def send_message_in_parts(user_id, text):

    parts = split_bot_answer(text)



    for index, part in enumerate(parts):

        await bot.send_message(

            user_id,

            part

        )



        if index < len(parts) - 1:

            await asyncio.sleep(

                random.uniform(

                    0.7,

                    1.4

                )

            )

# =====================================================

# STICKERS

# =====================================================



def build_sticker_message(sticker):

    parts = [

        "Пользователь отправил стикер"

    ]



    if sticker.emoji:

        parts.append(

            f"emoji: {sticker.emoji}"

        )



    if sticker.set_name:

        parts.append(

            f"набор: {sticker.set_name}"

        )



    if sticker.is_animated:

        parts.append(

            "тип: анимированный стикер"

        )

    elif sticker.is_video:

        parts.append(

            "тип: видео-стикер"

        )

    else:

        parts.append(

            "тип: статичный стикер-картинка"

        )



    return "[" + "; ".join(parts) + "]"



async def download_static_sticker(sticker):

    if sticker.is_animated or sticker.is_video:

        return None, None



    file = await bot.get_file(

        sticker.file_id

    )

    buffer = BytesIO()

    await bot.download_file(

        file.file_path,

        destination=buffer

    )

    return buffer.getvalue(), "image/webp"


def build_photo_message(message):

    if message.caption:

        return (

            "[Пользователь отправил фотографию; подпись: "

            f"{message.caption}]"

        )

    return "[Пользователь отправил фотографию]"


async def download_photo(message):

    if not message.photo:

        return None, None

    photo = message.photo[-1]

    file = await bot.get_file(

        photo.file_id

    )

    buffer = BytesIO()

    await bot.download_file(

        file.file_path,

        destination=buffer

    )

    return buffer.getvalue(), "image/jpeg"



# =====================================================

# USER MESSAGE

# =====================================================





async def process_photo_media_group(media_group_key):

    await asyncio.sleep(

        MEDIA_GROUP_WAIT_SECONDS

    )

    album = MEDIA_GROUPS.pop(

        media_group_key,

        None

    )

    if not album:

        return

    message = album["message"]

    image_items = album["images"]

    captions = [

        caption

        for caption in album["captions"]

        if caption

    ]

    photo_count = len(

        image_items

    )

    if captions:

        user_text = (

            f"[Пользователь отправил альбом из {photo_count} фотографий; "

            f"подпись: {' | '.join(captions)}]"

        )

    else:

        user_text = f"[Пользователь отправил альбом из {photo_count} фотографий]"

    user_id = message.from_user.id

    set_current_bot_user(

        user_id

    )

    save_user_id(

        user_id

    )

    relationship_command, relationship_level = parse_relationship_status_command(
        user_text
    )

    if relationship_command == "show":
        relationship = get_relationship()

        await message.answer(
            build_relationship_status_text(relationship)
        )

        return

    if relationship_command == "set":
        relationship = set_manual_relationship_level(
            relationship_level,
            note="telegram_command"
        )

        log_event(
            "manual_relationship_level_set",
            message=user_text,
            relationship=safe_relationship_snapshot(
                relationship
            )
        )

        await message.answer(
            "Готово. Теперь фактический статус: "
            f"{get_relationship_level_label(relationship.get('level'))}.\n"
            "Правильная система не отключена: score и correct_level продолжат считаться."
        )

        return

    if relationship_command == "clear":
        relationship = clear_manual_relationship_level()

        log_event(
            "manual_relationship_level_clear",
            message=user_text,
            relationship=safe_relationship_snapshot(
                relationship
            )
        )

        await message.answer(
            "Готово. Статус возвращён к правильной системе.\n"
            "Теперь фактический статус: "
            f"{get_relationship_level_label(relationship.get('level'))}."
        )

        return


    print("\n========================")

    print(

        f"Пользователь ID: {user_id}"

    )

    print(

        f"Сообщение: {user_text}"

    )

    print("========================")

    relationship_before = get_relationship()

    log_event(

        "incoming_message",

        message=user_text,

        message_kind="photo_album",

        has_image=True,

        image_count=photo_count,

        relationship_before=safe_relationship_snapshot(

            relationship_before

        )

    )

    try:

        analyze_memory(

            user_text

        )

        print(

            "[MEMORY] OK"

        )

        event = analyze_relationship_event(

            user_text

        )

        print(

            "[RELATIONSHIP EVENT]",

            event

        )

        relationship = update_relationship(

            event

        )

        iskorka_state = update_state_from_event(

            event,

            relationship

        )

        log_event(

            "relationship_update",

            relationship_event=event,

            relationship_before=safe_relationship_snapshot(

                relationship_before

            ),

            relationship_after=safe_relationship_snapshot(

                relationship

            ),

            iskorka_state=iskorka_state

        )

        memory_context = build_memory_context(

            user_text

        )

        history = get_history_text()

        answer = ask_ai_with_images(

            user_text,

            image_items,

            history,

            memory_context

        )

        print(

            "\nОтвет ИИ:"

        )

        print(

            answer

        )

        add_message(

            user_text,

            answer

        )

        log_event(

            "bot_answer",

            message=user_text,

            message_kind="photo_album",

            has_image=True,

            image_count=photo_count,

            answer=answer,

            relationship=safe_relationship_snapshot(

                relationship

            ),

            iskorka_state=iskorka_state

        )

        await answer_in_parts(

            message,

            answer

        )

    except Exception as e:

        print(

            "\n===== ALBUM ERROR ====="

        )

        print(

            repr(e)

        )

        log_event(

            "error",

            message=user_text,

            error=repr(e)

        )

        await message.answer(

            "Хм... кажется, я немного задумалась."

        )


@dp.message()

async def all_messages(

    message: Message

):





    sticker = message.sticker

    photo = message.photo

    image_bytes = None

    image_mime_type = None

    message_kind = "text"

    if message.text:

        user_text = message.text

    elif sticker:

        user_text = build_sticker_message(

            sticker

        )

        image_bytes, image_mime_type = await download_static_sticker(

            sticker

        )

        message_kind = "sticker"

    elif photo:

        user_text = build_photo_message(

            message

        )

        image_bytes, image_mime_type = await download_photo(

            message

        )

        message_kind = "photo"

        if message.media_group_id:

            media_group_key = (

                message.chat.id,

                message.media_group_id

            )

            album = MEDIA_GROUPS.setdefault(

                media_group_key,

                {

                    "message": message,

                    "images": [],

                    "captions": [],

                    "task": None

                }

            )

            album["images"].append(

                (

                    image_bytes,

                    image_mime_type

                )

            )

            if message.caption:

                album["captions"].append(

                    message.caption

                )

            if album["task"] is None:

                album["task"] = asyncio.create_task(

                    process_photo_media_group(

                        media_group_key

                    )

                )

            return

    else:

        user_text = None





    if not user_text:

        return







    user_id = message.from_user.id

    set_current_bot_user(

        user_id

    )





    save_user_id(

        user_id

    )



    if user_text.strip().lower().startswith("/start"):

        get_relationship()

        get_memory_context()

        log_event(

            "start_command",

            message=user_text,

            relationship=safe_relationship_snapshot(

                get_relationship()

            )

        )

        print(

            f"[START] Пользователь {user_id} добавлен без ответа"

        )

        return


    relationship_command, relationship_level = parse_relationship_status_command(
        user_text
    )

    if relationship_command == "show":
        relationship = get_relationship()

        await message.answer(
            build_relationship_status_text(relationship)
        )

        return

    if relationship_command == "set":
        relationship = set_manual_relationship_level(
            relationship_level,
            note="telegram_command"
        )

        log_event(
            "manual_relationship_level_set",
            message=user_text,
            relationship=safe_relationship_snapshot(
                relationship
            )
        )

        await message.answer(
            "Готово. Теперь фактический статус: "
            f"{get_relationship_level_label(relationship.get('level'))}.\n"
            "Правильная система не отключена: score и correct_level продолжат считаться."
        )

        return

    if relationship_command == "clear":
        relationship = clear_manual_relationship_level()

        log_event(
            "manual_relationship_level_clear",
            message=user_text,
            relationship=safe_relationship_snapshot(
                relationship
            )
        )

        await message.answer(
            "Готово. Статус возвращён к правильной системе.\n"
            "Теперь фактический статус: "
            f"{get_relationship_level_label(relationship.get('level'))}."
        )

        return





    print("\n========================")

    print(

        f"Пользователь ID: {user_id}"

    )



    print(

        f"Сообщение: {user_text}"

    )



    print("========================")



    relationship_before = get_relationship()

    log_event(

        "incoming_message",

        message=user_text,

        message_kind=message_kind,

        has_image=bool(image_bytes),

        sticker_is_visual=bool(image_bytes),

        relationship_before=safe_relationship_snapshot(

            relationship_before

        )

    )







    try:





        # -------------------------

        # MEMORY

        # -------------------------





        analyze_memory(

            user_text

        )





        print(

            "[MEMORY] OK"

        )







        # -------------------------

        # RELATIONSHIP

        # -------------------------





        event = analyze_relationship_event(

            user_text

        )





        print(

            "[RELATIONSHIP EVENT]",

            event

        )







        relationship = update_relationship(

            event

        )

        iskorka_state = update_state_from_event(

            event,

            relationship

        )



        log_event(

            "relationship_update",

            relationship_event=event,

            relationship_before=safe_relationship_snapshot(

                relationship_before

            ),

            relationship_after=safe_relationship_snapshot(

                relationship

            ),

            iskorka_state=iskorka_state

        )





        print(

            "[RELATIONSHIP]",

            relationship

        )







        # -------------------------

        # AI CONTEXT

        # -------------------------





        memory_context = build_memory_context(

            user_text

        )





        history = get_history_text()







        if image_bytes:

            answer = ask_ai_with_image(

                user_text,

                image_bytes,

                image_mime_type,

                history,

                memory_context

            )

        else:

            answer = ask_ai(

                user_text,

                history,

                memory_context

            )







        print(

            "\nОтвет ИИ:"

        )



        print(

            answer

        )







        add_message(

            user_text,

            answer

        )



        log_event(

            "bot_answer",

            message=user_text,

            message_kind=message_kind,

            has_image=bool(image_bytes),

            sticker_is_visual=bool(image_bytes),

            answer=answer,

            relationship=safe_relationship_snapshot(

                relationship

            ),

            iskorka_state=iskorka_state

        )





        await answer_in_parts(

            message,

            answer

        )







    except Exception as e:





        print(

            "\n===== ERROR ====="

        )



        print(

            repr(e)

        )



        log_event(

            "error",

            message=user_text,

            error=repr(e)

        )





        await message.answer(

            "Хм... кажется, я немного задумалась."

        )











# =====================================================

# AUTONOMOUS MESSAGES

# =====================================================





def can_send_autonomous_message(

    relationship

):





    level = relationship.get(

        "level",

        "stranger"

    )





    if level == "stranger":



        return False







    last = relationship.get(

        "last_interaction"

    )





    if last:





        try:





            last_time = datetime.fromisoformat(

                last

            )





            if datetime.now() - last_time < timedelta(

                minutes=30

            ):



                return False





        except:



            pass









    state = load_state()

    last_autonomous = state.get(

        "last_autonomous_message_at"

    )



    if last_autonomous:



        try:



            last_autonomous_time = datetime.fromisoformat(

                last_autonomous

            )



            if datetime.now() - last_autonomous_time < timedelta(

                hours=AUTONOMOUS_MESSAGE_COOLDOWN_HOURS

            ):



                return False



        except:



            pass



    if relationship.get(

        "mood",

        50

    ) < 30:



        return False







    return True













def get_autonomous_chance(

    relationship

):





    levels = {





        "stranger": 0,





        "acquaintance": 5,





        "friend": 25,





        "close_friend": 50,





        "partner": 70



    }







    chance = levels.get(

        relationship.get(

            "level",

            "stranger"

        ),

        0

    )







    last = relationship.get(

        "last_interaction"

    )







    if last:





        try:





            last_time = datetime.fromisoformat(

                last

            )





            days = (

                datetime.now()

                -

                last_time

            ).days







            if days >= 1:



                chance += 10







        except:



            pass









    return min(

        chance,

        90

    )













async def twilight_random_messages():





    await asyncio.sleep(

        300

    )







    while True:





        try:





            user_ids = get_saved_user_ids()







            checked_user_ids = set()

            for user_id in user_ids:

                user_key = str(user_id)

                if user_key in checked_user_ids:

                    continue

                checked_user_ids.add(user_key)



                set_current_bot_user(

                    user_id

                )





                relationship = get_relationship()







                if can_send_autonomous_message(

                    relationship

                ):







                    chance = get_autonomous_chance(

                        relationship

                    )





                    roll = random.randint(

                        1,

                        100

                    )







                    print(

                        f"[AUTO] шанс {chance}% | {roll}"

                    )



                    log_event(

                        "autonomous_check",

                        chance=chance,

                        roll=roll,

                        relationship=safe_relationship_snapshot(

                            relationship

                        )

                    )







                    if roll <= chance:







                        context = build_memory_context()





                        history = get_history_text()







                        text = ask_gemini_random_message(

                            context,

                            str(relationship),

                            history

                        )







                        if text:







                            await send_message_in_parts(

                                user_id,

                                text

                            )





                            add_message(

                                "[Искорка написала первой]",

                                text

                            )

                            iskorka_state = mark_autonomous_message_sent()



                            log_event(

                                "autonomous_message",

                                text=text,

                                chance=chance,

                                roll=roll,

                                relationship=safe_relationship_snapshot(

                                    relationship

                                ),

                                iskorka_state=iskorka_state

                            )





                            print(

                                "[AUTO] сообщение отправлено"

                            )









            await asyncio.sleep(

                21600

            )







        except Exception as e:





            print(

                "AUTOMESSAGE ERROR:",

                e

            )





            await asyncio.sleep(

                3600

            )













# =====================================================

# START

# =====================================================





async def main():





    print(

        "Бот запускается..."

    )





    me = await bot.get_me()





    print(

        f"Бот подключён: @{me.username}"

    )







    asyncio.create_task(

        twilight_random_messages()

    )







    await dp.start_polling(

        bot

    )













if __name__ == "__main__":





    asyncio.run(

        main()

    )

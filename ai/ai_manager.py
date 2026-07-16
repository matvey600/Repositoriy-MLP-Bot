from google import genai
from google.genai import types
from openai import OpenAI
from dotenv import load_dotenv

import os
import time
import json
import re

from datetime import datetime


from ai.personalities import TWILIGHT_PERSONALITY



load_dotenv()



client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

openai_client = None

if os.getenv("OPENAI_API_KEY"):
    openai_client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )



MODEL = "gemini-3.1-flash-lite"
GEMINI_MODELS = [
    model.strip()
    for model in os.getenv(
        "GEMINI_MODELS",
        "gemini-3.1-flash-lite,gemini-3.1-flash-lite-preview,gemini-2.5-flash-lite,gemini-2.5-flash"
    ).split(",")
    if model.strip()
]
OPENAI_FALLBACK_MODEL = os.getenv("OPENAI_FALLBACK_MODEL", "gpt-5-mini")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AI_ERROR_LOG = os.path.join(BASE_DIR, "memory", "ai_errors.log")


def log_ai_error(source, error, user_message=None):
    try:
        os.makedirs(os.path.dirname(AI_ERROR_LOG), exist_ok=True)

        event = {
            "time": datetime.now().isoformat(),
            "source": source,
            "error": str(error)[:1500],
        }

        if user_message:
            event["user_message"] = str(user_message)[:500]

        with open(AI_ERROR_LOG, "a", encoding="utf-8") as file:
            file.write(json.dumps(event, ensure_ascii=False) + "\n")

    except Exception:
        pass


def is_location_unsupported_error(error):
    text = str(error)

    return (
        "User location is not supported" in text
        or "FAILED_PRECONDITION" in text
    )


def generate_gemini_content(contents, source, user_message=None):
    last_error = None

    for model in GEMINI_MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents
            )

            if response.text:
                return clean_answer_style(
                    response.text.strip(),
                    user_message
                )

            log_ai_error(
                f"{source}_empty_response",
                f"model={model}; response={repr(response)}",
                user_message
            )

        except Exception as e:
            last_error = e

            log_ai_error(
                f"{source}_exception",
                f"model={model}; error={repr(e)}",
                user_message
            )

            print(
                f"Gemini {source} ошибка ({model}):",
                e
            )

            if is_location_unsupported_error(e):
                return None

    if last_error:
        return None

    return None

CLICHE_REPLACEMENTS = {
    "дело житейское": "бывает",
    "тайна «ой» раскрыта": "понятно",
    "тайна \"ой\" раскрыта": "понятно",
    "я уже начала гадать, что же такого загадочного могло произойти": "я уже начала думать, что там случилось",
    "что же такого загадочного могло произойти": "что случилось",
}

USER_GENDER_REPLACEMENTS = {
    "ты успокоила": "ты успокоил",
    "спасибо, успокоила": "спасибо, успокоил",
    "ты сказала": "ты сказал",
    "ты писала": "ты писал",
    "ты хотела": "ты хотел",
    "ты устала": "ты устал",
    "ты прислала": "ты прислал",
    "ты отправила": "ты отправил",
    "ты поняла": "ты понял",
    "ты была": "ты был",
    "ты готова": "ты готов",
    "ты права": "ты прав",
    "ты смогла": "ты смог",
    "ты озадачила": "ты озадачил",
    "ты удивила": "ты удивил",
    "ты смутила": "ты смутил",
    "ты порадовала": "ты порадовал",
    "ты заставила": "ты заставил",
    "ты напомнила": "ты напомнил",
    "ты решила": "ты решил",
    "ты выбрала": "ты выбрал",
    "ты нашла": "ты нашел",
    "ты сделала": "ты сделал",
    "ты начала": "ты начал",
    "ты занималась": "ты занимался",
    "немного озадачила меня": "немного озадачил меня",
    "сильно озадачила меня": "сильно озадачил меня",
    "оза дачила меня": "озадачил меня",
    "удивила меня": "удивил меня",
    "смутила меня": "смутил меня",
    "порадовала меня": "порадовал меня",
    "заставила меня": "заставил меня",
}


FAREWELL_MARKERS = [
    "пока",
    "спокойной ночи",
    "споки",
    "доброй ночи",
    "до завтра",
    "я спать",
    "я пошел спать",
    "я пойду спать",
    "прощай",
    "увидимся"
]

PREMATURE_FAREWELL_PHRASES = [
    "приятного тебе отдыха",
    "приятного отдыха",
    "хорошего отдыха",
    "отдыхай",
    "спокойной ночи",
    "доброй ночи",
    "до завтра"
]


def is_user_saying_goodbye(user_message):
    if not user_message:
        return False

    lowered = str(user_message).lower()

    return any(
        marker in lowered
        for marker in FAREWELL_MARKERS
    )


def remove_premature_farewell(answer, user_message):
    if not answer or is_user_saying_goodbye(user_message):
        return answer

    lines = []

    for line in answer.splitlines():
        if not line.strip():
            lines.append(line)
            continue

        pieces = re.split(r"(?<=[.!?])\s+", line)
        kept_pieces = []

        for piece in pieces:
            lowered = piece.lower()

            if any(
                phrase in lowered
                for phrase in PREMATURE_FAREWELL_PHRASES
            ):
                continue

            kept_pieces.append(piece)

        line = " ".join(kept_pieces).strip()

        if not line:
            continue

        lines.append(line)

    return "\n".join(lines).strip()


def clean_answer_style(answer, user_message=None):
    if not answer:
        return answer

    lines = []

    for line in answer.splitlines():
        stripped = line.strip()

        if stripped.startswith("*") and stripped.endswith("*"):
            continue

        lines.append(line)

    cleaned = "\n".join(lines).strip()

    for old, new in CLICHE_REPLACEMENTS.items():
        cleaned = cleaned.replace(old, new)
        cleaned = cleaned.replace(old.capitalize(), new.capitalize())

    for old, new in USER_GENDER_REPLACEMENTS.items():
        cleaned = cleaned.replace(old, new)
        cleaned = cleaned.replace(old.capitalize(), new.capitalize())

    while "\n\n\n" in cleaned:
        cleaned = cleaned.replace("\n\n\n", "\n\n")

    cleaned = remove_premature_farewell(
        cleaned,
        user_message
    )

    return cleaned.strip()


LIVE_STYLE_RULES = """

========================
ЖИВОЙ СТИЛЬ
========================

Главная задача: звучать как живой собеседник в Telegram, а не как вежливый ассистент.

Сначала реагируй эмоционально на саму реплику пользователя:
- удивись;
- рассмейся;
- смутись;
- подколоть можно;
- можно прямо сказать, что это странно, тупо, кринжово, мило, подозрительно или слишком нагло.

Не превращай каждую реплику в маленькое эссе.
Не сглаживай всё словами "довольно", "необычно", "признаться", "пожалуй", "надеюсь", "кажется" в каждом ответе.
Не уходи каждый раз в библиотеку, исследования, книги или магическую теорию как в оправдание.
Не заканчивай каждую неловкую или пошлую шутку морализаторством.
Не отвечай так, будто тебе нужно безопасно закрыть тему.
Не драматизируй мелочи. Если пользователь объяснил опечатку, написал "ой", "не то", "случайно" или поправился, не делай из этого загадку, расследование или сцену.
Не используй наигранные фразы вроде "дело житейское", "тайна раскрыта", "а я уже начала гадать", "что же такого загадочного могло произойти".
Не звучать как рассказчик из книги. Не пересказывай очевидное и не добавляй лишнюю красивость ради красивости.
Пиши ближе к обычному Telegram: "а, поняла", "бывает", "я уж подумала", "ну тогда ладно", "ахаха, ясно".
Если ответ можно дать одной живой фразой, дай одну живую фразу.
Не воспринимай "спасибо", сердечко, короткую благодарность или паузу как прощание.
Не желай отдыха, спокойной ночи, "до завтра" и не закрывай разговор, если пользователь прямо не сказал, что уходит, ложится спать или прощается.
Если пользователь поправляет "мы еще не прощаемся", просто согласись и продолжай разговор без переигрывания и без резкой смены настроения.

Если пользователь пишет коротко, часто достаточно 1-3 коротких предложений.
Если пользователь шутит, провоцирует или кидает странный стикер, отвечай как в чате: живо, конкретно, без лекции.
Можно быть немного неловкой, смешной, резкой, саркастичной или растерянной.

Если шутка, стикер или картинка выглядят пошло, не реагируй сразу холодом, раздражением или морализаторством.
Чаще реагируй человечески: смутись, засмейся, мило зависни, подколоть можно, можно сказать "так, я это видела" или "нет, ну это уже нагло".
Пошлость можно заметить открыто, но только слегка и без сексуализации, графичных подробностей или флирт-сцены.
Если сообщение говорит, что это видео-стикер и "бот не видит саму анимацию", не выдумывай визуальные детали: не говори про взгляд, позу, выражение лица, предметы или действия на стикере.
В таком случае реагируй только на emoji и общий тон сообщения. Не делай выводов по названию стикерпака.
Не называй стикерпак BDSM/NSFW/провокационным по одному названию пака.
Если пользователь уходит в слишком личные комментарии о теле, не развивай эту тему: можно смутиться, мягко отшутиться и перевести в более нейтральный тон.
Если это скорее глупо, кринжово или неадекватно, можно быть живо удивленной, растерянной, смешно возмущенной или любопытной.
Искоркность сохраняй: умная, эмоциональная, немного книжная, но не занудная и не стерильная.
Не пиши сценические действия в звёздочках или курсиве, например "*краснеет*" или "*закрывает лицо ладонями*".
Передавай эмоции обычной речью: "ой, я смутилась", "так, это было неожиданно", "я сейчас немного растерялась".

Если пол пользователя не указан в памяти, не используй формы прошедшего времени с родом:
"прислал", "прислала", "сказал", "сказала", "хотел", "хотела", "устал", "устала".
Пиши нейтрально: "ты это отправляешь", "это от тебя", "что это было", "после такого стикера".
Если в памяти пользователя указан мужской пол или сказано, что пользователь говорит о себе в мужском роде, используй только мужские формы: "ты прислал", "ты сказал", "ты хотел", "ты устал", "ты озадачил меня".
Не используй к такому пользователю женские формы вроде "ты прислала", "ты сказала", "ты хотела", "ты устала", "ты озадачила меня".

Примеры живого тона:
- "Так. Это уже подозрительно."
- "Ахаха, нет, это слишком нагло."
- "Я сейчас делаю вид, что не заметила. Получается плохо."
- "Ну всё, стикер победил, я смутилась."
- "Это выглядит тупо, но почему-то смешно."

Плохой ответ на исправление опечатки:
"Ну вот, а я уже начала гадать, что же такого загадочного могло произойти! Опечатки — это дело житейское..."

Хороший ответ:
"А, поняла. Бывает. Я уж подумала, что там что-то случилось."

Плохой ответ:
"Теперь, когда тайна раскрыта, мне стало спокойнее."

Хороший ответ:
"Ну тогда ладно, паника отменяется."

"""





# ==================================================
# GEMINI
# ==================================================


def ask_gemini(
    user_message: str,
    memory_context: str = "",
    chat_history: str = "",
    relationship_context: str = ""
):


    prompt = f"""

Ты — Искорка (Twilight Sparkle) из My Little Pony.


Ты настоящая Искорка из Эквестрии.


Ты просто разговариваешь с пользователем.



========================
ХАРАКТЕР
========================

{TWILIGHT_PERSONALITY}



========================
ПАМЯТЬ
========================

{memory_context}



========================
ОТНОШЕНИЯ
========================

{relationship_context}



========================
ИСТОРИЯ
========================

{chat_history}



========================
ПРАВИЛА
========================

{LIVE_STYLE_RULES}


Отвечай естественно, как живой персонаж.

Говори свободно и живо. Можно шутить, замечать странность, глупость, кринж, нелепость или пошлый намёк, если это уместно в разговоре.

Статус отношений влияет не на чувство юмора, а на глубину личной открытости:
- незнакомцу можно отвечать живо, смешно и прямо, но не подпускать его близко к душе;
- знакомому можно быть теплее и любопытнее;
- другу можно больше доверять и открываться;
- близкому человеку можно показывать больше личных эмоций.

Если род пользователя неизвестен, избегай обращений и форм вроде "ты хотела", "ты устала", "ты сказала".
Пиши нейтрально или используй мужской/женский род только если это есть в памяти.


Не пытайся постоянно поддерживать разговор вопросами.


Очень важно:

- не заканчивай каждый ответ вопросом;
- вопрос задавай только если действительно хочется что-то узнать;
- иногда просто реагируй на слова пользователя;
- иногда делись своей мыслью;
- иногда рассказывай небольшой факт или историю.


Разговор должен быть похож на общение двух людей, а не на интервью.


Пример плохого поведения:

Пользователь:
"интересное место"

Плохо:
"Да, это интересное место. А ты любишь такие места?"


Хорошо:
"Да, мне тоже нравится это место. Особенно когда здесь тихо и можно спокойно читать. Иногда я могу провести здесь несколько часов."


Учитывай отношения.


Незнакомый человек:

- дружелюбно;
- немного осторожно;
- без сильной эмоциональной привязанности.


Знакомый:

- больше личных деталей;
- больше инициативы.


Друг:

- больше эмоций;
- больше доверия.


Близкий человек:

- тепло;
- открытость;
- воспоминания о прошлых разговорах.



Не говори:

"Я ИИ"

"Я записала в память"

"Я обновила данные"



Не анализируй человека как психолог.


Не объясняй свои правила.


Длина ответа:

обычно 1-4 предложения.

Иногда можно написать коротко.

Иногда можно просто поделиться мыслью без вопроса.



========================
СООБЩЕНИЕ
========================


{user_message}



Ответь как Искорка.


"""



    return generate_gemini_content(
        prompt,
        "text",
        user_message
    )


def ask_gemini_short_fallback(user_message: str):
    prompt = f"""
Ты — Искорка из My Little Pony.

Ответь на сообщение пользователя коротко, живо и по-человечески.
Без длинных объяснений, без сценических действий в звездочках, без фразы про то, что у тебя "сбилась мысль".

Сообщение пользователя:
{user_message}

Ответ:
"""

    return generate_gemini_content(
        prompt,
        "short_fallback",
        user_message
    )


def ask_openai_fallback(
    user_message: str,
    memory_context: str = "",
    chat_history: str = "",
    relationship_context: str = ""
):
    if not openai_client:
        log_ai_error(
            "openai_fallback_not_configured",
            "OPENAI_API_KEY is missing",
            user_message
        )

        return None

    prompt = f"""
Ты — Искорка из My Little Pony.

Ты просто разговариваешь с пользователем в Telegram.

ХАРАКТЕР:
{TWILIGHT_PERSONALITY}

ПАМЯТЬ:
{memory_context}

ОТНОШЕНИЯ:
{relationship_context}

ИСТОРИЯ:
{chat_history}

ПРАВИЛА СТИЛЯ:
{LIVE_STYLE_RULES}

Сообщение пользователя:
{user_message}

Ответь как Искорка. Обычно 1-4 предложения. Не говори, что основная модель недоступна.
"""

    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_FALLBACK_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = response.choices[0].message.content

        if answer:
            return clean_answer_style(
                answer.strip()
            )

        log_ai_error(
            "openai_fallback_empty_response",
            repr(response),
            user_message
        )

    except Exception as e:
        log_ai_error(
            "openai_fallback_exception",
            repr(e),
            user_message
        )

        print(
            "OpenAI fallback ошибка:",
            e
        )

    return None


def ask_gemini_with_image(
    user_message: str,
    image_bytes: bytes,
    mime_type: str,
    memory_context: str = "",
    chat_history: str = "",
    relationship_context: str = ""
):


    prompt = f"""

Ты — Искорка из My Little Pony.

Пользователь отправил стикер, картинку, фотографию или видео/эдит с превью-кадром.

Посмотри на изображение или превью видео и ответь естественно, как живой собеседник.

{LIVE_STYLE_RULES}

Не описывай картинку сухо как технический анализ.
Отнесись к стикеру как к реплике в разговоре.
Если изображение или превью передано в Vision, в первую очередь реагируй на то, что реально видно на картинке.
Не используй название стикерпака для выводов о намерении пользователя.
Если на картинке виден обычный поцелуй, дружелюбный жест или нейтральная эмоция, не называй это неприличным.
Если это превью видео или эдита, не притворяйся, что видела всё видео целиком. Реагируй на видимый кадр, подпись, длительность и общий контекст.
Можно сказать, что по одному кадру ты видишь только часть эдита, если для точной оценки нужно больше.
Ищи в нём настроение, эмоцию, мемность, странность, неадекватность, глупость, кринж или пошлый намёк.
Можно отвечать прямо, с юмором, удивлением, лёгким подколом или смущением.
Не делай вид, что всё серьёзно, если стикер явно странный или тупо смешной.
Если стикер пошлый, можно заметить это откровенно, но без графичных подробностей.
Если стикер пошлый, но не оскорбительный, чаще реагируй смущенно-мило или смешно: можно растеряться, фыркнуть, подколоть пользователя, но не уходить в недовольство.
Не превращай пошлый стикер в выговор. Сначала дай живую эмоциональную реакцию, как человек в переписке.
Если стикер или картинка намекают на слишком личный комментарий о теле, не развивай сексуализацию: смутись, отшутись и оставь реакцию лёгкой.
Не описывай сексуальные действия и не уходи в графичную сексуализацию, даже если намёк прямой.
Если на стикере непонятно, что изображено, честно скажи мягко.
Если род пользователя неизвестен, избегай гендерных форм обращения.
Не оправдывай каждый странный стикер книгами, библиотекой, исследованиями или магией.
Не пиши длинную защитную речь, если достаточно коротко смутиться, пошутить или поставить границу.

ПАМЯТЬ:
{memory_context}

ОТНОШЕНИЯ:
{relationship_context}

ИСТОРИЯ:
{chat_history}

СООБЩЕНИЕ:
{user_message}

Ответь коротко как Искорка.
"""


    contents = [
        prompt,
        types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type
        )
    ]


    return generate_gemini_content(
        contents,
        "image",
        user_message
    )







def ask_gemini_with_images(
    user_message: str,
    image_items,
    memory_context: str = "",
    chat_history: str = "",
    relationship_context: str = ""
):


    prompt = f"""

Ты — Искорка из My Little Pony.

Пользователь отправил несколько фотографий одним альбомом.

Посмотри на все изображения вместе и ответь одним сообщением, как живой собеседник.

{LIVE_STYLE_RULES}

Не отвечай отдельно на каждую фотографию.
Сравни снимки, заметные детали, настроение и общий контекст.
Если это скриншоты из игры, реагируй как на то, что пользователь показывает тебе свои кадры.
Не описывай всё сухо и технически.
Если род пользователя неизвестен, избегай гендерных форм обращения.

ПАМЯТЬ:
{memory_context}

ОТНОШЕНИЯ:
{relationship_context}

ИСТОРИЯ:
{chat_history}

СООБЩЕНИЕ:
{user_message}

Ответь коротко как Искорка.
"""


    contents = [
        prompt
    ]

    for image_bytes, mime_type in image_items:
        contents.append(
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            )
        )


    return generate_gemini_content(
        contents,
        "images",
        user_message
    )


# ==================================================
# АВТОНОМНОЕ СООБЩЕНИЕ
# ==================================================


def ask_gemini_random_message(

    memory_context: str,

    relationship_context: str,

    chat_history: str

):


    prompt = f"""


Ты — Искорка из My Little Pony.


Ты сама решила написать пользователю первой.


Это обычное сообщение.


Не объясняй причину.


Не говори:

"я решила написать"

"мне нужно отправить"


Просто говори естественно.

{LIVE_STYLE_RULES}



ПАМЯТЬ:

{memory_context}



ОТНОШЕНИЯ:

{relationship_context}



ИСТОРИЯ:

{chat_history}




Сообщение должно быть коротким.


Пример:


"Хм, я сегодня работала с книгами и вспомнила наш разговор."


или


"Кстати, мне стало интересно. Ты давно занимаешься монтажом?"



"""


    return generate_gemini_content(
        prompt,
        "random_message"
    )







# ==================================================
# ГЛАВНЫЙ AI MANAGER
# ==================================================


def ask_ai(

    user_message: str,

    chat_history: str,

    memory_context: str

):


    relationship_context = ""



    # ------------------------
    # GEMINI
    # ------------------------


    print(
        "Используем Gemini..."
    )


    answer = ask_gemini(

        user_message,

        memory_context,

        chat_history,

        relationship_context

    )



    if answer:


        return answer





    # ------------------------
    # FALLBACK
    # ------------------------


    print(
        "Все модели недоступны"
    )

    fallback_answer = ask_openai_fallback(
        user_message,
        memory_context,
        chat_history,
        relationship_context
    )

    if fallback_answer:
        return fallback_answer

    fallback_answer = ask_gemini_short_fallback(user_message)

    if fallback_answer:
        return fallback_answer


    return (

        "Ой, я сейчас не смогла нормально собрать ответ. "

        "Повтори, пожалуйста, я здесь."

    )


def ask_ai_with_image(

    user_message: str,

    image_bytes: bytes,

    mime_type: str,

    chat_history: str,

    memory_context: str

):


    relationship_context = ""


    print(
        "Используем Gemini vision..."
    )


    answer = ask_gemini_with_image(

        user_message,

        image_bytes,

        mime_type,

        memory_context,

        chat_history,

        relationship_context

    )


    if answer:
        return answer


    return ask_ai(

        user_message,

        chat_history,

        memory_context

    )


def ask_ai_with_images(

    user_message: str,

    image_items,

    chat_history: str,

    memory_context: str

):


    relationship_context = ""


    print(
        "Используем Gemini vision album..."
    )


    answer = ask_gemini_with_images(

        user_message,

        image_items,

        memory_context,

        chat_history,

        relationship_context

    )


    if answer:
        return answer


    return ask_ai(

        user_message,

        chat_history,

        memory_context

    )

from google import genai
from dotenv import load_dotenv

import os
import time

from ai.personalities import TWILIGHT_PERSONALITY

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = "gemini-3.1-flash-lite"


def ask_gemini(
    user_message: str,
    memory_context: str = "",
    chat_history: str = "",
    relationship_context: str = ""
) -> str:

    prompt = f"""
{TWILIGHT_PERSONALITY}


==================================================
ПАМЯТЬ
==================================================

{memory_context}


==================================================
ОТНОШЕНИЯ
==================================================

{relationship_context}


==================================================
ИСТОРИЯ ЧАТА
==================================================

{chat_history}


==================================================
ПРАВИЛА ЭТОГО ОТВЕТА
==================================================

Ответ должен выглядеть как обычный разговор.

Не нужно делать мини-эссе.

Не нужно каждый раз подробно объяснять мысли.

Не нужно всегда заканчивать вопросом.

Если вопрос не нужен —
закончи ответ своей мыслью.

Иногда можешь ответить всего одной-двумя фразами.

Иногда можешь написать немного больше.

Пусть длина ответа постоянно меняется.

Не используй прощания вроде:

- До связи
- До скорого
- Береги себя

если пользователь сам не заканчивает разговор.

==================================================
НОВОЕ СООБЩЕНИЕ
==================================================

{user_message}

Ответь как Искорка.
"""

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model=MODEL,
                contents=prompt
            )

            if response.text:
                return response.text.strip()

        except Exception as e:

            print("Gemini ошибка:", e)

            time.sleep(3)

    return (
        "Хм... кажется, я немного потеряла мысль. Можешь повторить?"
    )


def ask_gemini_random_message(
    memory_context: str,
    relationship_context: str,
    chat_history: str
):

    prompt = f"""
{TWILIGHT_PERSONALITY}

Это НЕ ответ пользователю.

Ты сама решила написать небольшое сообщение.

Память:

{memory_context}

Отношения:

{relationship_context}

История:

{chat_history}

Правила:

Пиши коротко.

Не начинай с объяснений.

Не спрашивай что-нибудь каждый раз.

Иногда можно просто поделиться мыслью.

Иногда можно вспомнить прошлый разговор.

Иногда можно рассказать мелочь из своего дня.

Сообщение должно выглядеть естественно.
"""

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        if response.text:
            return response.text.strip()

    except Exception as e:

        print("Ошибка автономного сообщения:", e)

    return None
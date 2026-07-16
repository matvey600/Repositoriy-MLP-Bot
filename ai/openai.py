from openai import OpenAI
from dotenv import load_dotenv

import os

from ai.personalities import TWILIGHT_PERSONALITY


load_dotenv()


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)



def ask_openai(
    user_message: str,
    memory_context: str = "",
    chat_history: str = ""
) -> str:


    prompt = f"""
{TWILIGHT_PERSONALITY}


========================
ПАМЯТЬ О ПОЛЬЗОВАТЕЛЕ
========================

{memory_context}



========================
ИСТОРИЯ РАЗГОВОРА
========================

{chat_history}



========================
НОВОЕ СООБЩЕНИЕ
========================

{user_message}



Ответь как Искорка.

Главное:

- сохраняй характер Искорки;
- не представляйся каждый раз;
- не упоминай, что ты программа;
- не придумывай воспоминания;
- не ускоряй развитие отношений;
- отвечай естественно, как живой собеседник.
"""


    response = client.chat.completions.create(
        model="gpt-5",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )


    return response.choices[0].message.content
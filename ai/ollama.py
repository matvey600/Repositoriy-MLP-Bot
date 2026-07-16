import requests


OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL = "qwen2.5:7b"


def ask_ollama(
    user_message: str,
    memory_context: str = ""
) -> str:

    prompt = f"""
Ты — живой персонаж из My Little Pony.

Общайся с пользователем дружелюбно, естественно и эмоционально.

Учитывай память:

{memory_context}


Сообщение пользователя:

{user_message}


Ответь как настоящий персонаж.
Не говори, что ты искусственный интеллект.
"""


    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )


    response.raise_for_status()


    data = response.json()


    return data["response"]
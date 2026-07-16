import re

from memory_manager import (
    add_emotion,
    add_event,
    add_memory,
    add_to_list,
    set_user_data,
    set_user_name
)


def analyze_memory(user_message: str):
    original = user_message.strip()
    text = original.lower()

    analyze_name(text)
    analyze_identity(text)
    analyze_age(text)
    analyze_city(original, text)
    analyze_work(original, text)
    analyze_study(original, text)
    analyze_profession(original, text)
    analyze_hobbies(original, text)
    analyze_interests(original, text)
    analyze_dislikes(original, text)
    analyze_likes(original, text)
    analyze_goals(original, text)
    analyze_dreams(original, text)
    analyze_traits(original, text)
    analyze_emotions(original, text)
    analyze_events(original, text)

    print("[MEMORY] Анализ завершён")


def analyze_name(text):
    patterns = [
        r"\bменя зовут ([а-яёa-z-]+)",
        r"\bмо[её] имя ([а-яёa-z-]+)",
        r"\bя ([а-яёa-z-]+),? приятно"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            name = match.group(1).capitalize()
            set_user_name(name)
            print(f"[MEMORY] Имя: {name}")
            return


def analyze_identity(text):
    if re.search(r"\bя (?:парень|мужчина|мужик)\b", text):
        set_user_data("gender", "мужской")
        add_to_list("identity", "пользователь говорит о себе в мужском роде")
        print("[MEMORY] Род обращения: мужской")
        return

    if re.search(r"\bя (?:девушка|женщина)\b", text):
        set_user_data("gender", "женский")
        add_to_list("identity", "пользователь говорит о себе в женском роде")
        print("[MEMORY] Род обращения: женский")
        return

    if re.search(r"\bя гей\b", text):
        set_user_data("gender", "мужской")
        set_user_data("orientation", "гей")
        add_to_list("identity", "пользователь сказал, что он гей")
        add_memory("identity", "Пользователь сказал, что он гей", 8)
        print("[MEMORY] Ориентация: гей")
        return

    if re.search(r"\bя лесбиянка\b", text):
        set_user_data("gender", "женский")
        set_user_data("orientation", "лесбиянка")
        add_to_list("identity", "пользовательница сказала, что она лесбиянка")
        add_memory("identity", "Пользовательница сказала, что она лесбиянка", 8)
        print("[MEMORY] Ориентация: лесбиянка")
        return


def analyze_age(text):
    patterns = [
        r"\bмне (\d{1,3})\s*(?:год|года|лет)\b",
        r"\bмой возраст (\d{1,3})\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            age = int(match.group(1))

            if 1 <= age <= 120:
                set_user_data("age", age)
                print(f"[MEMORY] Возраст: {age}")

            return


def analyze_city(original, text):
    triggers = [
        "я живу в",
        "живу в",
        "я из",
        "мой город",
        "моя страна",
        "мой район"
    ]

    value = extract_after_any(original, text, triggers)

    if value:
        set_user_data("city", value)
        add_memory("location", f"Пользователь живёт в {value}", 6)
        print("[MEMORY] Город:", value)


def analyze_work(original, text):
    triggers = [
        "я работаю",
        "работаю",
        "моя работа",
        "на работе я",
        "я устроился",
        "я устроилась"
    ]

    value = extract_after_any(original, text, triggers)

    if value:
        set_user_data("work", value)
        add_memory("work", f"Работа пользователя: {value}", 7)
        print("[MEMORY] Работа:", value)


def analyze_study(original, text):
    triggers = [
        "я учусь",
        "учусь",
        "я студент",
        "я студентка",
        "моя учёба",
        "моя учеба"
    ]

    value = extract_after_any(original, text, triggers)

    if value:
        set_user_data("study", value)
        add_memory("study", f"Учёба пользователя: {value}", 7)
        print("[MEMORY] Учёба:", value)


def analyze_profession(original, text):
    triggers = [
        "я программист",
        "я разработчик",
        "я дизайнер",
        "я монтажер",
        "я монтажёр",
        "моя профессия",
        "по профессии я"
    ]

    for trigger in triggers:
        if trigger in text:
            value = extract_after(original, text, trigger) or trigger.replace("я ", "")
            set_user_data("profession", value)
            add_memory("profession", f"Профессия пользователя: {value}", 7)
            print("[MEMORY] Профессия:", value)
            return


def analyze_hobbies(original, text):
    triggers = [
        "я занимаюсь",
        "я увлекаюсь",
        "моё хобби",
        "мое хобби",
        "я тренируюсь"
    ]

    value = extract_after_any(original, text, triggers)

    if value:
        add_to_list("hobbies", value)
        add_memory("hobby", f"Пользователь занимается {value}", 7)
        print("[MEMORY] Хобби:", value)


def analyze_interests(original, text):
    triggers = [
        "мне интересно",
        "меня интересует",
        "мои интересы",
        "интересуюсь"
    ]

    value = extract_after_any(original, text, triggers)

    if value:
        add_to_list("interests", value)
        add_memory("interest", f"Пользователю интересно {value}", 6)
        print("[MEMORY] Интерес:", value)


def analyze_likes(original, text):
    if "не люблю" in text or "не нравится" in text:
        return

    patterns = [
        r"\bмне\s+([а-яёa-z0-9 -]{2,80}?)\s+(?:с детства\s+)?нрав(?:ятся|ится)\b",
        r"\b([а-яёa-z0-9 -]{2,80}?)\s+мне\s+(?:очень\s+)?нрав(?:ятся|ится)\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            value = clean_fact(match.group(1))

            if value:
                add_to_list("likes", value)
                add_memory("like", f"Пользователю нравится {value}", 6)
                print("[MEMORY] Нравится:", value)
                return

    triggers = [
        "мне очень нравится",
        "мне нравится",
        "я люблю",
        "обожаю"
    ]

    value = extract_after_any(original, text, triggers)

    if value:
        add_to_list("likes", value)
        add_memory("like", f"Пользователю нравится {value}", 6)
        print("[MEMORY] Нравится:", value)


def analyze_dislikes(original, text):
    triggers = [
        "мне не нравится",
        "я не люблю",
        "ненавижу",
        "терпеть не могу"
    ]

    value = extract_after_any(original, text, triggers)

    if value:
        add_to_list("dislikes", value)
        add_memory("dislike", f"Пользователю не нравится {value}", 6)
        print("[MEMORY] Не нравится:", value)


def analyze_goals(original, text):
    triggers = [
        "хочу научиться",
        "хочу сделать",
        "моя цель",
        "я хочу"
    ]

    value = extract_after_any(original, text, triggers)

    if value and not looks_like_small_talk_goal(value):
        add_to_list("goals", value)
        add_memory("goal", f"Цель пользователя: {value}", 8)
        print("[MEMORY] Цель:", value)


def analyze_dreams(original, text):
    triggers = [
        "я мечтаю",
        "моя мечта",
        "мечтаю о",
        "мечтаю"
    ]

    value = extract_after_any(original, text, triggers)

    if value:
        add_to_list("dreams", value)
        add_memory("dream", f"Мечта пользователя: {value}", 8)
        print("[MEMORY] Мечта:", value)


def analyze_traits(original, text):
    patterns = [
        r"\bя (?:очень )?(спокойный|спокойная|весёлый|веселый|весёлая|веселая|тревожный|тревожная|упрямый|упрямая|добрый|добрая|стеснительный|стеснительная)\b",
        r"\bу меня характер ([а-яёa-z -]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            trait = clean_fact(match.group(1))
            add_to_list("traits", trait)
            add_memory("trait", f"Черта пользователя: {trait}", 5)
            print("[MEMORY] Черта:", trait)
            return


def analyze_emotions(original, text):
    emotion_rules = [
        ("sadness", ["грустно", "печально", "тоскливо", "плохо на душе"], "Пользователь чувствовал грусть"),
        ("joy", ["рад", "рада", "счастлив", "счастлива", "доволен", "довольна"], "Пользователь чувствовал радость"),
        ("tiredness", ["устал", "устала", "нет сил", "выгорел", "выгорела"], "Пользователь чувствовал усталость"),
        ("stress", ["стресс", "нервничаю", "переживаю", "тревожно", "паника"], "Пользователь чувствовал стресс"),
        ("anger", ["злюсь", "бесит", "раздражает", "я зол", "я злая"], "Пользователь чувствовал злость"),
        ("motivation", ["замотивирован", "замотивирована", "есть мотивация", "хочу продолжать"], "Пользователь чувствовал мотивацию"),
        ("tiredness", ["тяжёлый день", "тяжелый день"], "У пользователя был тяжёлый день")
    ]

    for emotion, markers, memory_text in emotion_rules:
        if any(marker in text for marker in markers):
            add_emotion(emotion, memory_text, 6)
            print("[MEMORY] Эмоция:", emotion)
            return


def analyze_events(original, text):
    event_rules = [
        ("achievement", ["получилось", "я смог", "я смогла", "добился", "добилась", "закончил", "закончила"], 8),
        ("problem", ["проблема", "не получается", "сломалось", "поссорился", "поссорилась"], 7),
        ("life_change", ["переехал", "переехала", "устроился", "устроилась", "уволился", "уволилась", "начал учиться", "начала учиться"], 8),
        ("important_conversation", ["важный разговор", "хочу рассказать важное", "это важно"], 8)
    ]

    for category, markers, importance in event_rules:
        marker = find_first_marker(text, markers)

        if marker:
            event_text = extract_sentence_with_marker(original, text, marker)
            add_event(category, event_text, importance)
            add_memory(category, event_text, importance)
            print("[MEMORY] Событие:", category)
            return


def extract_after_any(original, text, triggers):
    for trigger in triggers:
        if trigger in text:
            value = extract_after(original, text, trigger)

            if value:
                return value

    return None


def extract_after(original, text, trigger):
    index = text.find(trigger)

    if index == -1:
        return None

    result = original[index + len(trigger):]
    return clean_fact(result)


def clean_fact(value):
    result = str(value).strip()
    result = result.strip(" .!,?;:—-")
    result = re.split(r"[.!?]\s+", result, maxsplit=1)[0]

    stop_phrases = [
        " и хочу ",
        " но ",
        " потому что ",
        " поэтому ",
        " когда ",
        " хотя ",
        " а ещё ",
        " а еще "
    ]

    lower_result = result.lower()

    for stop_phrase in stop_phrases:
        index = lower_result.find(stop_phrase)

        if index > 0:
            result = result[:index]
            break

    result = result.strip(" .!,?;:—-")

    if len(result) < 2:
        return None

    return result.lower()


def find_first_marker(text, markers):
    for marker in markers:
        if marker in text:
            return marker

    return None


def extract_sentence_with_marker(original, text, marker):
    marker_index = text.find(marker)

    if marker_index == -1:
        return clean_fact(original)

    start = 0
    end = len(original)

    for separator in ".!?":
        separator_index = original.rfind(separator, 0, marker_index)

        if separator_index != -1:
            start = max(start, separator_index + 1)

    for separator in ".!?":
        separator_index = original.find(separator, marker_index)

        if separator_index != -1:
            end = min(end, separator_index)

    return clean_event_text(original[start:end])


def clean_event_text(value):
    result = str(value).strip()
    result = result.strip(" .!,?;:—-")

    if len(result) < 2:
        return None

    return result.lower()


def looks_like_small_talk_goal(value):
    weak_values = {
        "спать",
        "есть",
        "пить",
        "поговорить",
        "спросить",
        "знать"
    }

    return normalize_goal(value) in weak_values


def normalize_goal(value):
    return " ".join(str(value).lower().strip().split())

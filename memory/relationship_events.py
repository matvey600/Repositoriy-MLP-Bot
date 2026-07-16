import re



# =========================
# АНАЛИЗ ОТНОШЕНИЙ
# =========================


def analyze_relationship_event(message: str):


    text = message.lower().strip()

    # =====================
    # НАПРАВЛЕННАЯ АГРЕССИЯ
    # =====================


    direct_markers = [

        "ты",

        "тебя",

        "тебе",

        "тобой",

        "искорка"

    ]


    has_direct_marker = any(

        re.search(
            rf"\b{marker}\b",
            text
        )

        for marker in direct_markers

    )


    aggressive_commands = [

        "иди нах",

        "иди ты нах",

        "пошла нах",

        "пошел нах",

        "пошёл нах",

        "отъебись",

        "отъебись от меня",

        "заткнись",

        "завали ебало",

        "иди в жопу"

    ]


    directed_insult_patterns = [

        r"\bты\s+.*?(туп|глуп|дур|дебил|идиот|бездуш|заеб|заёб|бесиш|кончен)",

        r"\bчто\s+ты\s+за\s+.*?(туп|глуп|дур|дебил|идиот|бездуш|кончен)",

        r"\bкакая\s+ты\s+.*?(туп|глуп|дур|бездуш|кончен)",

        r"\bкакой\s+ты\s+.*?(туп|глуп|дур|бездуш|кончен)"

    ]


    for phrase in aggressive_commands:


        if phrase in text:


            return "insult"


    for pattern in directed_insult_patterns:


        if re.search(
            pattern,
            text
        ):


            return "insult"



    # =====================
    # ИЗВИНЕНИЕ
    # =====================


    apologies = [

        "извини",

        "прости",

        "прошу прощения",

        "я был неправ",

        "я была неправа",

        "не хотел тебя обидеть",

        "не хотела тебя обидеть"

    ]



    for word in apologies:


        if word in text:


            return "apology"






    # =====================
    # ОСКОРБЛЕНИЕ
    # =====================


    insults = [

        "тупая",

        "тупой",

        "глупая",

        "глупый",

        "идиот",

        "дура",

        "дурак",

        "дебил",

        "бесишь",

        "ненавижу",

        "отстань",

        "заткнись",

        "бездушная",

        "бездушный",

        "заебала",

        "заебал",

        "заебали"

    ]



    for word in insults:


        if word in text and (

            has_direct_marker

            or

            word in [

                "отстань",

                "заткнись",

                "ненавижу",

                "бесишь"

            ]

        ):


            return "insult"







    # =====================
    # ПОМОЩЬ / ЗАБОТА
    # =====================


    help_phrases = [

        "как ты",

        "как дела",

        "ты в порядке",

        "ты устала",

        "тебе помочь",

        "чем помочь",

        "не переживай",

        "я рядом",

        "всё будет хорошо",

        "держись"

    ]



    for phrase in help_phrases:


        if phrase in text:


            return "help"








    # =====================
    # ЛИЧНАЯ ИНФОРМАЦИЯ
    # =====================


    personal_patterns = [


        r"меня зовут",


        r"мне нравится",


        r"я занимаюсь",


        r"я работаю",


        r"я учусь",


        r"я живу",


        r"мне \d+ лет",


        r"я увлекаюсь"


    ]



    for pattern in personal_patterns:



        if re.search(
            pattern,
            text
        ):


            return "shared_info"








    # =====================
    # ФЛИРТ
    # =====================


    flirt_words = [


        "ты красивая",

        "ты милая",

        "ты прекрасная",

        "ты мне нравишься",

        "обожаю тебя",

        "люблю тебя"


    ]



    for word in flirt_words:


        if word in text:


            return "flirt"








    # =====================
    # ПОЗИТИВ
    # =====================


    positive_words = [


        "спасибо",

        "благодарю",

        "молодец",

        "классно",

        "круто",

        "отлично",

        "здорово",

        "хорошо помогла"


    ]



    for word in positive_words:


        if word in text:


            return "positive"








    # =====================
    # ОБЫЧНЫЙ РАЗГОВОР
    # =====================


    return "normal_conversation"

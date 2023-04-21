import random
import pymorphy2
from api import *


def make_response(event: dict, session_state: dict, text: str, tts: str = None, end_session: bool = False, image: dict = None):
    """Sends a response to the user"""

    response = {
        "version": event["version"],
        "session": event["session"],
        "response": {
            "text": text,
            "buttons": [
                {
                    "title": "Что ты умеешь?",
                    "hide": True
                },
                {
                    "title": "Помощь",
                    "hide": True
                },
                {
                    "title": "Список жанров",
                    "hide": True
                },
                {
                    "title": "Выход",
                    "hide": True
                }
            ],
            "end_session": end_session
        },
        "session_state": session_state
    }

    if tts is not None:
        response["response"]["tts"] = tts
    else:
        pass
    if image is not None:
        response["response"]["card"] = {
            "type": "BigImage",
            "image_id": image["image_id"],
            "title": image["title"],
            "description": image["description"],
            "button": {
                "url": image["url"]
            }
        }
    else:
        pass

    return response


def generate_film_by_genre(event: dict, session_state: dict) -> dict:
    """Generates a film by genre"""

    try:
        if "genre" in event["state"]["session"] and \
                "generate_new" in event["request"]["nlu"]["intents"] and \
                event["request"]["nlu"]["intents"]["generate_new"]["slots"]["request_generate_new"]["value"] == "generate_new":
            obj_genre = event["state"]["session"]["genre"]
        else:
            obj_genre = [get_genres()[gnr] for gnr in event["request"]["nlu"]["tokens"] if gnr in get_genres().keys()][0]
        obj_type = "FILM"
        user_given_parameters = {
            "genres": obj_genre,
            "type": obj_type
        }
        films = asyncio.get_event_loop().run_until_complete(film_by_parameters(user_given_parameters))
        film_name = random.choice(list(films))
        film_id = films[film_name]
        text_variants = ("Думаю, вам понравиться", "Советую посмотреть", "Вам должно понравиться")
        text = f"{random.choice(text_variants)} '{film_name}'"

        session_state["non_valid_genre"] = False
        session_state["film_name"] = film_name
        session_state["film_id"] = film_id
        session_state["genre"] = obj_genre
        session_state["stage"] = "film_by_parameters_is_selected"
        session_state["function"] = "film_by_parameters"

        return make_response(event, session_state, text)
    except IndexError:
        text_variants = ("Извините, я не поняла, какого жанра фильм вы хотите посмотреть. Повторите жанр",
                         "Прошу прощения, можете повторить жанр?",
                         "Прошу прощения, какого жанра фильм вы хотели посмотреть?",
                         "Извините, я не знаю такого жанра. Скажите 'Покажи жанры', чтобы просмотреть список")
        text = random.choice(text_variants)

        session_state["stage"] = "genre_selection"
        session_state["non_valid_genre"] = True
        session_state["function"] = "film_by_parameters"

        return make_response(event, session_state, text)


def generate_serial_by_genre(event: dict, session_state: dict) -> dict:
    """Generates a TV-series by genre"""

    try:
        if "genre" in event["state"]["session"] and \
                ("intents" in event["request"]["nlu"] and "generate_new" in event["request"]["nlu"]["intents"] and
                 event["request"]["nlu"]["intents"]["generate_new"]["slots"]["request_generate_new"]["value"] == "generate_new"):
            obj_genre = event["state"]["session"]["genre"]
        else:
            obj_genre = [get_genres()[gnr] for gnr in event["request"]["nlu"]["tokens"] if gnr in get_genres().keys()][
                0]
        obj_type = "TV_SERIES"
        user_given_parameters = {
            "genres": obj_genre,
            "type": obj_type
        }
        serials = asyncio.get_event_loop().run_until_complete(film_by_parameters(user_given_parameters))
        serial_name = random.choice(list(serials))
        serial_id = serials[serial_name]
        text_variants = ("Думаю, вам понравиться", "Советую посмотреть", "Вам должно понравиться", "Попробуйте посмотреть")
        text = f"{random.choice(text_variants)} '{serial_name}'"
        session_state["non_valid_genre"] = False
        session_state["film_name"] = serial_name
        session_state["film_id"] = serial_id
        session_state["function"] = "tv_series_by_parameters"
        session_state["genre"] = obj_genre
        session_state["stage"] = "tv_series_by_parameters_is_selected"

        return make_response(event, session_state, text)

    except IndexError:
        text_variants = ("Извините, я не поняла, какого жанра сериал вы хотите посмотреть. Повторите жанр",
                         "Прошу прощения, можете повторить жанр?",
                         "Прошу прощения, какого жанра сериал вы хотели посмотреть?",
                         "Извините, я не знаю такого жанра. Скажите 'Покажи жанры', чтобы просмотреть список")
        text = random.choice(text_variants)
        session_state["non_valid_genre"] = True
        session_state["stage"] = "tv_series_genre_selection"
        session_state["function"] = "tv_series_by_parameters"

        return make_response(event, session_state, text)


def film_more_info(event: dict, session_state: dict) -> dict:
    """Generates more info about the suggested film"""

    film_name = event["state"]["session"]["film_name"]
    film_id = event["state"]["session"]["film_id"]
    film_info = film_by_id_info(film_id)
    film_poster_url = film_info["poster_url"]
    film_poster_id = upload_image(film_poster_url)
    film_url = film_info["url"]

    if film_info["description"] is not None:
        description = f"{film_info['description']} " \
                      f"Фильм был снят в {film_info['year']} году, страна производства {film_info['country']}. " \
                      f"Жанры: {', '.join(genre for genre in film_info['genres'])}. " \
                      f"Рейтинг на КиноПоиске {film_info['rating']}"
        text = f"Подробнее о '{film_name}': {description}"
        tts = f"Подробнее о '{film_name}' sil <[500]> : {film_info['description']} sil <[500]>" \
              f"Фильм был снят в {film_info['year']} году, страна производства {film_info['country']}. sil <[500]>" \
              f"Жанры: {', '.join(genre for genre in film_info['genres'])}. sil <[500]>" \
              f"Рейтинг на КинаП+оиске {film_info['rating']}"
    else:
        description = f"Фильм был снят в {film_info['year']} году, страна производства {film_info['country']}. " \
                      f"Жанры: {', '.join(genre for genre in film_info['genres'])}. " \
                      f"Рейтинг на КиноПоиске {film_info['rating']}"
        text = f"Подробнее о '{film_name}': {description}"
        tts = f"Подробнее о '{film_name}' sil <[500]>. " \
              f"Фильм был снят в {film_info['year']} году, страна производства {film_info['country']}. sil <[500]>" \
              f"Жанры: {', '.join(genre for genre in film_info['genres'])}. sil <[500]>" \
              f"Рейтинг на КинаП+оиске {film_info['rating']}"

    image_block = {
        "image_id": film_poster_id,
        "title": film_name,
        "description": description,
        "url": film_url
    }

    return make_response(event, session_state, text, tts=tts, image=image_block)


def serial_more_info(event: dict, session_state: dict) -> dict:
    """Generates more info about the previously suggested TV-series"""

    serial_name = event["state"]["session"]["film_name"]
    serial_id = event["state"]["session"]["film_id"]
    serial_info = film_by_id_info(serial_id)
    serial_poster_url = serial_info["poster_url"]
    serial_poster_id = upload_image(serial_poster_url)
    serial_url = serial_info["url"]

    if serial_info["description"] is not None:
        description = f"{serial_info['description']} " \
                      f"Сериал начал выходить в {serial_info['year']} году, страна производства {serial_info['country']}. " \
                      f"Жанры: {', '.join(genre for genre in serial_info['genres'])}. " \
                      f"Рейтинг на КиноПоиске {serial_info['rating']}"

        text = f"Подробнее о '{serial_name}': {description}"
        tts = f"Подробнее о '{serial_name}' sil <[500]> : {serial_info['description']} sil <[500]>" \
              f"Сериал начал выходить в {serial_info['year']} году, страна производства {serial_info['country']}. sil <[500]>" \
              f"Жанры: {', '.join(genre for genre in serial_info['genres'])}. sil <[500]>" \
              f"Рейтинг на КинаП+оиске {serial_info['rating']}"
    else:
        description = f"Сериал начал выходить в {serial_info['year']} году, страна производства {serial_info['country']}. " \
                      f"Жанры: {', '.join(genre for genre in serial_info['genres'])}. " \
                      f"Рейтинг на КиноПоиске {serial_info['rating']}"

        text = f"Подробнее о '{serial_name}': {description}"
        tts = f"Подробнее о '{serial_name}' sil <[500]>. " \
              f"Сериал начал выходить в {serial_info['year']} году, страна производства {serial_info['country']}. sil <[500]>" \
              f"Жанры: {', '.join(genre for genre in serial_info['genres'])}. sil <[500]>" \
              f"Рейтинг на КинаП+оиске {serial_info['rating']}"

    image_block = {
        "image_id": serial_poster_id,
        "title": serial_name,
        "description": description,
        "url": serial_url
    }

    return make_response(event, session_state, text, tts=tts, image=image_block)


def film_by_name_more_info(event: dict, session_state: dict) -> dict:
    """Generates more info about the film that was requested by the user"""

    morph = pymorphy2.MorphAnalyzer(lang="ru")
    try:
        film_type = [word for word in
                     (form.word for form in morph.parse("фильм")[0].lexeme + morph.parse("сериал")[0].lexeme)
                     if word in event["request"]["nlu"]["tokens"]][0]
        film_name = " ".join(event["request"]["nlu"]["tokens"][event["request"]["nlu"]["tokens"].index(film_type) + 1:])
        film = film_by_name_info(film_name)

        try:
            film_name, film_info = film["name"], film["info"]
            film_poster_url = film_info["poster_url"]
            film_poster_id = upload_image(film_poster_url)

            if film_type in [word for word in (form.word for form in morph.parse("фильм")[0].lexeme)]:
                if film_info["description"] is not None:
                    description = f"{film_info['description']} " \
                                  f"Фильм был снят в {film_info['year']} году, страна производства {film_info['country']}. " \
                                  f"Жанры: {', '.join(genre for genre in film_info['genres'])}. " \
                                  f"Рейтинг на КиноПоиске {film_info['rating']}"
                    text = f"Подробнее о '{film_name}': {description}"
                    tts = f"Подробнее о '{film_name}' sil <[500]> : {film_info['description']} sil <[500]>" \
                          f"Фильм был снят в {film_info['year']} году, страна производства {film_info['country']}. sil <[500]>" \
                          f"Жанры: {', '.join(genre for genre in film_info['genres'])}. sil <[500]>" \
                          f"Рейтинг на КинаП+оиске {film_info['rating']}"
                else:
                    description = f"Фильм был снят в {film_info['year']} году, страна производства {film_info['country']}. " \
                                  f"Жанры: {', '.join(genre for genre in film_info['genres'])}. " \
                                  f"Рейтинг на КиноПоиске {film_info['rating']}"
                    text = f"Подробнее о '{film_name}': {description}"
                    tts = f"Подробнее о '{film_name}' sil <[500]>" \
                          f"Фильм был снят в {film_info['year']} году, страна производства {film_info['country']}. sil <[500]>" \
                          f"Жанры: {', '.join(genre for genre in film_info['genres'])}. sil <[500]>" \
                          f"Рейтинг на КинаП+оиске {film_info['rating']}"
            else:
                if film_info["description"] is not None:
                    description = f"{film_info['description']} " \
                                  f"Сериал начал выходить в {film_info['year']} году, страна производства {film_info['country']}. " \
                                  f"Жанры: {', '.join(genre for genre in film_info['genres'])}. " \
                                  f"Рейтинг на КиноПоиске {film_info['rating']}"
                    text = f"Подробнее о '{film_name}': {description}"
                    tts = f"Подробнее о '{film_name}' sil <[500]> : {film_info['description']} sil <[500]>" \
                          f"Сериал начал выходить в {film_info['year']} году, страна производства {film_info['country']}. sil <[500]>" \
                          f"Жанры: {', '.join(genre for genre in film_info['genres'])}. sil <[500]>" \
                          f"Рейтинг на КинаП+оиске {film_info['rating']}"
                else:
                    description = f"Сериал начал выходить в {film_info['year']} году, страна производства {film_info['country']}. " \
                                  f"Жанры: {', '.join(genre for genre in film_info['genres'])}. " \
                                  f"Рейтинг на КиноПоиске {film_info['rating']}"
                    text = f"Подробнее о '{film_name}': {description}"
                    tts = f"Подробнее о '{film_name}' sil <[500]>" \
                          f"Сериал начал выходить в {film_info['year']} году, страна производства {film_info['country']}. sil <[500]>" \
                          f"Жанры: {', '.join(genre for genre in film_info['genres'])}. sil <[500]>" \
                          f"Рейтинг на КинаП+оиске {film_info['rating']}"

            image_block = {
                "image_id": film_poster_id,
                "title": film_name,
                "description": description,
                "url": film_poster_url
            }

            return make_response(event, session_state, text, tts=tts, image=image_block)
        except KeyError:
            text_variants = ("Извините, я не смогла найти такой фильм",
                             "Прошу прощения, кажется, я не знаю такого фильма",
                             "Простите, мне неизвестен этот фильм")
            text = random.choice(text_variants)

            return make_response(event, session_state, text)
    except IndexError:
        text = "Извините, я вас не поняла. Не могли бы вы повторить запрос?"
        return make_response(event, session_state, text)


def actor_by_name_more_info(event: dict, session_state: dict) -> dict:
    """Generates info about the actor that was requested by the user"""

    morph = pymorphy2.MorphAnalyzer(lang="ru")
    try:
        actor_flag = [word for word in
                      (form.word for form in morph.parse("актёр")[0].lexeme + morph.parse("актриса")[0].lexeme)
                      if word in event["request"]["nlu"]["tokens"]][0]
        actor_name = " ".join(
            event["request"]["nlu"]["tokens"][event["request"]["nlu"]["tokens"].index(actor_flag) + 1:])
        actor = actor_by_name_info(actor_name)
        try:
            actor_name, actor_info = actor["name"], actor["info"]
            actor_poster_url = actor_info["poster_url"]
            actor_poster_id = upload_image(actor_poster_url)
            if "death" in actor_info:
                if "fact" in actor_info:
                    description = f"Дата рождения {actor_info['birthday']}, место рождения {actor_info['birthplace']}. " \
                                  f"Возраст {actor_info['age']}, дата смерти {actor_info['death']}. " \
                                  f"Интересный факт: {actor_info['fact']}"
                    text = f"Подробнее о '{actor_name}': {description}"
                    tts = f"Подробнее о '{actor_name}'. sil <[500]>" \
                          f"Дата рождения {actor_info['birthday']}, место рождения {actor_info['birthplace']}. sil <[500]>" \
                          f"Возраст {actor_info['age']}, дата смерти {actor_info['death']}. sil <[500]>" \
                          f"Интересный факт: {actor_info['fact']}"
                else:
                    description = f"Дата рождения {actor_info['birthday']}, место рождения {actor_info['birthplace']}. " \
                                  f"Возраст {actor_info['age']}, дата смерти {actor_info['death']}"
                    text = f"Подробнее о '{actor_name}': {description}"
                    tts = f"Подробнее о '{actor_name}'. sil <[500]>" \
                          f"Дата рождения {actor_info['birthday']}, место рождения {actor_info['birthplace']}. sil <[500]>" \
                          f"Возраст {actor_info['age']}, дата смерти {actor_info['death']}"
            else:
                if "fact" in actor_info:
                    description = f"Дата рождения {actor_info['birthday']}, место рождения {actor_info['birthplace']}. " \
                                  f"Возраст {actor_info['age']}. " \
                                  f"Интересный факт: {actor_info['fact']}"
                    text = f"Подробнее о '{actor_name}': {description}"
                    tts = f"Подробнее о '{actor_name}'. sil <[500]>" \
                          f"Дата рождения {actor_info['birthday']}, место рождения {actor_info['birthplace']}. sil <[500]>" \
                          f"Возраст {actor_info['age']}. sil <[500]>" \
                          f"Интересный факт: {actor_info['fact']}"
                else:
                    description = f"Дата рождения {actor_info['birthday']}, место рождения {actor_info['birthplace']}. " \
                                  f"Возраст {actor_info['age']}"
                    text = f"Подробнее о '{actor_name}': {description}"
                    tts = f"Подробнее о '{actor_name}'. sil <[500]>" \
                          f"Дата рождения {actor_info['birthday']}, место рождения {actor_info['birthplace']}. sil <[500]>" \
                          f"Возраст {actor_info['age']}"

            image_block = {
                "image_id": actor_poster_id,
                "title": actor_name,
                "description": description,
                "url": actor_poster_url
            }

            return make_response(event, session_state, text, tts=tts, image=image_block)
        except KeyError:
            text_variants = ("Извините, я не смогла найти такого актёра",
                             "Прошу прощения, кажется, я не знаю такого актёра",
                             "Простите, мне неизвестен этот актёр")
            text = random.choice(text_variants)

            return make_response(event, session_state, text)
    except IndexError:
        text = "Извините, я вас не поняла. Не могли бы вы повторить запрос?"
        return make_response(event, session_state, text)


def handler(event: dict, context) -> dict:
    """Handler function for the Yandex Alisa skill"""

    try:
        session_state = event["state"]["session"]
    except KeyError:
        session_state = {}

    # Ответ на вопрос "Что ты умеешь/можешь?"
    if "request" in event and \
            (all(token in event["request"]["nlu"]["tokens"] for token in ("что", "ты", "умеешь"))
             or
             all(token in event["request"]["nlu"]["tokens"] for token in ("что", "ты", "можешь"))):
        text = "Я могу подсказать вам, какой фильм или сериал можно посмотреть, чтобы приятно провести время. \n" \
               "Также я могу рассказать про какой-либо конкретный фильм или актёра. \n" \
               "Чтобы узнать список команд скажите 'Помощь'"
        tts = "Я могу подсказать вам, какой фильм или сериал можно посмотреть, чтобы приятно провести время. sil <[500]>" \
              "Также я могу рассказать про какой-либо конкретный фильм или актёра. sil <[500]>" \
              "Чтобы узнать список команд скажите 'Помощь'"

        return make_response(event, session_state, text, tts=tts)

    # Список команд по запросу "Помощь"
    if "request" in event and "помощь" in event["request"]["nlu"]["tokens"]:
        text = "Чтобы получить фильм, вы можете сказать 'Подскажи какой фильм можно посмотреть вечерком'. \n" \
               "Чтобы получить сериал, скажите, например, 'Посоветуй какой-нибудь сериал на вечер'. \n" \
               "Сказав 'Расскажи подробнее', вы можете узнать больше о предложенном вам фильме или сериале. \n" \
               "По командам наподобие 'Посоветуй другой' вы можете перегенерировать полученный ответ. \n" \
               "Чтобы узнать подробнее про определённый фильм или сериал, скажите 'Расскажи подробнее про фильм/сериал' и название фильма/сериала. \n" \
               "Чтобы узнать подробнее про определённого актёра, скажите 'Расскажи подробнее про актёра' и имя актёра " \
               "или 'Расскажи об актрисе' и имя актрисы. Пожалуйста, называйте имена и фамилии в именительном падеже, чтобы избежать недопониманий. \n" \
               "Скажите 'Покажи жанры', чтобы узнать список жанров. \n" \
               "Скажите 'Класс', 'Выход' или 'Спасибо', чтобы выйти из навыка"
        tts = "Чтобы получить фильм, вы можете сказать 'Подскажи какой фильм можно посмотреть вечерком' sil <[500]>" \
              "Чтобы получить сериал, скажите например 'Посоветуй какой-нибудь сериал на вечер' sil <[500]>" \
              "Сказав 'Расскажи подробнее', вы можете узнать больше о предложенном вам фильме или сериале sil <[500]>" \
              "По командам наподобие 'Посоветуй другой' вы можете перегенерировать полученный ответ sil <[500]>" \
              "Чтобы узнать подробнее про определённый фильм или сериал, скажите 'Расскажи подробнее про фильм/сериал', и название фильма/сериала sil <[500]>" \
              "Чтобы узнать подробнее про определённого актёра, скажите 'Расскажи подробнее про актёра', и имя актёра sil <[200]>" \
              "или 'Расскажи об актрисе', и имя актрисы. Пожалуйста, называйте имена и фамилии в именительном падеже, чтобы избежать недопониманий sil <[500]>" \
              "Скажите 'Покажи жанры' чтобы узнать список жанров sil <[500]>" \
              "Скажите 'Класс', sil <[50]> 'Выход' или 'Спасибо' чтобы выйти из навыка"

        return make_response(event, session_state, text, tts=tts)

    # Пользователь просит список доступных жанров
    if "request" in event and \
            ("intents" in event["request"]["nlu"] and "genre_list" in event["request"]["nlu"]["intents"] and
             event["request"]["nlu"]["intents"]["genre_list"]["slots"]["request_genre_list"]["value"] == "genre_list_is_needed"):
        text = "Вот список доступных жанров:" \
               "Триллер \n" \
               "Драма \n" \
               "Детектив \n" \
               "Криминал \n" \
               "Фантастика \n" \
               "Приключения \n" \
               "Биография \n" \
               "Вестерн \n" \
               "Боевик \n" \
               "Фэнтези \n" \
               "Комедия \n" \
               "Военный \n" \
               "История \n" \
               "Ужасы \n" \
               "Семейный \n" \
               "Мюзикл \n" \
               "Спорт \n" \
               "Документальный \n" \
               "Аниме"
        tts = "Вот список доступных жанров:" \
              "Триллер sil<[500]>" \
              "Драма sil<[500]>" \
              "Детектив sil<[500]>" \
              "Криминал sil<[500]>" \
              "Фантастика sil<[500]>" \
              "Приключения sil<[500]>" \
              "Биография sil<[500]>" \
              "Вестерн sil<[500]>" \
              "Боевик sil<[500]>" \
              "Фэнтези sil<[500]>" \
              "Комедия sil<[500]>" \
              "Военный sil<[500]>" \
              "История sil<[500]>" \
              "Ужасы sil<[500]>" \
              "Семейный sil<[500]>" \
              "Мюзикл sil<[500]>" \
              "Спорт sil<[500]>" \
              "Документальный sil<[500]>" \
              "Аниме"

        return make_response(event, session_state, text, tts=tts)

    # Выход из навыка
    if "request" in event and any(token in event["request"]["nlu"]["tokens"] for token in ("выход", "спасибо", "класс")):

        text = "Рада была помочь, обращайтесь"
        img_list = image_list()
        for image_id in img_list:
            delete_image(image_id)

        return make_response(event, session_state, text, end_session=True)

    # Проверка на активность навыка
    if "request" in event and event["request"]["original_utterance"] == "ping":
        text = "pong"

        return make_response(event, session_state, text)

    # Новая сессия
    if "session" in event and event["session"]["new"]:
        welcome_text = "Здравствуйте, чем могу помочь? Если хотите, я могу посоветовать вам фильм или сериал. " \
                       "Просто скажите 'Посоветуй фильм'. " \
                       "Если что-то непонятно, скажите 'Помощь'"

        return make_response(event, session_state, welcome_text)

    # Пользователь просит подсказать фильм
    if "request" in event and \
            ("intents" in event["request"]["nlu"] and
             "advice" in event["request"]["nlu"]["intents"] and
             event["request"]["nlu"]["intents"]["advice"]["slots"]["film_type"]["value"] == "film"):
        text = "Случайный или по жанру?"
        session_state["stage"] = "film_selection"

        return make_response(event, session_state, text)

    # Пользователь просит случайный фильм
    if "request" in event and \
            (("request" in event and "stage" in event["state"]["session"] and "случайный" in event["request"]["nlu"]["tokens"] and
              event["state"]["session"]["stage"] == "film_selection")
             or
             ("request" in event and "function" in event["state"]["session"] and event["state"]["session"]["function"] == "film_random" and
              "intents" in event["request"]["nlu"] and "generate_new" in event["request"]["nlu"]["intents"] and
              event["request"]["nlu"]["intents"]["generate_new"]["slots"]["request_generate_new"]["value"] == "generate_new")):
        film = film_random()
        film_name = list(film.keys())[0]
        film_id = film[film_name]
        text_variants = ("Думаю, вам понравиться", "Советую посмотреть", "Вам должно понравиться", "Попробуйте посмотреть")
        text = f"{random.choice(text_variants)} '{film_name}'"
        session_state["stage"] = "film_random_is_selected"
        session_state["function"] = "film_random"
        session_state["film_name"] = film_name
        session_state["film_id"] = film_id

        return make_response(event, session_state, text)

    # Пользователь просит больше информации о случайном фильме
    if "request" in event and event["state"]["session"] and \
            "stage" in event["state"]["session"] and event["state"]["session"]["stage"] == "film_random_is_selected" and \
            ("intents" in event["request"]["nlu"] and "more_info" in event["request"]["nlu"]["intents"] and
             event["request"]["nlu"]["intents"]["more_info"]["slots"]["request_more_info"]["value"] == "more_info_is_needed") and \
            all(token not in event["request"]["command"] for token in
                ("про фильм", "про сериал", "о фильме", "о сериале")) and \
            all(token not in event["request"]["command"] for token in
                ("про актёра", "про актрису", "об актёре", "об актрисе", "о актёре", "о актрисе")):
        return film_more_info(event, session_state)

    # Пользователь просит фильм по жанру
    if "request" in event and \
            all(token in event["request"]["nlu"]["tokens"] for token in ["по", "жанру"]) and \
            "stage" in event["state"]["session"] and event["state"]["session"]["stage"] == "film_selection":
        text = "Какого жанра фильм вы бы хотели посмотреть? Чтобы узнать список доступных жанров, скажите 'Покажи жанры'"
        session_state["stage"] = "genre_selection"
        session_state["function"] = "film_by_parameters"

        return make_response(event, session_state, text)
    if "request" in event and event["state"]["session"] and \
            (("stage" in event["state"]["session"] and event["state"]["session"]["stage"] == "genre_selection")
             or
             ("non_valid_genre" in event["state"]["session"] and event["state"]["session"]["non_valid_genre"] and
              "stage" in event["state"]["session"] and event["state"]["session"]["stage"] == "genre_selection")
             or
             ("request" in event and "function" in event["state"]["session"] and event["state"]["session"]["function"] == "film_by_parameters" and
              "intents" in event["request"]["nlu"] and "generate_new" in event["request"]["nlu"]["intents"] and
              event["request"]["nlu"]["intents"]["generate_new"]["slots"]["request_generate_new"]["value"] == "generate_new")):
        return generate_film_by_genre(event, session_state)

    # Пользователь просит больше информации о фильме по жанру
    if "request" in event and event["state"]["session"] and \
            "stage" in event["state"]["session"] and event["state"]["session"]["stage"] == "film_by_parameters_is_selected" and \
            "intents" in event["request"]["nlu"] and "more_info" in event["request"]["nlu"]["intents"] and \
            event["request"]["nlu"]["intents"]["more_info"]["slots"]["request_more_info"]["value"] == "more_info_is_needed" and \
            all(token not in event["request"]["command"] for token in
                ("про фильм", "про сериал", "о фильме", "о сериале")) and \
            all(token not in event["request"]["command"] for token in
                ("про актёра", "про актрису", "об актёре", "об актрисе", "о актёре", "о актрисе")):
        return film_more_info(event, session_state)

    # Пользователь просит подсказать сериал
    if "request" in event and \
            "advice" in event["request"]["nlu"]["intents"] and \
            event["request"]["nlu"]["intents"]["advice"]["slots"]["film_type"]["value"] == "tv_series":
        text = "Какого жанра сериал вы бы хотели посмотреть? Чтобы узнать список доступных жанров, скажите 'Покажи жанры'"
        session_state["stage"] = "tv_series_genre_selection"
        session_state["function"] = "tv_series_by_parameters"

        return make_response(event, session_state, text)
    if "request" in event and event["state"]["session"] and \
            (("stage" in event["state"]["session"] and event["state"]["session"]["stage"] == "tv_series_genre_selection")
             or
             ("non_valid_genre" in event["state"]["session"] and event["state"]["session"]["non_valid_genre"] and
              "stage" in event["state"]["session"] and event["state"]["session"]["stage"] == "tv_series_genre_selection")
             or
             ("function" in event["state"]["session"] and event["state"]["session"]["function"] == "tv_series_by_parameters" and
              "intents" in event["request"]["nlu"] and "generate_new" in event["request"]["nlu"]["intents"] and
              event["request"]["nlu"]["intents"]["generate_new"]["slots"]["request_generate_new"]["value"] == "generate_new")):
        return generate_serial_by_genre(event, session_state)

    # Пользователь просит больше информации о сериале по жанру
    if "request" in event and event["state"]["session"] and \
            "stage" in event["state"]["session"] and event["state"]["session"]["stage"] == "tv_series_by_parameters_is_selected" and \
            ("intents" in event["request"]["nlu"] and "more_info" in event["request"]["nlu"]["intents"] and
             event["request"]["nlu"]["intents"]["more_info"]["slots"]["request_more_info"]["value"] == "more_info_is_needed") and \
            all(token not in event["request"]["command"] for token in
                ("про фильм", "про сериал", "о фильме", "о сериале")) and \
            all(token not in event["request"]["command"] for token in
                ("про актёра", "про актрису", "об актёре", "об актрисе", "о актёре", "о актрисе")):
        return serial_more_info(event, session_state)

    # Пользователь просит информацию по конкретному фильму
    if "request" in event and \
            (any(token in event["request"]["command"] for token in("про фильм", "про сериал", "о фильме", "о сериале"))) and \
            ("intents" in event["request"]["nlu"] and "more_info" in event["request"]["nlu"]["intents"] and
             event["request"]["nlu"]["intents"]["more_info"]["slots"]["request_more_info"]["value"] == "more_info_is_needed"):
        return film_by_name_more_info(event, session_state)

    # Пользователь просит информацию по конкретному актёру
    if "request" in event and \
            any(token in event["request"]["command"] for token in
                ("про актёра", "про актрису", "об актёре", "об актрисе", "о актёре", "о актрисе")) and \
            ("intents" in event["request"]["nlu"] and "more_info" in event["request"]["nlu"]["intents"] and
             event["request"]["nlu"]["intents"]["more_info"]["slots"]["request_more_info"]["value"] == "more_info_is_needed"):
        return actor_by_name_more_info(event, session_state)

    text_variants = ("Извините, я вас не поняла. Повторите запрос",
                     "Простите, я не поняла запрос. Можете повторить?",
                     "Прошу прощения, я вас не поняла. Скажите 'Помощь', чтобы узнать список команд")
    text = random.choice(text_variants)

    return make_response(event, session_state, text)

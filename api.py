import json
import datetime
import asyncio
import aiohttp
import requests
from constants import *


async def film_by_parameters_request(session: aiohttp.ClientSession, url: str, headers: dict, params: dict) -> dict:
    """
    Asynchronous request function for the Kinopoisk unofficial API to parse the required data.

    :param session: AIOHTTP session object
    :param url: url for an API call
    :param headers: headers for an API call
    :param params: parameters for an API call
    :return: single film_name-film_ID pair
    """
    name_id = {}

    async with session.get(url, headers=headers, params=params) as resp:
        response = await resp.json()
        for item in range(len(response["items"])):
            name_id[response["items"][item]["nameRu"]] = response["items"][item]["kinopoiskId"]
    name_id = {key: value for key, value in name_id.items() if all(item is not None for item in (key, value))}

    return name_id


async def film_by_parameters(user_given_parameters: dict) -> dict:
    """
    Asynchronous request function for forming name-id pairs from all the films received from the Kinopoisk unofficial API.

    :param user_given_parameters: user-specified parameters for an API call
    :return: up to 100 film_name-film_ID pairs
    """
    name_id = {}

    async with aiohttp.ClientSession() as session:

        url = "https://kinopoiskapiunofficial.tech/api/v2.2/films"
        headers = {
            "accept": 'application/json',
            "X-API-KEY": API_V2_KEY
        }
        params = {
            "order": "RATING",
            "productionStatus": "COMPLETED",
            "ratingFrom": "7", "ratingTo": "10",
            "yearFrom": "1990", "yearTo": f"{datetime.date.today().year}",
            "page": "1"
        }

        user_given_parameters = {key: value for key, value in user_given_parameters.items() if all(item is not None for item in (key, value))}
        params.update(user_given_parameters)

        # Getting total number of pages in API response
        async with session.get(url, headers=headers, params=params) as resp:
            response = await resp.json()
            pages = response["totalPages"]

        # Getting data from all pages with films in API response
        tasks = []
        for page in range(1, pages + 1):
            params = {
                "order": "RATING",
                "productionStatus": "COMPLETED",
                "ratingFrom": "7", "ratingTo": "10",
                "yearFrom": "1990", "yearTo": f"{datetime.date.today().year}",
                "page": f"{page}"
            }
            params.update(user_given_parameters)
            tasks.append(asyncio.ensure_future(film_by_parameters_request(session, url, headers, params)))
        for task in await asyncio.gather(*tasks):
            name_id.update(task)

    return name_id


def film_by_id_info(film_id: str) -> dict:
    """
    Requests additional information about the film using the Kinopoisk unofficial API.

    :param film_id: film ID as in the KinoPoisk database for an API call
    :return: film description, rating, release year, country, genres, poster url and film url for Kinopoisk page
    """
    url = f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{film_id}"
    headers = {
        "accept": 'application/json',
        "X-API-KEY": API_V2_KEY
    }
    response = requests.get(url, headers=headers).json()

    try:
        return {
            "description": response["description"].replace("\n", ""),
            "rating": response["ratingKinopoisk"],
            "year": response["year"],
            "country": response["countries"][0]["country"],
            "genres": [genre["genre"] for genre in response["genres"]],
            "poster_url": response["posterUrlPreview"],
            "url": response["webUrl"]
        }
    except (AttributeError, KeyError):
        return {
            "description": None,
            "rating": response["ratingKinopoisk"],
            "year": response["year"],
            "country": response["countries"][0]["country"],
            "genres": [genre["genre"] for genre in response["genres"]],
            "poster_url": response["posterUrlPreview"],
            "url": response["webUrl"]
        }


def film_random() -> dict:
    """
    Forms film_name-film_id pair from a random film received from the Kinopoisk unofficial API.

    :return: single film_name-film_ID pair
    """
    name_id = {}

    url = "https://api.kinopoisk.dev/v1/movie/random"
    headers = {
        "accept": "application/json",
        "X-API-KEY": API_V1_KEY
    }
    response = requests.get(url, headers=headers).json()

    name_id[response["name"].replace(u"\xa0", " ").replace(u"\u202f", " ").replace("\n", " ")] = response["id"]

    return name_id


def get_genres() -> dict:
    """
    Reads json file with all available genres and forms film_genre-genre_ID pairs used for a Kinopoisk unofficial API call.

    :return: 221 genre-id pairs
    """
    with open("genres.json", "r", encoding="windows-1251") as file:
        genres = json.load(file)

    return genres


def film_by_name_info(film_name: str) -> dict:
    """
    Forms film_name-film_info pair from user requested film received from the Kinopoisk unofficial API.

    :param film_name: user-specified film name
    :return: film description, rating, release year, country, genres, poster url
    """
    film = {}

    url = "https://api.kinopoisk.dev/v1/movie"
    headers = {
        "accept": "application/json",
        "X-API-KEY": API_V1_KEY
    }
    params = {
        "order": "RATING",
        "productionStatus": "COMPLETED",
        "ratingFrom": "7", "ratingTo": "10",
        "yearFrom": "1990", "yearTo": f"{datetime.date.today().year}",
        "limit": "1",
        "page": "1",
        "name": film_name
    }
    try:
        response = requests.get(url, headers=headers, params=params).json()

        film["name"] = response["docs"][0]["name"]
        film["info"] = {
            "description": response["docs"][0]["description"],
            "rating": response["docs"][0]["rating"]["kp"],
            "year": response["docs"][0]["year"],
            "country": response["docs"][0]["countries"][0]["name"],
            "genres": [genre["name"] for genre in response["docs"][0]["genres"]],
            "poster_url": response["docs"][0]["poster"]["previewUrl"]
        }

        film["name"] = film["name"].replace(u"\xa0", " ").replace(u"\u202f", " ").replace("\n", " ")
        if film["info"]["description"] is not None:
            film["info"]["description"] = film["info"]["description"].replace(u"\xa0", " ").replace(u"\u202f", " ").replace("\n"," ")
        else:
            film["info"]["description"] = None

        return film
    except IndexError:
        film = {}

        return film


def actor_by_name_info(actor_name: str) -> dict:
    """
     Forms actor_name-actor_info pair for user requested actor received from the Kinopoisk unofficial API.

     :param actor_name: user-specified actor name
     :return: single actor_name-actor_info pair
     """
    actor = {}

    try:
        url = "https://kinopoiskapiunofficial.tech/api/v1/persons"
        headers = {
            "accept": "application/json",
            "X-API-KEY": API_V2_KEY
        }
        params = {
            "page": "1",
            "name": actor_name
        }
        response = requests.get(url, headers=headers, params=params).json()

        actor_id = response["items"][0]["kinopoiskId"]
    except (KeyError, IndexError):
        actor_id = None

    try:
        if actor_id is not None:
            url = f"https://kinopoiskapiunofficial.tech/api/v1/staff/{actor_id}"
            headers = {
                "accept": "application/json",
                "X-API-KEY": API_V2_KEY
            }
            response = requests.get(url, headers=headers).json()

            actor["name"] = response["nameRu"]
            actor["info"] = {
                "birthday": response["birthday"],
                "birthplace": response["birthplace"],
                "age": response["age"],
                "death": response["death"],
                "fact": response["facts"][0] if response["facts"] else None,
                "poster_url": response["posterUrl"]
            }
            actor["info"] = {key: value for key, value in actor["info"].items() if all(item is not None for item in (key, value))}
        else:
            actor = {}
    except KeyError:
        actor = {}

    return actor


def check_place() -> float:
    """Returns the percentage of space occupied by images on the Yandex server."""
    url = "https://dialogs.yandex.net/api/v1/status"
    headers = {
        "Authorization": YANDEX_API_KEY
    }
    response = requests.get(url, headers=headers).json()

    used, total = response["images"]["quota"]["used"], response["images"]["quota"]["total"]

    return used / total


def image_list() -> tuple:
    """Returns a list of IDs for images contained on the Yandex server."""
    url = f"https://dialogs.yandex.net/api/v1/skills/{SKILL_ID}/images"
    headers = {
        "Authorization": YANDEX_API_KEY
    }
    response = requests.get(url, headers=headers).json()

    img_list = tuple(image["id"] for image in response["images"])

    return img_list


def upload_image(image_url: str) -> str:
    """Uploads image from web to the Yandex server."""
    url = f"https://dialogs.yandex.net/api/v1/skills/{SKILL_ID}/images"
    headers = {
        "Authorization": YANDEX_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "url": image_url
    }
    response = requests.post(url, headers=headers, data=json.dumps(data)).json()

    image_id = response["image"]["id"]

    return image_id


def delete_image(image_id: str) -> None:
    """Deletes image from the Yandex server."""
    url = f"https://dialogs.yandex.net/api/v1/skills/{SKILL_ID}/images/{image_id}"
    headers = {
        "Authorization": YANDEX_API_KEY
    }
    requests.delete(url, headers=headers)

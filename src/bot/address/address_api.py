# scr/bot/address/address_api.py

import os
from copy import deepcopy

import requests
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
load_dotenv(find_dotenv(".env.example"))  # В будущем нужно удалить

ENDPOINT = os.getenv("GEOCODER_BASE_URL", default="None")
GEOCODER_APIKEY = os.getenv("GEOCODER_APIKEY", default="None")
GEOCODER_INPUT_PARAMS = dict(
    geocode=None,  # Обязательный параметр
    apikey=None,  # Обязательный параметр
    sco=None,  # Значение по умолчанию: longlat.
    kind=None,  #
    rspn=None,  # Значение по умолчению: 0.
    ll=None,  #
    spn=None,  #
    bbox=None,  #
    format=None,  # Значение по умолчанию: xml.
    results=None,  # Значение по умолчанию: 10. Максимальное: 100.
    skip=None,  # Значение по умолчанию: 0.
    lang=None,  # Значение по умолчанию: ru_RU.
    callback=None,
)
MAXIMUM_OBJECTS = os.getenv("MAXIMUM_OBJECTS_FROM_GEOCODER", default="10")
DATA_EXTRACTION_ERROR_MESSAGE = "Ошибка извлечения адресных данных: {error}"
NETWORK_ERROR = "Сетевая ошибка: {error}. " "Параметры get запроса: ENDPOINT: {url}; params: {params}."


def _extract_address_data(response: dict) -> list:
    geo_objects = response["response"]["GeoObjectCollection"]["featureMember"]
    extracted_addresses_data = []
    for geo_object in geo_objects:
        address_data = geo_object["GeoObject"]
        text = address_data["metaDataProperty"]["GeocoderMetaData"]["text"]
        points = address_data["Point"]["pos"]
        extracted_addresses_data.append(
            (
                text,
                points,
            )
        )
    return extracted_addresses_data


def search_addresses(
    geocode: str,
    apikey: str = GEOCODER_APIKEY,
    format_response: str = "json",
    results: int = MAXIMUM_OBJECTS,
    sco="latlong",
    query_params: dict = None,
) -> list[tuple[str]]:
    """
    Позволяет определять координаты топонима по его адресу,
    или адрес точки по её координатам.

    :param geocode: Адрес либо географические координаты искомого объекта;
    :param apikey: Ключ от API интерфейса 'JavaScript API и HTTP Геокодер';
    :param format_response: Формат возвращаемого результата
           (поддерживается 'json');
    :param sco: Порядок записи координат (longlat — долгота, широта;
                                          latlong — широта, долгота).
    :param results: Формат возвращаемого результата (поддерживается 'json');
    :param query_params: Параметры запроса для API Геокодера;
    :return: Возвращает список кортежей подходящий адресов в формате:
    (полный адрес топонима одной строкой, координаты геоточки).
    """
    if query_params is None:
        query_params = deepcopy(GEOCODER_INPUT_PARAMS)
        query_params["geocode"] = geocode
        query_params["apikey"] = apikey
        query_params["format"] = format_response
        query_params["results"] = results
        query_params["sco"] = sco
    request_parameters = {
        "url": ENDPOINT,
        "params": query_params,
    }
    try:
        response = requests.get(**request_parameters)
    except requests.RequestException as error:
        error_message = NETWORK_ERROR.format(error=error, **request_parameters)
        # Сообщение для логера
        # logging.exception('error_message')
        raise ConnectionError(error_message)
    if response.status_code != requests.codes.ok:
        response.raise_for_status()
    try:
        addresses = _extract_address_data(response.json())
    except KeyError as error:
        error_message = DATA_EXTRACTION_ERROR_MESSAGE.format(error=error)
        # Сообщение для логера
        # logging.exception('error_message')
        raise KeyError(error_message)
    return addresses


def mock_get_city_name(text: str) -> list[str]:
    return ["Москва", "Балашиха", "Железнодорожный"]

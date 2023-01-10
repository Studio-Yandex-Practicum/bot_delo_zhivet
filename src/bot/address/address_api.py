# scr/bot/address/address_api.py

import os
from copy import deepcopy

import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
load_dotenv(find_dotenv('.env.example'))  # В будущем нужно удалить

GEOCODER_BASE_URL = 'https://geocode-maps.yandex.ru/1.x/'
GEOCODER_APIKEY = os.getenv('GEOCODER_APIKEY', default='None')
GEOCODER_INPUT_PARAMS = dict(
    geocode=None,
    apikey=None,
    sco=None,
    kind=None,
    ll=None,
    spn=None,
    bbox=None,
    format=None,
    results=None,
    skip=None,
    lang=None,
    callback=None,
)
MAXIMUM_OBJECTS = 10
DATA_EXTRACTION_ERROR_MESSAGE = 'Ошибка извлечения адресных данных: {error}'


def _configure_params(params: dict) -> dict:
    params['sco'] = 'latlong'  # широта, долгота
    params['format'] = 'json'  # результат возвращается в формате JSON
    params['results'] = MAXIMUM_OBJECTS  # максимальное количество совпадений
    return params


def _extract_address_data(response: dict) -> list:
    geoobjects = response['response']['GeoObjectCollection']['featureMember']
    extracted_addresses_data = []
    for geoobject in geoobjects:
        address_data = geoobject['GeoObject']
        text = address_data['metaDataProperty']['GeocoderMetaData']['text']
        points = address_data['Point']['pos']
        extracted_addresses_data.append((text, points,))
    return extracted_addresses_data


def search_addresses(
        geocode: str,
        apikey: str = GEOCODER_APIKEY,
        query_params: dict = None
) -> list[tuple[str]]:
    """
    Позволяет определять координаты топонима по его адресу,
    или адрес точки по её координатам.

    :param geocode: Адрес либо географические координаты искомого объекта;
    :param apikey: Ключ от API интерфейса 'JavaScript API и HTTP Геокодер';
    :param query_params: Параметры запроса для API Геокодера;
    :return: Возвращает список кортежей подходящий адресов в формате:
    (полный адрес топонима одной строкой, координаты геоточки).
    """
    if query_params is None:
        query_params = deepcopy(GEOCODER_INPUT_PARAMS)
    query_params = _configure_params(query_params)
    query_params['geocode'] = geocode
    query_params['apikey'] = apikey
    response = requests.get(GEOCODER_BASE_URL, params=query_params)
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

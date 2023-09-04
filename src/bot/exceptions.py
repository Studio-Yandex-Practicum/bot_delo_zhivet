class DadataUnavailabilityError(Exception):

    """Сервис dadata недоступен."""


class DadataForbidden(Exception):
    """Проблема с аутентификацией, или лимитом запросов."""


class DadataNoResult(Exception):
    """Отсутствуют результаты предполагаемых адресов."""

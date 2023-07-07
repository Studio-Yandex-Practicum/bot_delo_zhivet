from dadata import Dadata

from core.config import settings

dadata = Dadata(settings.DADATA_TOKEN, settings.DADATA_SECRET)


def get_fields_from_dadata(data):
    try:
        result = dadata.suggest("address", data)[0]
        if result["data"]["settlement_with_type"] is not None:
            city = result["data"]["settlement_with_type"]
        else:
            city = result["data"]["city_with_type"]
        full_address = result["unrestricted_value"]
        latitude = float(result["data"]["geo_lat"])
        longitude = float(result["data"]["geo_lon"])
        return dict(
            city=city,
            full_address=full_address,
            latitude=latitude,
            longitude=longitude,
        )
    except (IndexError, TypeError):
        return None

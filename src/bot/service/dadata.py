import os

from dadata import Dadata

token = os.environ["DADATA_TOKEN"]
secret = os.environ["DADATA_SECRET"]
dadata = Dadata(token, secret)


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
    except IndexError:
        return None

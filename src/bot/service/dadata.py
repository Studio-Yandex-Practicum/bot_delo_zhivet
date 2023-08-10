from dadata import DadataAsync
from httpx import ConnectError, HTTPStatusError
from structlog import get_logger

from bot.exceptions import DadataForbidden, DadataNoResult, DadataUnavailabilityError
from core.config import settings

logger = get_logger("dadata", service="dadata")


async def get_fields_from_dadata(data: str) -> dict[str, float | str]:
    async with DadataAsync(
        settings.DADATA_TOKEN,
        settings.DADATA_SECRET,
    ) as dadata:
        try:
            addresses = await dadata.suggest("address", data)
            address = addresses[0]

            if address["data"]["settlement_with_type"] is not None:
                city = address["data"]["settlement_with_type"]
            else:
                city = address["data"]["city_with_type"]

            full_address = address["unrestricted_value"]
            latitude = float(address["data"]["geo_lat"])
            longitude = float(address["data"]["geo_lon"])
        except (IndexError, TypeError):
            logger.info("Unsuccessful request(No result)", query=data)
            raise DadataNoResult
        except ConnectError:
            logger.error("Error connection to service")
            raise DadataUnavailabilityError
        except HTTPStatusError:
            logger.critical("403 Forbidden, check credentials or limits on service")
            raise DadataForbidden

        logger.info("Successful request", query=data, result=full_address)
        return dict(
            city=city,
            full_address=full_address,
            latitude=latitude,
            longitude=longitude,
        )

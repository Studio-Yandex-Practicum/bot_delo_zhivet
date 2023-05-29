from typing import Optional
from uuid import UUID

import boto3
from PIL import Image
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.const import QUALITY, TARGET_WIDTH
from src.bot.service.tags import check_pollution_tag_exists
from src.core.config import settings
from src.core.db.repository.pollution_repository import crud_pollution


class PollutionCreate(BaseModel):
    photo = str
    latitude = float
    longitude = float
    geometry = str
    comment = Optional[str]
    telegram_id = int
    ticketID = Optional[str]
    tag_id = Optional[UUID]

    class Config:
        arbitrary_types_allowed = True


async def create_new_pollution(
    data: PollutionCreate,
    session: AsyncSession,
):
    if "tag_id" in data:
        if not await check_pollution_tag_exists(data["tag_id"], session):
            data["tag_id"] = None
    new_pollution_problem = await crud_pollution.create(data, session)
    return new_pollution_problem


async def download_to_object_storage(file_path: str):
    session = boto3.session.Session()
    s3 = session.client(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        service_name=settings.AWS_SERVICE_NAME,
        endpoint_url=settings.AWS_ENDPOINT_URL,
    )
    s3.upload_file(file_path, settings.AWS_BUCKET_NAME, file_path[6:])


async def resize_downloaded_image(file_path):
    """Функция сжатия загружаемого изображения для экономии места."""
    image = Image.open(file_path)
    width, height = image.size
    resize_image = image.resize((int(TARGET_WIDTH), int(height / (width / TARGET_WIDTH))))
    return resize_image.save(file_path, optimize=True, quality=QUALITY)

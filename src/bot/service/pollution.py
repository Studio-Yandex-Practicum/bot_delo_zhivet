from typing import Optional

import boto3
from PIL import Image
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

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

    class Config:
        arbitrary_types_allowed = True


async def create_new_pollution(
    data: PollutionCreate,
    session: AsyncSession,
):
    new_social_problem = await crud_pollution.create(data, session)
    return new_social_problem


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
    target_width = 1000
    coefficient = width / target_width
    target_height = height / coefficient
    resize_image = image.resize((int(target_width), int(target_height)))
    return resize_image.save(file_path, optimize=True, quality=95)

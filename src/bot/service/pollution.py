from typing import Optional
from uuid import UUID

import boto3
from PIL import Image
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.const import QUALITY, TARGET_WIDTH
from src.bot.handlers.state_constants import (
    COMMENT, GEOM, LATITUDE, LONGITUDE, NO_COMMENT_PHASE, POLLUTION,
    POLLUTION_COMMENT, POLLUTION_FOTO, POLLUTION_TAGS, TAGS, TELEGRAM_ID,
)
from src.core.config import settings
from src.core.db.model import Pollution, Tag_Pollution
from src.core.db.repository.pollution_repository import crud_pollution
from src.core.db.repository.tags_repository import crud_tag_pollution


class PollutionCreate(BaseModel):
    photo = str
    latitude = float
    longitude = float
    geometry = str
    comment = Optional[str]
    telegram_id = int
    tags = Optional[list[UUID]]

    class Config:
        arbitrary_types_allowed = True


async def create_new_pollution(
    data: PollutionCreate,
    session: AsyncSession,
):
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


async def create_new_pollution_dict_from_data(user_id: int, data: dict, session: AsyncSession) -> dict:
    """Перекладывает данные из data в словарь который подходит для создания Pollution"""
    mandatory_fields: list[str] = [POLLUTION_FOTO, LATITUDE, LONGITUDE]
    new_pollution_dict: dict = {TELEGRAM_ID: user_id}
    for field in mandatory_fields:
        new_pollution_dict[field] = data[field]
    new_pollution_dict[GEOM] = f"POINT({data[LONGITUDE]} {data[LATITUDE]})"
    if POLLUTION_COMMENT in data:
        new_pollution_dict[COMMENT] = data[POLLUTION_COMMENT]
    if POLLUTION_TAGS in data:
        new_pollution_dict[TAGS]: list[Tag_Pollution] = await crud_tag_pollution.get_tags_list_from_tag_id_list(
            data[POLLUTION_TAGS], session
        )
    return new_pollution_dict


def create_new_pollution_message_for_tracker(pollution: Pollution, volunteers_description: str) -> dict:
    summary = f"{pollution.sender.telegram_username} - {pollution.latitude}, {pollution.longitude}"
    comment = pollution.comment if pollution.comment else NO_COMMENT_PHASE
    description = f"""
    Ник в телеграмме оставившего заявку: {pollution.sender.telegram_username}
    Координаты загрязнения: {pollution.latitude}, {pollution.longitude}
    Комментарий к заявке: {comment}
    {settings.AWS_ENDPOINT_URL}/{settings.AWS_BUCKET_NAME}/{pollution.photo[6:]}
    """
    description += volunteers_description
    return {
        "queue": POLLUTION,
        "summary": summary,
        "description": description,
        "tags": [str(tag) for tag in pollution.tags],
    }

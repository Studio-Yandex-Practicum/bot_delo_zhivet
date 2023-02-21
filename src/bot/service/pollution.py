import os
from typing import Optional

import boto3
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.repository.pollution_repository import crud_pollution

aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]
service_name = os.environ["AWS_SERVICE_NAME"]
endpoint_url = os.environ["AWS_ENDPOINT_URL"]
bucket_name = os.environ["AWS_BUCKET_NAME"]


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
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        service_name=service_name,
        endpoint_url=endpoint_url,
    )
    s3.upload_file(file_path, bucket_name, file_path[6:])

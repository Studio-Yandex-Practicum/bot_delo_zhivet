from yandex_tracker_client import TrackerClient

from core.config import settings

client = TrackerClient(token=settings.OAUTH_TOKEN, org_id=settings.ORG_ID)

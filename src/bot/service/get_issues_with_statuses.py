import os

from dotenv import load_dotenv
from yandex_tracker_client import TrackerClient

from bot.handlers.state_constants import POLLUTION, SOCIAL

load_dotenv()

client = TrackerClient(
    token=os.getenv("OAUTH_TOKEN"),
    org_id=os.getenv("ORG_ID")
)

def get_issues_with_statuses(
    queues=[POLLUTION, SOCIAL],
    statuses=['OPEN']  
):
    issues = client.issues.find(
        filter=dict(queue=queues, status=statuses)
    )
    return issues

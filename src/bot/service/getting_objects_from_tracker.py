from os import getenv

from dotenv import load_dotenv
from yandex_tracker_client import TrackerClient

load_dotenv()

client = TrackerClient(
    token=getenv('OAUTH_TOKEN'),
    org_id=getenv('ORG_ID')
)

issues = client.issues.find(
    filter={'queue': ["SOCIAL", "POLLUTION"], 'status': 'OPEN'}
)
descriptions = [issue.description for issue in issues]
print(descriptions[5])

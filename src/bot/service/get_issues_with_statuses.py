from datetime import date
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from yandex_tracker_client import TrackerClient

from src.bot.handlers.state_constants import POLLUTION, SOCIAL
from src.core.db.model import Volunteer
from src.core.db.repository.volunteer_repository import crud_volunteer

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


async def add_new_volunteer_to_issue(
    volunteer: Volunteer,
    session: AsyncSession
):
    format = "%d/%m/%Y"
    open_issues = get_issues_with_statuses()
    issues_in_radius = await crud_volunteer.get_issues_in_radius(
        volunteer.longitude, volunteer.latitude, volunteer.radius,
        session
    )
    for issue in open_issues:
        if issue.key in issues_in_radius:
            description = issue.description
            description += '\n' + date.today().strftime(
               format
            ) + " Найден новый волонтер " 
            description += 'c машиной' if volunteer.has_car else 'без машины'
            issue.update(description=description)

from src.core.db.model import Task
from src.core.db.repository.abstract_repository import CRUDBase

crud_task = CRUDBase(Task)

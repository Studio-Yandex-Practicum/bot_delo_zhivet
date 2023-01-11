from src.core.db.model import Volunteer
from src.core.db.repository.abstract_repository import CRUDBase

crud_user = CRUDBase(Volunteer)

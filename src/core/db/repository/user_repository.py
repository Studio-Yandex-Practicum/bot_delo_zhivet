from src.core.db.model import User
from src.core.db.repository.abstract_repository import CRUDBase

crud_user = CRUDBase(User)

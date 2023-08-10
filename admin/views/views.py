from flask_admin import Admin
import flask_login as login
from flask_admin.contrib import sqla
from flask_security import current_user
from structlog import get_logger
from .auth import MyAdminIndexView

from src.core.db.model import (
    Assistance_disabled,
    Pollution,
    Staff,
    Tag_Assistance,
    Tag_Pollution,
    User,
    Volunteer,
)

from .. import app
from ..database import db
from ..utils import (
    check_tag_uniqueness,
    get_readonly_dict,
    get_sortable_fields_list,
    get_table_fields_from_model,
    get_translated_labels,
)

logger = get_logger("admin_logger")


def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(staff_id):
        return db.session.query(Staff).get(staff_id)


init_login()


class BaseModelView(sqla.ModelView):
    """ Базовый вью-класс. """

    can_create = False
    can_delete = False
    page_size = 10

    def is_accessible(self):
        return (
            current_user.is_active
            and current_user.is_authenticated
            and (current_user.has_role("superuser") or current_user.has_role("admin"))
        )


class UserModelView(BaseModelView):
    """ Вью-класс пользователей. """

    all_columns = get_table_fields_from_model(User)

    column_exclude_list = ("password",)
    form_excluded_columns = ("password",)
    column_labels = get_translated_labels(all_columns)
    form_columns = (
        "telegram_username",
        "is_banned",
    )
    form_widget_args = {"telegram_username": {"readonly": True}}
    column_searchable_list = ("telegram_username",)


class StaffModelView(BaseModelView):
    """ Вью-класс администраторов. """

    all_columns = get_table_fields_from_model(Staff)
    column_exclude_list = ("password",)
    form_excluded_columns = ("password",)
    column_labels = get_translated_labels(all_columns)
    form_columns = (
        "login",
        "roles",
        "active",
    )
    form_widget_args = {"login": {"readonly": True}}

    def is_accessible(self):
        return current_user.is_active and current_user.is_authenticated and current_user.has_role("superuser")


class VolunteerModelView(BaseModelView):
    """ Вью-класс волонтеров. """

    all_columns = get_table_fields_from_model(Volunteer)
    form_columns = (
        "telegram_username",
        "first_name",
        "last_name",
        "full_address",
        "birthday",
        "is_banned",
    )
    column_labels = get_translated_labels(all_columns)
    form_widget_args = get_readonly_dict(
        (
            "telegram_username",
            "first_name",
            "last_name",
            "full_address",
        )
    )
    column_exclude_list = ("geometry",)
    column_searchable_list = ("telegram_username",)


class AssistanceDisabledModelView(BaseModelView):
    """ Вью-класс социальной помощи. """

    all_columns = get_table_fields_from_model(Assistance_disabled)
    column_labels = get_translated_labels(all_columns)
    sortable_relationship = {"tags": "tags.name"}
    column_list = all_columns
    column_sortable_list = get_sortable_fields_list(all_columns, sortable_relationship)
    column_filters = ("tags.name",)
    can_edit = False


class PollutionModelView(BaseModelView):
    """ Вью-класс загрязнения. """

    all_columns = get_table_fields_from_model(Pollution)
    column_labels = get_translated_labels(all_columns)
    sortable_relationship = {"tags": "tags.name"}
    column_list = all_columns
    column_sortable_list = get_sortable_fields_list(all_columns, sortable_relationship)
    column_filters = ("tags.name",)
    can_edit = False


class TagPollutionModelView(BaseModelView):
    """ Вью-класс тегов загрязнения. """

    all_columns = get_table_fields_from_model(Tag_Pollution)
    column_labels = get_translated_labels(all_columns)
    form_excluded_columns = ("created_at", "updated_at")
    can_edit = True
    can_create = True
    can_delete = True

    def on_model_change(self, form, model, is_created):
        if is_created:
            existing_tags = Tag_Pollution.query.all()
            check_tag_uniqueness(model, existing_tags)

        super().on_model_change(form, model, is_created)


class TagAssistanceModelView(BaseModelView):
    """ Вью-класс тегов соц. помощи. """

    all_columns = get_table_fields_from_model(Tag_Assistance)
    column_labels = get_translated_labels(all_columns)
    form_excluded_columns = ("created_at", "updated_at")
    can_edit = True
    can_create = True
    can_delete = True

    def on_model_change(self, form, model, is_created):
        if is_created:
            existing_tags = Tag_Assistance.query.all()
            check_tag_uniqueness(model, existing_tags)

        super().on_model_change(form, model, is_created)


BOOTSTRAP_VERSION = "bootstrap4"
ADMIN_NAME = "Бот «Дело живёт»"
BASE_TEMPLATE = "admin/index.html"
admin = Admin(
    app,
    template_mode=BOOTSTRAP_VERSION,
    name=ADMIN_NAME,
    index_view=MyAdminIndexView(name="Главная"),
    base_template=BASE_TEMPLATE,
)

MODALS_NAMES = {
    'staff': 'Персонал',
    'users': 'Пользователи',
    'volunteers': 'Волонтеры',
    'social_help': 'Социальная помощь',
    'pollution': 'Загрязнения',
    'tag_pollution': 'Теги загрязнения',
    'tag_assistance': 'Теги социальной помощи'
}
admin.add_view(
    StaffModelView(
        Staff,
        db.session,
        name=MODALS_NAMES['staff']
    )
)
admin.add_view(
    UserModelView(
        User,
        db.session,
        name=MODALS_NAMES['users']
    )
)
admin.add_view(
    VolunteerModelView(
        Volunteer,
        db.session,
        MODALS_NAMES['volunteers']
    )
)
admin.add_view(
    AssistanceDisabledModelView(
        Assistance_disabled,
        db.session,
        MODALS_NAMES['social_help']
    )
)
admin.add_view(
    PollutionModelView(
        Pollution,
        db.session,
        name=MODALS_NAMES['pollution']
    )
)
admin.add_view(
    TagPollutionModelView(
        Tag_Pollution,
        db.session,
        name=MODALS_NAMES['tag_pollution']
    )
)
admin.add_view(
    TagAssistanceModelView(
        Tag_Assistance,
        db.session,
        name=MODALS_NAMES['tag_assistance']
    )
)

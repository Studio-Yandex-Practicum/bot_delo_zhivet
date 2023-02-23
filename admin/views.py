import flask_admin
import flask_login as login
from flask import redirect, request, url_for
from flask_admin import AdminIndexView, expose, helpers
from flask_admin.contrib import sqla
from flask_security import current_user
from sqlalchemy.orm.attributes import InstrumentedAttribute
from werkzeug.security import generate_password_hash

from src.core.db.model import Assistance_disabled, Pollution, Staff, User, Volunteer

from . import app
from .database import db
from .forms import LoginForm, RegistrationForm

# Словарь для перевода полей
FIELD_TRANSLATION_RU = {
    "id": "id",
    "created_at": "Создан",
    "updated_at": "Изменен",
    "telegram_username": "Имя пользователя Telegram",
    "telegram_id": "ID пользователя Telegram",
    "is_banned": "Заблокирован",
    "first_name": "Имя",
    "last_name": "Фамилия",
    "city": "Город",
    "full_address": "Адрес",
    "radius": "Радиус активности",
    "has_car": "Есть машина",
    "latitude": "Широта",
    "longitude": "Долгота",
    "phone": "Номер телефона",
    "birthday": "День рождения",
    "deleted_at": "Удален",
    "ticketID": "ID тикета в Яндекс.Трекер",
    "geometry": "Координаты",
    "login": "Учетная запись",
    "email": "Электронная почта",
    "password": "Пароль",
    "comment": "Коментарий",
    "photo": "Фотография",
    "active": "Включен",
    "roles": "Роли",
}


def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(staff_id):
        return db.session.query(Staff).get(staff_id)


init_login()


def get_readonly_dict(fields):
    """
    Возвращает словарь для установки полей, перечисленных
    в параметре, в значение readonly для дальнейшей передачи
    в свойство form_widget_args вью-класса
    """
    readonly_fileds = dict()
    for field in fields:
        readonly_fileds[field] = {"readonly": True}
    return readonly_fileds


def get_translated_lables(fields):
    """Функция для перевода полей на русский язык"""
    labels = dict()
    for field in fields:
        labels[field] = FIELD_TRANSLATION_RU[field]
    return labels


def get_table_fields_from_model(model):
    """
    Функция для извлечения списка полей, отображаемых в админке,
    из модели
    """
    fields = []
    for field, value in dict(model.__dict__).items():
        if isinstance(value, InstrumentedAttribute):
            fields.append(field)
    return fields


class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for(".login_view"))
        return super(MyAdminIndexView, self).index()

    @expose("/login/", methods=("GET", "POST"))
    def login_view(self):
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for(".index"))
        link = (
            '<p>У Вас нет учетной записи? <a href="'
            + url_for(".register_view")
            + '">Нажмите здесь, чтобы зарегистрироваться</a></p>'
        )
        self._template_args["form"] = form
        self._template_args["link"] = link
        return super(MyAdminIndexView, self).index()

    @expose("/register/", methods=("GET", "POST"))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = Staff()

            form.populate_obj(user)
            user.password = generate_password_hash(form.password.data)

            db.session.add(user)
            db.session.commit()

            login.login_user(user)
            return redirect(url_for(".index"))
        link = '<p>Вы уже зарегистрированы? <a href="' + url_for(".login_view") + '">Нажмите здесь, чтобы войти</a></p>'
        self._template_args["form"] = form
        self._template_args["link"] = link
        return super(MyAdminIndexView, self).index()

    @expose("/logout/")
    def logout_view(self):
        login.logout_user()
        return redirect(url_for(".index"))


class BaseModelView(sqla.ModelView):
    """Базовый вью-класс"""

    can_create = False
    can_delete = False
    page_size = 10

    def is_accessible(self):
        return current_user.is_active and current_user.is_authenticated and current_user.has_role("admin")


class SuperuserModelView(BaseModelView):
    """Вью-класс суперпользователя"""

    column_exclude_list = ("password",)
    form_excluded_columns = ("password",)

    def is_accessible(self):
        return current_user.is_active and current_user.is_authenticated and current_user.has_role("superuser")


class StaffModelView(SuperuserModelView):
    """Вью-класс администраторов"""

    all_columns = get_table_fields_from_model(Staff)
    column_labels = get_translated_lables(all_columns)
    form_columns = (
        "login",
        "roles",
        "active",
    )
    form_widget_args = {"login": {"readonly": True}}


class UserModelView(SuperuserModelView):
    """Вью-класс пользователей"""

    all_columns = get_table_fields_from_model(User)
    column_labels = get_translated_lables(all_columns)
    form_columns = (
        "telegram_username",
        "is_banned",
    )
    form_widget_args = {"telegram_username": {"readonly": True}}
    column_searchable_list = ("telegram_username",)


class VolunteerModelView(BaseModelView):
    """Вью-класс волонтеров"""

    all_columns = get_table_fields_from_model(Volunteer)
    form_columns = (
        "telegram_username",
        "first_name",
        "last_name",
        "full_address",
        "birthday",
        "is_banned",
    )
    column_labels = get_translated_lables(all_columns)
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
    get_table_fields_from_model(Volunteer)

    def is_accessible(self):
        return (
            current_user.is_active
            and current_user.is_authenticated
            and (current_user.has_role("superuser") or current_user.has_role("admin"))
        )


class AssistanceDisabledModelView(BaseModelView):
    """Вью-класс социальной помощи"""

    all_columns = get_table_fields_from_model(Assistance_disabled)
    column_labels = get_translated_lables(all_columns)
    can_edit = False


class PolutionModelView(BaseModelView):
    """Вью-класс загрязнения"""

    all_columns = get_table_fields_from_model(Pollution)
    column_labels = get_translated_lables(all_columns)
    can_edit = False


admin = flask_admin.Admin(
    app,
    "Bot delo zhivet : Admin console",
    index_view=MyAdminIndexView(name="Главная"),
    base_template="my_master.html",
    template_mode="bootstrap4",
)

admin.add_view(StaffModelView(Staff, db.session, name="Администраторы"))
admin.add_view(UserModelView(User, db.session, name="Пользователи"))

admin.add_view(VolunteerModelView(Volunteer, db.session, name="Волонтеры"))
admin.add_view(AssistanceDisabledModelView(Assistance_disabled, db.session, name="Социальная помощь"))
admin.add_view(PolutionModelView(Pollution, db.session, name="Загрязнения"))

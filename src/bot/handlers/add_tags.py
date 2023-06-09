import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.bot.handlers.common import handle_invalid_button
from src.bot.handlers.pollution import (
    back_to_select_option_to_report_about_pollution,
)
from src.bot.handlers.social import back_to_add_social
from src.bot.handlers.state_constants import (
    ADD_POLLUTION_TAG, ADD_SOCIAL_TAG, BACK, CHECK_MARK, CURRENT_FEATURE,
    FEATURES, NO_TAG, POLLUTION_TAGS, SOCIAL_TAGS, TAG_BUTTON_CALLBACK_PREFIX,
    TAG_ID, TAG_ID_PATTERN,
)
from src.bot.service.tags import get_chosen_tags_names
from src.core.config import settings
from src.core.db.db import get_async_session
from src.core.db.repository.tags_repository import (
    AbstractTag, TagCRUD, crud_tag_assistance, crud_tag_pollution,
)


class TagsHandlerClass:
    """Класс для создания хендлера для выбора тегов."""

    def __init__(
        self,
        crud_tag: TagCRUD,
        entry_point=ADD_POLLUTION_TAG or ADD_SOCIAL_TAG,
        tag_storage_name=POLLUTION_TAGS or SOCIAL_TAGS,
        back_to_select_callback=back_to_select_option_to_report_about_pollution or back_to_add_social,
    ) -> None:
        self.entry_point = entry_point
        self.tag_storage_name = tag_storage_name
        self.crud_tag = crud_tag
        self.back_to_select_callback = back_to_select_callback
        self.problem_name = "экологическая" if entry_point == ADD_POLLUTION_TAG else "социальная"
        self.text = f"Выберите, к какому типу относится {self.problem_name} проблема.\n"

    async def enter_tags(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Хендлер для обработки как первого входа в выбор тегов, так и всех нажатий кнопок с тегами."""
        if not await self._on_enter_checks(update, context):
            return await handle_invalid_button(update, context)

        await update.callback_query.answer()

        chosen_tags_ids_list = context.user_data[FEATURES][self.tag_storage_name]
        all_tags_list = await self._get_tags_from_db()
        all_tags_ids_list = [str(tag.id) for tag in all_tags_list]

        chosen_tag = re.match(TAG_ID_PATTERN, update.callback_query.data)
        if chosen_tag and chosen_tag.group(TAG_ID):
            chosen_tags_ids_list = self._update_chosen_tags(
                chosen_tag.group(TAG_ID), chosen_tags_ids_list, all_tags_ids_list
            )
        # обновим сообщение
        text = self.text
        if chosen_tags_ids_list:
            text += f"Вы уже выбрали {get_chosen_tags_names(all_tags_list, chosen_tags_ids_list)}"
        else:
            text += "Вы пока ничего не выбрали."
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=self._build_tags_keyboard(all_tags_list, chosen_tags_ids_list),
        )
        return self.entry_point

    async def no_tag(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Хендлер кнопки очистки тегов."""
        context.user_data[FEATURES][self.tag_storage_name] = []
        chosen_tags_ids_list = []

        all_tags_list = await self._get_tags_from_db()
        await update.callback_query.edit_message_text(
            text=self.text,
            reply_markup=self._build_tags_keyboard(all_tags_list, chosen_tags_ids_list),
        )
        return self.entry_point

    async def exit_tags(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Выход из тегов. Если список выбраных тегов пустой, то он удаляется."""
        if (
            self.tag_storage_name in context.user_data[FEATURES]
            and not context.user_data[FEATURES][self.tag_storage_name]
        ):
            context.user_data[FEATURES].pop(self.tag_storage_name, None)
        return await self.back_to_select_callback(update, context)

    async def _on_enter_checks(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Убедится что в context.user_data есть нужные ключи."""
        # если FEATURES нет в user_data, значит что то не так
        if FEATURES not in context.user_data:
            return False

        if update.callback_query.data == self.entry_point:
            context.user_data[CURRENT_FEATURE] = self.entry_point

        # если в user_data FEATURES нет списка для тегов создадим его
        if self.tag_storage_name not in context.user_data[FEATURES]:
            context.user_data[FEATURES][self.tag_storage_name] = []
        return True

    async def _get_tags_from_db(self) -> list:
        """Получает список тегов их базы в заданом порядке."""
        session_generator = get_async_session()
        session = await session_generator.asend(None)
        return await self.crud_tag.get_all_sorted_by_attribute(settings.sort_tags_in_bot, session)

    def _update_chosen_tags(self, chosen_tag: str, chosen_tags_ids_list: list[str], all_tags_ids_list: list[str]):
        """Проверяет что chosen_tag есть в all_tags_ids_list
        Сохраняет или удаляет chosen_tag в/из chosen_tags_ids_list"""
        if chosen_tag in all_tags_ids_list:
            if chosen_tag not in chosen_tags_ids_list:
                chosen_tags_ids_list.append(chosen_tag)
            else:
                chosen_tags_ids_list.remove(chosen_tag)
        return chosen_tags_ids_list

    def _build_tags_keyboard(
        self, all_tags_list: list[AbstractTag], chosen_tags_ids_list: list
    ) -> InlineKeyboardMarkup:
        """Создает список кнопочек с тегами."""

        def check_tag_is_added(tag_id, tag_ids_list: list) -> bool:
            return str(tag_id) in tag_ids_list

        tags_buttons_list: list[InlineKeyboardButton] = [
            InlineKeyboardButton(
                text=f"{str(tag.name)} {CHECK_MARK*check_tag_is_added(tag.id, chosen_tags_ids_list)}",
                callback_data=TAG_BUTTON_CALLBACK_PREFIX + str(tag.id),
            )
            for tag in all_tags_list
        ]
        no_tags_button = InlineKeyboardButton(text="Очистить", callback_data=NO_TAG)
        go_back_button = InlineKeyboardButton(text="Сохранить и вернуться назад", callback_data=BACK)
        tags_buttons_list.append(no_tags_button)
        tags_buttons_list.append(go_back_button)
        return InlineKeyboardMarkup.from_column(tags_buttons_list)


pollution_tags_handler = TagsHandlerClass(
    crud_tag_pollution, ADD_POLLUTION_TAG, POLLUTION_TAGS, back_to_select_option_to_report_about_pollution
)

social_tags_handler = TagsHandlerClass(crud_tag_assistance, ADD_SOCIAL_TAG, SOCIAL_TAGS, back_to_add_social)

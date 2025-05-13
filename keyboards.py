from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_start_keyboard():
    # Создаём инлайн клавиатуру
    keyboard = InlineKeyboardMarkup(row_width=1)  # 2 кнопки в строке

    # Кнопки
    products_button = InlineKeyboardButton("🛒 Товары", callback_data="products", url="https://ebsh.taplink.ws/")
    gift_button = InlineKeyboardButton("🎁 Получить подарок", callback_data="gift")
    support_button = InlineKeyboardButton("💬 Поддержка", callback_data="support")
    # dialog = InlineKeyboardButton("👤 Поговорить с человеком", callback_data="human")

    # Добавляем кнопки на клавиатуру
    keyboard.add(gift_button, products_button, support_button)

    return keyboard


def get_questions_keyboard():
    """Клавиатура для вопросов и отмены."""
    ask_button = InlineKeyboardButton(text="✍️ Задать вопрос", callback_data="ask_question")
    back_button = InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
    keyboard = InlineKeyboardMarkup().add(ask_button).add(back_button)
    return keyboard
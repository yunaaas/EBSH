from aiogram.dispatcher.filters.state import State, StatesGroup

class UserStates(StatesGroup):
    asking_question = State()
    waiting_for_message = State()


class GiftState(StatesGroup):
    waiting_for_photo = State()  # Ожидаем фото
    waiting_for_phone = State()  # Ожидаем номер телефона
    waiting_for_bank_name = State()  # Ожидаем название банка
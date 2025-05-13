from aiogram import types
from aiogram.types import ContentType
from aiogram.types import ParseMode
from keyboards import *  # Импортируем вашу клавиатуру
from users import *  # Импортируем базу данных пользователей
from states import *  # Если нужно использовать состояния
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from config import API_TOKEN
from states import *
from config import admins
from config import ya_token

text = '''
<b>Добро пожаловать</b> в мир <i>стильной</i> и современной одежды! 

Мы — молодой и динамично развивающийся бренд, для которого важнейшими ценностями являются <u>качество</u>, <u>удобство</u> и <u>стиль</u> 😎

<b>Спасибо</b>, что обратились к нам! 😊

Пожалуйста, выберите нужный раздел в меню ниже. 📲
'''

user_db = UserDB()


async def reset_state(message: types.Message, state: FSMContext):
    """Сбрасываем состояние пользователя и отправляем сообщение."""
    await state.finish()  # Завершаем текущее состояние пользователя
    await message.reply("Состояние сброшено. Нажмите /start, чтобы начать заново.")


async def cmd_start(message: types.Message):
    user = message.from_user

    # Проверяем и добавляем пользователя в базу данных, если его нет
    user_db.add_user_if_not_exists(user.id, user.first_name, user.last_name, user.username)

    # Получаем инлайн клавиатуру
    keyboard = get_start_keyboard()

    # Отправляем сообщение
    await message.answer(text = f"Здравствуйте, {user.first_name}\n{text}", parse_mode=ParseMode.HTML, reply_markup=keyboard)


# # Обработчик для кнопки "Товары"
# async def products_handler(callback_query: types.CallbackQuery):
#     await callback_query.message.edit_text("Вы выбрали раздел: 🛒 Товары\nЗдесь вы можете ознакомиться с нашим ассортиментом. Выберите нужный товар.")


# # Обработчик для кнопки "Получить подарок"
# async def gift_handler(callback_query: types.CallbackQuery):
#     await callback_query.message.edit_text("Вы выбрали раздел: 🎁 Получить подарок\nПодарки для вас ждут! Напишите свой запрос или выберите подарок.")


# Обработчик для кнопки "Поддержка"
async def support_handler(callback_query: types.CallbackQuery):
    keyboard = get_questions_keyboard()
    await callback_query.message.edit_text(
        "💬 Вы выбрали раздел: Поддержка\nНаши специалисты готовы помочь. Напишите вашу проблему в чат или задайте вопрос."
    )



    await callback_query.message.edit_reply_markup(reply_markup=keyboard)


# Обработчик для кнопки "Отменить"
async def cancel_question(callback_query: types.CallbackQuery, state: FSMContext):
    """Отмена вопроса и возврат в меню вопросов."""
    await callback_query.message.edit_text(
        "💬 Вы выбрали раздел: Поддержка\nНаши специалисты готовы помочь. Напишите вашу проблему в чат или задайте вопрос.", 
        reply_markup=get_questions_keyboard(), 
        parse_mode=ParseMode.HTML
    )
    # Завершаем состояние
    await state.finish()

async def support_handler(callback_query: types.CallbackQuery):
    """Обрабатываем раздел 'Поддержка'."""
    await callback_query.message.edit_text(
        "💬 Вы выбрали раздел: Поддержка\nНаши специалисты готовы помочь. Напишите вашу проблему в чат или задайте вопрос."
    )
    await callback_query.answer("Бежим смотреть ваш вопрос! 👀")
    ask_button = InlineKeyboardButton(text="✍️ Задать вопрос", callback_data="ask_question")
    back_button = InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
    keyboard = InlineKeyboardMarkup().add(ask_button).add(back_button)

    await callback_query.message.edit_reply_markup(reply_markup=keyboard)


async def ask_own_question(callback_query: types.CallbackQuery, state: FSMContext):
    """Запрашиваем у пользователя вопрос и даём кнопку отмены."""
    await callback_query.message.edit_text(
        "Напишите ваш вопрос или прикрепите фото/видео. Наша команда увидит его и ответит как можно скорее! 💌"
    )
    await callback_query.answer("Ждем ваш вопрос! ⏳")
    cancel_button = InlineKeyboardButton(text="🙈 Я нажал сюда случайно", callback_data="cancel_question")
    keyboard = InlineKeyboardMarkup().add(cancel_button)

    await callback_query.message.edit_reply_markup(reply_markup=keyboard)

    # Устанавливаем состояние для получения вопроса
    await state.set_state(UserStates.asking_question)


async def cancel_question(callback_query: types.CallbackQuery, state: FSMContext):
    """Отмена вопроса и возврат в главное меню."""
    await state.finish()  # Завершаем состояние
    await callback_query.answer("Вопрос отменён! ❌")
    # Отправляем сообщение о возврате в главное меню
    await callback_query.message.edit_text(
        f"Вы вернулись в главное меню. {text}", parse_mode=ParseMode.HTML,
        reply_markup=get_start_keyboard()  # Возвращаем клавиатуру главного меню
    )


async def handle_question(message: types.Message, state: FSMContext):
    """Обрабатываем отправку вопроса и пересылаем его администраторам."""
    if await state.get_state() == UserStates.asking_question.state:
        user = message.from_user

        # Пересылаем вопрос всем администраторам
        for admin_id in admins:
            await message.forward(chat_id=admin_id)

            # Отправляем информацию о пользователе администратору
            await message.bot.send_message(
                chat_id=admin_id,
                text=f"ВОПРОС!!!\n\nОт: {user.first_name} {user.last_name} @{user.username}, \n<code>|send |{user.id}|</code>",
                parse_mode=ParseMode.HTML
            )

        # Отправляем ответ пользователю
        await message.answer("Ваш вопрос принят! Мы ответим вам как можно скорее. 💌", reply_markup=get_start_keyboard())

        # Завершаем состояние
        await state.finish()


from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType
from states import UserStates

# Обработчик для раздела "Поговорить с человеком"
async def human_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """Обрабатываем раздел 'Поговорить с человеком'."""
    
    # Ответ пользователю
    await callback_query.answer("Уже ищем человека для вас! 👀")

    # Запрашиваем у пользователя сообщение
    await callback_query.message.edit_text("📝 Напишите ваш вопрос или сообщение, и мы передадим его специалисту.", parse_mode=ParseMode.HTML)
    
    # Переходим к состоянию для получения сообщения от пользователя
    await state.set_state(UserStates.waiting_for_message)
    
    # Добавляем кнопку "Назад"
    back_button = InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
    keyboard = InlineKeyboardMarkup().add(back_button)
    
    # Редактируем клавиатуру
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)


# Обработчик для кнопки "Назад"
async def back_to_main(callback_query: types.CallbackQuery, state: FSMContext):
    """Возвращаем пользователя в главное меню, независимо от состояния."""
    
    # Завершаем состояние и возвращаем в главное меню
    await state.finish()
    
    # Отправляем сообщение о возврате в главное меню
    await callback_query.answer("Возвращаемся в главное меню! 😁")
    await callback_query.message.edit_text(
        "Вы вернулись в главное меню.",
        reply_markup=get_start_keyboard(),  # Возвращаем клавиатуру главного меню
        parse_mode=ParseMode.HTML
    )


# Обработчик для получения сообщения от пользователя
async def handle_user_message(message: types.Message, state: FSMContext):
    """Обрабатываем сообщение пользователя и отправляем его администратору."""
    
    if await state.get_state() == UserStates.waiting_for_message.state:
        user = message.from_user
        user_message = message.text.strip()  # Сообщение пользователя
        
        # Пересылаем сообщение администратору
        for admin_id in admins:
            await message.bot.send_message(
                chat_id=admin_id,
                text=f"Новый запрос на общение от пользователя {user.first_name} {user.last_name} (@{user.username}):\n\n{user_message}\n\nВы можете написать ему лично нажав сюда — \n(@{user.username}), или использовать — \n<code>|send |{user.id}|</code>",
                parse_mode=ParseMode.HTML
            )

        # Ответ пользователю
        await message.answer("Ваш запрос принят! Наши специалисты скоро с вами свяжутся. 💬", reply_markup=get_start_keyboard())
        
        # Завершаем состояние
        await state.finish()





# Обработчик для возврата в главное меню
async def process_back_to_main(callback_query: types.CallbackQuery):
    """Возвращаем пользователя в главное меню."""
    keyboard = get_start_keyboard()  # Клавиатура главного меню
    await callback_query.answer("Возвращаемся назад 😁")
    await callback_query.answer()
    await callback_query.message.edit_text(text=f"Вы вернулись в главное меню! {text}", reply_markup=keyboard, parse_mode=ParseMode.HTML)


async def gift_handler(callback_query: types.CallbackQuery, state: FSMContext):
    # Создаем клавиатуру с кнопками
    keyboard = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("🎁 Получить подарок", callback_data="conditions_accepted"),
        InlineKeyboardButton("🔙 Вернуться назад", callback_data="main_menu")
    )
    await callback_query.answer("Один момент! 🔄")
    # Редактируем сообщение с условиями
    await callback_query.message.edit_text(
        "Уважаемый <b>Покупатель</b>, просим обратить внимание! Чтобы условия были выполнены, при оценке товара необходимо <b>обязательно написать текстовый отзыв</b>.\n\n"
        "<b>Важно:</b> Для получения подарка, отзыв должен быть с <b>оценкой 5 звезд</b> с <b>фотографиями</b> или <b>видео</b>\n\n"
        "<b>Шаги:</b>\n"
        "1. Откройте приложение маркетплейса на телефоне.\n"
        "2. Нажмите на иконку профиля.\n"
        "3. Выберите категорию <i>«Покупки»</i>.\n"
        "4. Выберите товар, на который хотите оставить отзыв.\n"
        "5. Найдите строчку <i>«Отзывы»</i>, обычно она под описанием товара.\n"
        "6. Нажмите кнопку <i>«Оставить отзыв»</i>.\n"
        "7. Напишите, чем Вам понравился наш товар, <b>обязательно прикрепите фото</b>.\n\n"
        "<b>Пожалуйста, убедитесь, что вы выполнили все условия, чтобы получить подарок!</b>",
        reply_markup=keyboard, parse_mode=ParseMode.HTML
    )


# Обработчик для кнопки "Получить подарок"
from aiogram.types import ContentType, ParseMode, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types

# Обработчик для кнопки "Получить подарок"
async def conditions_accepted(callback_query: types.CallbackQuery, state: FSMContext):
    # Переходим к запросу номера телефона
    await callback_query.answer("Мы начинаем! ✅")
    await callback_query.message.edit_text(
        "<b>Вы выбрали раздел:\n</b> 🎁 <i>Получить подарок</i>\n\n"
        "<b>Пожалуйста, отправьте ваш номер телефона.</b> 📱"
        "\n\n<i>Мы ждем ваш номер для получения подарка!</i> 💌",
        parse_mode=ParseMode.HTML
    )

    # Создаем клавиатуру с кнопкой для отправки номера телефона
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton("Отправить номер телефона 📱", request_contact=True)
    )

    # Переходим к шагу запроса номера телефона
    await state.set_state(GiftState.waiting_for_phone)
    await callback_query.message.answer(
        "<b>Пожалуйста, отправьте свой номер телефона, используя кнопку ниже.</b>",
        reply_markup=keyboard,  # Клавиатура с кнопкой для отправки контакта
        parse_mode=ParseMode.HTML
    )


# Обработчик для получения номера телефона
async def handle_phone(message: types.Message, state: FSMContext):
    if message.contact:
        # Сохраняем номер телефона
        phone_number = message.contact.phone_number
        await state.update_data(phone_number=phone_number)
        user = message.from_user
        user_db.set_dr(user.id, phone_number)
        # Создаем клавиатуру с кнопкой для запроса фото
        # keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(
        #     KeyboardButton("Отправить фото 📸")
        # )

        # Переходим ко второму шагу — запрос фото
        await state.set_state(GiftState.waiting_for_photo)
        await message.answer(
            "<b>Спасибо за номер телефона!</b> 📱 \n<i>Теперь отправьте фото вашего отзыва.</i>", 
            reply_markup=ReplyKeyboardRemove(),
            # reply_markup=keyboard,  # Клавиатура с кнопкой для отправки фото
            parse_mode=ParseMode.HTML
        )
    else:
        await message.answer(
            "<b>Вы отправили неверный формат.</b> ❌ \n<i>Пожалуйста, отправьте свой номер телефона через кнопку ниже.</i> 📲",
            parse_mode=ParseMode.HTML
        )


# Обработчик для получения фото
async def handle_photo(message: types.Message, state: FSMContext):
    if message.content_type == ContentType.PHOTO:
        # Сохраняем фото в контексте состояния
        await state.update_data(photo=message.photo[-1].file_id)

        # Сбор всех данных
        user_data = await state.get_data()
        photo_id = user_data['photo']
        phone_number = user_data['phone_number']
        
        # Формируем сообщение для администратора
        admin_message = (
            f"<b>Подарок за отзыв!</b>\n\n"
            f"<b>Номер телефона:</b> {phone_number}\n"
            f"От: {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}, \n<code>|send |{message.from_user.id}|</code>"
        )

        # Отправляем фото с номером телефона админу
        for admin_id in admins:
            await message.bot.send_photo(
                admin_id, 
                photo_id,  # Отправляем фото с использованием file_id
                caption=admin_message,  # Сообщение с данными
                parse_mode=ParseMode.HTML
            )

        # Клавиатура с кнопками для перехода в меню
        keyboard = InlineKeyboardMarkup(row_width=1)
        button1 = InlineKeyboardButton("🔙 В главное меню", callback_data="main_menu")
        button2 = InlineKeyboardButton("🛒 Посмотреть другие товары", callback_data="view_other_products", url="https://ebsh.taplink.ws/")
        keyboard.add(button2, button1)

        # Отправляем ответ пользователю
        await message.answer(
            "Ваш запрос на подарок принят! Мы проверим ваши данные и свяжемся с вами в течении 48 часов. 💌\nПока идет проверка, вы можете ознакомиться с другими нашими товарами!",
            reply_markup=keyboard
        )

        # Завершаем состояние
        await state.finish()

    else:
        # Если сообщение не фото, отправляем предупреждение
        await message.answer(
            "<b>Кажется, это не фото.</b> ❌ \n<i>Пожалуйста, отправьте фото вашего отзыва.</i> 📸",
            parse_mode=ParseMode.HTML
        )






# Регистрация хэндлеров
def register_user_handlers(dp):
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_callback_query_handler(support_handler, lambda c: c.data == "support")
    dp.register_callback_query_handler(ask_own_question, lambda c: c.data == "ask_question")
    dp.register_callback_query_handler(cancel_question, lambda c: c.data == "cancel_question", state=UserStates.asking_question)
    dp.register_message_handler(handle_question, content_types=["any"], state=UserStates.asking_question)
    dp.register_callback_query_handler(process_back_to_main, lambda c: c.data == "main_menu")
    dp.register_callback_query_handler(gift_handler, lambda c: c.data == "gift")
    dp.register_callback_query_handler(conditions_accepted, lambda c: c.data == "conditions_accepted")
    dp.register_message_handler(handle_photo, content_types=types.ContentType.ANY, state=GiftState.waiting_for_photo)
    dp.register_message_handler(handle_phone, content_types=types.ContentType.ANY, state=GiftState.waiting_for_phone)
    # dp.register_message_handler(handle_bank_name, state=GiftState.waiting_for_bank_name)
    dp.register_callback_query_handler(human_handler, lambda c: c.data == 'human')  # Обработчик для 'Поговорить с человеком'
    dp.register_message_handler(handle_user_message, content_types=types.ContentType.TEXT, state=UserStates.waiting_for_message)  # Обработчик для получения сообщений
    dp.register_callback_query_handler(back_to_main, lambda c: c.data == "back_to_main", state=UserStates.waiting_for_message)
    dp.register_message_handler(reset_state, commands=["reset"], state="*")  # Этот хэндлер сбросит все состояния
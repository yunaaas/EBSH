import asyncio
import datetime

from aiogram import types
from aiogram.types import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from users import *
from config import *
from aiogram import Dispatcher
from aiogram import Bot
from config import *
from admins import *

user_db = UserDB()
admin_db = AdminDB()

async def cmd_admin(message: types.Message):
    """Обрабатываем команду добавления администратора."""
    
    # Разделяем команду по символу '|'
    msg_parts = message.text.split("|")
    print(msg_parts)
    # Проверка правильности формата
    if len(msg_parts) < 4:  # Формат: |admin |id| |name| |comment|
        await message.reply("Неверный формат команды. Используйте: |admin |id| |name| |comment|")
        return

    try:
        # Извлекаем данные
        admin_id = int(msg_parts[2].strip())  # ID администратора (извлекаем и преобразуем в целое число)
        name = msg_parts[4].strip()  # Имя администратора
        comment = msg_parts[6].strip()  # Комментарий (может быть пустым)

        # Добавляем администратора в базу данных
        admin_db.add_admin(admin_id, name, comment)
        
        # Отправляем подтверждение
        await message.reply(f"Администратор с ID {admin_id} успешно добавлен! 🟢")
    except ValueError:
        await message.reply("Ошибка в ID администратора. Он должен быть целым числом.")



async def cmd_send_message(message: types.Message):
    if message.from_user.id in admins:  # Проверка, что это администратор
        # Разделяем сообщение по символу '|'
        msg_parts = message.text.split("|")
        
        if len(msg_parts) < 3:  # Проверяем, что есть достаточно параметров
            await message.reply("<b>Неверный формат команды.</b> Используйте: <code>|send |id| сообщение</code>", parse_mode=ParseMode.HTML)
            return
    
        target = msg_parts[2].strip()  # ID пользователя или 'all'
        text_message = msg_parts[3].strip()  # Сообщение
    
        if target == "all":  # Если рассылка всем
            data = user_db.get_id()  # Получаем всех пользователей
            for user_id in data:
                try:
                    await bot.send_message(chat_id=user_id[0], text=f"<b>Важное сообщение!</b>\n\n{text_message}\n\nС уважением, <b>команда EBSH</b>🫂", parse_mode=ParseMode.HTML)
                    await asyncio.sleep(1)
                except Exception as e:
                    continue
                
            await bot.send_message(message.from_user.id, text=f"<b>Сообщение отправлено всем пользователям.</b>", parse_mode=ParseMode.HTML)
            
            # Отправляем лог главному администратору
            main_admin_id = main_admin  # Замените на ID главного администратора
            await bot.send_message(main_admin_id, f"<i>Сообщение:</i> <b>'{text_message}'</b> \nБыло отправлено <b>всем</b> пользователям.", parse_mode=ParseMode.HTML)
    
        else:
            if user_db.get_user(target):  # Проверяем, есть ли пользователь с таким ID
                await bot.send_message(message.from_user.id, text=f"<b>Сообщение отправлено пользователю {target}.</b>", parse_mode=ParseMode.HTML)
                await bot.send_message(chat_id=target, text=f"<b>Важное сообщение!</b>\n\n{text_message}\n\nС уважением, <b>команда EBSH</b>🫂", parse_mode=ParseMode.HTML)
                
                # Отправляем лог главному администратору
                main_admin_id = main_admin  # Замените на ID главного администратора
                await bot.send_message(main_admin_id, f"<i>Сообщение:</i> <b>'{text_message}'</b> \nБыло отправлено пользователю с <b>ID {target}.</b>", parse_mode=ParseMode.HTML)
    
            else:
                await bot.send_message(message.from_user.id, text="<b>Пользователь не найден.</b>", parse_mode=ParseMode.HTML)
                
                # Отправляем лог главному администратору, если пользователь не найден
                main_admin_id = main_admin  # Замените на ID главного администратора
                await bot.send_message(main_admin_id, f"<b>Попытка отправить сообщение пользователю с ID {target}, но пользователь не найден.</b>", parse_mode=ParseMode.HTML)
    
    else:
        await bot.send_message(message.from_user.id, text="<b>У вас нет прав для отправки сообщений.</b>", parse_mode=ParseMode.HTML)
        
        # Отправляем лог главному администратору, если не администратор
        main_admin_id = main_admin  # Замените на ID главного администратора
        await bot.send_message(main_admin_id, f"<b>Попытка неавторизованного доступа от пользователя {message.from_user.id}.</b>", parse_mode=ParseMode.HTML)


# Обработчик для кнопки "👑 Администраторы"
async def admin_data_handler(callback_query: types.CallbackQuery):
    """Обрабатываем нажатие на кнопку '👑 Администраторы'."""
    # Создаем кнопку для просмотра администраторов
    view_button = InlineKeyboardButton("👀 Посмотреть администраторов", callback_data="view_admins")
    back_button = InlineKeyboardButton("🔙 Назад", callback_data="admin_main_menu")  # Кнопка для возврата в главное меню

    # Создание клавиатуры
    keyboard = InlineKeyboardMarkup().add(view_button).add(back_button)

    # Редактируем сообщение с новыми кнопками
    await callback_query.message.edit_text(
        "👑 Вы выбрали раздел: Администраторы\nВыберите действие:",
        reply_markup=keyboard
    )

# Обработчик для кнопки "Посмотреть администраторов"
async def view_admins_handler(callback_query: types.CallbackQuery):
    """Обрабатываем запрос на просмотр всех администраторов."""
    admins = admin_db.get_all_admins()  # Получаем всех администраторов из базы данных

    if admins:
        # Создаем клавиатуру с кнопками для каждого администратора
        keyboard = InlineKeyboardMarkup(row_width=1)

        # Добавляем кнопки для каждого администратора
        for admin in admins:
            admin_id, name, comment, date_added = admin
            admin_button = InlineKeyboardButton(f"{name} (ID: {admin_id})", callback_data=f"admin_{admin_id}")
            keyboard.add(admin_button)

        # Кнопка для возврата
        back_button = InlineKeyboardButton("🔙 Назад", callback_data="admin_data")
        keyboard.add(back_button)

        # Редактируем сообщение с результатами
        await callback_query.message.edit_text(
            "📜 Список администраторов:\nВыберите администратора для получения информации:",
            reply_markup=keyboard
        )
    else:
        await callback_query.message.edit_text(
            "❌ Нет администраторов в базе данных.",
            reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Назад", callback_data="admin_data"))
        )

# Обработчик для получения информации об администраторе и кнопок "Удалить" и "Назад"
async def show_admin_info(callback_query: types.CallbackQuery):
    """Отправляем информацию о выбранном администраторе с кнопками для удаления и возврата."""
    admin_id = int(callback_query.data.split('_')[1])  # Извлекаем ID администратора из callback_data
    admin = admin_db.get_admin_by_id(admin_id)

    if admin:
        admin_id, name, comment, date_added = admin
        # Формируем информацию об администраторе
        message = f"<b>Администратор</b>: {name}\n"
        message += f"<b>ID</b>: {admin_id}\n"
        message += f"<b>Комментарий</b>: {comment if comment else 'Нет комментария'}\n"
        message += f"<b>Дата добавления</b>: {date_added}"

        # Кнопки для удаления и возврата
        delete_button = InlineKeyboardButton("🗑️ Удалить администратора", callback_data=f"delete_{admin_id}")
        back_button = InlineKeyboardButton("🔙 Назад", callback_data="view_admins")

        keyboard = InlineKeyboardMarkup().add(delete_button).add(back_button)

        # Отправляем информацию
        await callback_query.message.edit_text(message, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    else:
        await callback_query.message.edit_text("❌ Администратор не найден.", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Назад", callback_data="admin_data")))

async def delete_admin_handler(callback_query: types.CallbackQuery):
    """Удаляем администратора из базы данных и возвращаем в главное меню администратора."""
    admin_id = int(callback_query.data.split("_")[1])  # Извлекаем ID администратора из callback_data

    # Удаляем администратора из базы данных
    admin_db.delete_admin(admin_id)

    # Ответ на действие
    await callback_query.answer(f"✅ Администратор с ID {admin_id} был удален.")
    help_button = InlineKeyboardButton("💬 Помощь", callback_data="help")
    clients_button = InlineKeyboardButton("👥 Клиенты", callback_data="clients")
    export_button = InlineKeyboardButton("📊 Выгрузить данные на диск", callback_data="export_data")
    admin_button = InlineKeyboardButton("👑 Администраторы", callback_data="admin_data")

    # Кнопка для возврата в главное меню
    keyboard = InlineKeyboardMarkup(row_width=2).add(help_button, clients_button).row(export_button).row(admin_button)
    # Редактируем сообщение, чтобы показать главное меню администратора
    await callback_query.message.edit_text("👑 Вы в главном меню администратора. Выберите действие:", reply_markup=keyboard)

# async def send_admin_menu(message: types.Message):
#     """Редактируем сообщение с меню администратора с кнопками."""
#     help_button = InlineKeyboardButton("💬 Помощь", callback_data="help")
#     clients_button = InlineKeyboardButton("👥 Клиенты", callback_data="clients")
#     export_button = InlineKeyboardButton("📊 Выгрузить данные на диск", callback_data="export_data")
#     admin_button = InlineKeyboardButton("👑 Администраторы", callback_data="admin_data")

#     # Кнопка для возврата в главное меню
#     keyboard = InlineKeyboardMarkup().add(help_button).add(clients_button).add(export_button).add(admin_button)

#     # Редактируем сообщение, которое вызвало данное действие
#     await message.edit_text("👑 Вы в главном меню администратора. Выберите действие:", reply_markup=keyboard)



async def back_to_main(callback_query: types.CallbackQuery):
    """Возвращаем пользователя в главное меню администратора."""
    
    # Создаем кнопки заново внутри обработчика
    help_button = InlineKeyboardButton("💬 Помощь", callback_data="help")
    clients_button = InlineKeyboardButton("👥 Клиенты", callback_data="clients")
    export_button = InlineKeyboardButton("📊 Выгрузить данные на диск", callback_data="export_data")
    admin_button = InlineKeyboardButton("👑 Администраторы", callback_data="admin_data")
    
    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(row_width=2).add(help_button, clients_button).row(export_button).row(admin_button)
    
    # Редактируем сообщение и добавляем клавиатуру
    await callback_query.message.edit_text(
        "👑 Администратор, выберите действие:",
        reply_markup=keyboard
    )
    
    # Ответ на нажатие кнопки "Назад"
    await callback_query.answer("Возвращаемся в главное меню администратора!")






async def send_admin_menu(message: types.Message):
    """Отправляем меню администратора с кнопками."""
    help_button = InlineKeyboardButton("💬 Помощь", callback_data="help")
    clients_button = InlineKeyboardButton("👥 Клиенты", callback_data="clients")
    export_button = InlineKeyboardButton("📊 Выгрузить данные на диск", callback_data="export_data")
    admin_button = InlineKeyboardButton("👑 Администраторы", callback_data="admin_data")

    # Создаем клавиатуру с кнопками
    keyboard = InlineKeyboardMarkup(row_width=2).add(help_button, clients_button).row(export_button).row(admin_button)

    # Отправляем сообщение с кнопками
    await message.answer(
        "Здравствуйте, администратор! Выберите действие:",
        reply_markup=keyboard
    )

async def admin_menu(message: types.Message):
    """Проверяем, является ли пользователь администратором, и показываем меню."""
    if message.from_user.id in admins:
        # Отправляем меню администратора
        await send_admin_menu(message)
    else:
        await message.reply("У вас нет прав для использования этой команды.")


async def handle_help(callback_query: types.CallbackQuery):
    """Обрабатываем запрос на помощь и даём описание команды отправки сообщений."""
    
    help_text = (
        "💬 <b>Команда |send</b>:\n\n"
        "Команда для отправки сообщений пользователям бота или всем пользователям сразу.\n\n"
        "Формат команды:\n<code>|send |id| сообщение</code>\n\n"
        "- <b>id</b>: Это ID пользователя, которому нужно отправить сообщение. "
        "Если в качестве ID указано <i>'all'</i>, сообщение будет отправлено всем пользователям.\n"
        "- <b>сообщение</b>: Текст сообщения, которое будет отправлено. Текст можно указать после символа '|'.\n\n"
        "Пример:\n"
        "1. Отправить сообщение конкретному пользователю:\n"
        "<code>|send |123456789| Привет, как дела?</code>\n"
        "Это отправит сообщение пользователю с ID 123456789.\n\n"
        "2. Отправить сообщение всем пользователям:\n"
        "<code>|send |all| Важная информация для всех пользователей!</code>\n"
        "Это отправит сообщение всем зарегистрированным пользователям.\n\n"
        "Важно: Используйте правильный формат и передавайте корректные данные для успешной рассылки.\n\n"

        "💬 <b>Команда |admin</b>:\n\n"
        "Команда для добавления нового администратора в систему.\n\n"
        "Формат команды:\n<code>|admin |id| |name| |comment|</code>\n\n"
        "- <b>id</b>: Это ID пользователя, которому нужно присвоить роль администратора. ID должен быть целым числом.\n"
        "- <b>name</b>: Имя администратора.\n"
        "- <b>comment</b>: Дополнительный комментарий (может быть пустым).\n\n"
        "Пример:\n"
        "1. Добавить администратора с ID 123456 и комментарием:\n"
        "<code>|admin |123456| |Иван Иванов| |Администратор нового магазина|</code>\n\n"
        "2. Добавить администратора без комментария:\n"
        "<code>|admin |7891011| |Петр Петров| |</code>\n\n"
        "Важно: Убедитесь, что вы передаете правильный формат данных, чтобы администратор был успешно добавлен.\n\n"
        "🛠 <i>Раздел 'Помощь' завершён. Если у вас есть вопросы, не стесняйтесь обращаться!</i>"
    )

                 

    await callback_query.answer("Открываем справочные материалы... 💬")
    await callback_query.message.edit_text(help_text, parse_mode=ParseMode.HTML)



async def handle_clients(callback_query: types.CallbackQuery):
    """Обрабатываем запрос на список клиентов и отправляем файл."""
    
    # Начинаем редактировать сообщение
    await callback_query.answer("👥 Список клиентов: Экспортируем данные...")

    # Этап 1: Начало процесса экспорта
    await callback_query.message.edit_text(
        "<b>👥 Экспортируем список клиентов...</b>", parse_mode=ParseMode.HTML
    )

    # Экспорт данных в Excel
    user_db.export_to_excel("users_data.xlsx")
    
    # Этап 2: Данные экспортированы, готовимся к отправке
    await asyncio.sleep(1)  # Задержка для имитации работы
    await callback_query.message.edit_text(
        "<i>📊 Данные экспортированы. Готовимся отправить файл...</i>", parse_mode=ParseMode.HTML
    )
    
    # Этап 3: Отправляем файл
    try:
        with open("users_data.xlsx", "rb") as file:
            await callback_query.message.answer_document(
                document=file,
                caption="<b>Вот список клиентов в Excel-формате.</b>", parse_mode=ParseMode.HTML
            )
        
        # Этап 4: Сообщаем, что файл отправлен
        await callback_query.message.edit_text(
            "<b>👥 Список клиентов был успешно экспортирован и отправлен.</b>", parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        # В случае ошибки при отправке файла
        await callback_query.message.edit_text(
            "<b>❌ Произошла ошибка при экспорте данных.</b>", parse_mode=ParseMode.HTML
        )
        print(f"Ошибка при отправке файла: {e}")



# Функция для обработки нажатия кнопки "📊 Выгрузить данные на диск"
import asyncio
from aiogram import types
from aiogram.types import ParseMode

async def handle_export_data(callback_query: types.CallbackQuery):
    """Обрабатываем запрос на выгрузку данных на диск и показываем процесс."""

    await callback_query.answer("📊 Начинаем выгрузку данных...")

    # Начинаем редактировать сообщение с использованием HTML
    await callback_query.message.edit_text(
        "<b>📊 Начинаем выгрузку данных...</b>", parse_mode=ParseMode.HTML
    )

    # Этап 1: Показать, что процесс начинается
    await asyncio.sleep(1)  # Задержка для имитации работы
    await callback_query.message.edit_text(
        "<i>📊 Почти готово... <b>Обрабатываем данные...</b></i>", parse_mode=ParseMode.HTML
    )

    # Этап 2: Показать, что данные обрабатываются
    await asyncio.sleep(2)  # Задержка для имитации работы
    await callback_query.message.edit_text(
        "<i>📊 Почти готово... <b>Загружаем данные на диск...</b></i>", parse_mode=ParseMode.HTML
    )

    # Экспортируем данные в Excel (в реальном коде можно добавить вызов экспортной функции)
    user_db.export_to_excel("users_data.xlsx")

    # Этап 3: Загружаем файл на Яндекс.Диск
    token = ya_token
    local_file_path = 'users_data.xlsx'
    file_path_on_disk = '/EBSH/users_data.xlsx'

    # Загружаем файл на Яндекс.Диск
    user_db.upload_file_to_yandex_disk(token, local_file_path, file_path_on_disk)

    # Завершаем процесс
    await asyncio.sleep(1)  # Задержка для имитации завершения процесса
    await callback_query.message.edit_text(
        "<b>📊 Данные успешно выгружены на <a href='https://disk.yandex.ru/d/4FRXkiytaRbaPg'>диск</a>.</b>\nВсе готово!", parse_mode=ParseMode.HTML
    )


async def excel_upload_handler(message: types.Message):
    if message.from_user.id not in admins:
        return

    if message.document.mime_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        await message.reply("Пожалуйста, отправьте файл в формате Excel (.xlsx).")
        return

    file_info = await bot.get_file(message.document.file_id)
    downloaded = await bot.download_file(file_info.file_path)

    local_path = message.document.file_name  # сохраняем в текущей папке
    with open(local_path, "wb") as f:
        f.write(downloaded.read())

    try:
        db = UserDB()
        db.load_from_excel(local_path)
        await message.reply("Данные успешно загружены в базу.")
    except Exception as e:
        await message.reply(f"Ошибка при загрузке данных: {e}")
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)

def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_send_message, commands=['send'], commands_prefix='|')
    dp.register_message_handler(cmd_admin, commands=['admin'], commands_prefix='|')
    dp.register_message_handler(admin_menu, commands=['admin'])  # Обработчик команды /admin
    dp.register_callback_query_handler(handle_help, lambda c: c.data == 'help')  # Обработчик кнопки помощи
    dp.register_callback_query_handler(handle_clients, lambda c: c.data == 'clients')  # Обработчик кнопки клиентов
    dp.register_callback_query_handler(handle_export_data, lambda c: c.data == 'export_data')  # Обработчик кнопки выгрузки данных
    dp.register_callback_query_handler(delete_admin_handler, lambda c: c.data == 'delete_admin')  # Обработчик для удаления администратора
    dp.register_callback_query_handler(back_to_main, lambda c: c.data == "admin_main_menu")  # Обработчик для кнопки "Назад"
    dp.register_callback_query_handler(admin_data_handler, lambda c: c.data == 'admin_data')
    dp.register_callback_query_handler(view_admins_handler, lambda c: c.data == 'view_admins')
    dp.register_callback_query_handler(show_admin_info, lambda c: c.data.startswith('admin_'))
    dp.register_callback_query_handler(delete_admin_handler, lambda c: c.data.startswith('delete_'))
    dp.register_message_handler(excel_upload_handler, content_types=types.ContentType.DOCUMENT)
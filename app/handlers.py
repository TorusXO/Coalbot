from aiogram import types, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import time
import datetime
import asyncio

from .Classes import ShishaCallback, ShishaMenuCallback, TableCallback, Shisha
from .variables import db, active_chats, table_builder
from .functions import get_user_data, update_status, status_updater
from bot_logger import logger, bot

router = Router()

@router.message(Command('minus'))
async def decrease_shishas(message: types.Message):
    total_shishas = db.get_total_shishas()
    if total_shishas > 0:
        db.decrement_total_shishas()
        total_shishas = db.get_total_shishas()  # Get the updated total shishas
        await bot.send_message(chat_id=message.chat.id, text=f'Total shishas decreased by 1, remaining: {total_shishas}')
    else:
        await bot.send_message(chat_id=message.chat.id, text='Total shishas is already 0.')


@router.message(Command('reset_counter'))
async def reset_counter(message: types.Message):
    today = datetime.date.today()
    total_shishas = db.get_total_shishas()
    await bot.send_message(chat_id=message.chat.id, text=f'{today.strftime("%d.%m.%Y")} - {total_shishas} shishas')
    db.reset_total_shishas()


@router.message(CommandStart())
async def send_welcome(message: types.Message):
    user_data = get_user_data(message.chat.id)
    active_chats.append(message.chat.id)
    user_data["chat_id_updater"] = message.chat.id
    if user_data["updater"] is not None:
        user_data["updater"].cancel()
    user_data["stop_flag"] = False
    user_data["updater"] = asyncio.create_task(status_updater())

    # Load shishas for each table from the database
    for table in user_data["tables"].values():
        shishas = db.get_shishas(table.id)
        table.shishas = {shisha.db_id: shisha for shisha in shishas}

    table_builder = InlineKeyboardBuilder()
    for table_id, table in user_data["tables"].items():
        table_builder.button(text=f'{table.name}', callback_data=TableCallback(action="select", table_id=table_id).pack())
    table_builder.adjust(5, 5)
    markup = table_builder.as_markup()
    user_data["menu_message"] = await bot.send_message(message.chat.id, "Выбор стола:", reply_markup=markup)
    await update_status(message)
    logger.info('Bot started')

@router.callback_query(TableCallback.filter())
async def process_table_callback(callback_query: types.CallbackQuery, callback_data: TableCallback):
    logger.info(f"Received callback data: {callback_query.data}")
    user_data = get_user_data(callback_query.from_user.id)
    if callback_data.action == "select":
        table_id = callback_data.table_id
        if table_id == 0:  # Ignore the callback if the table_id is 0
            return
        user_data["current_table"] = callback_data.table_id

        submenu_builder = InlineKeyboardBuilder()
        
        # Add buttons for each active shisha
        for j, shisha in enumerate(user_data["tables"][table_id].shishas.values()):
            if shisha is not None:
                submenu_builder.button(text=f'{user_data["tables"][table_id].name} Кальян {j+1}', callback_data=ShishaMenuCallback(action="shisha", table_id=table_id, shisha_db_id=shisha.db_id).pack())
                # Add button to add another shisha
        submenu_builder.button(text='Добавить кальян', callback_data=ShishaCallback(action="add", table_id=table_id).pack())
        # Add button to go back to table selection
        submenu_builder.button(text='Выбор стола', callback_data=TableCallback(action="back", table_id=0).pack())
        submenu_builder.adjust(2, 2)

        new_content = f'{user_data["tables"][table_id].name}. Выбрать или добавить кальян:'
        new_markup = submenu_builder.as_markup()

        # Get the current message content and reply markup
        current_content = callback_query.message.text
        current_markup = callback_query.message.reply_markup

        # Only edit the message if the content or reply markup has changed
        if new_content != current_content or new_markup != current_markup:
            try:
                await bot.edit_message_text(new_content, chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=new_markup)
            except TelegramBadRequest as e:
                if 'message is not modified' in str(e):
                    pass  # Ignore the 'message is not modified' error
                else:
                    raise  # Re-raise the exception if it's a different error

    elif callback_data.action == "back":
        await bot.edit_message_text("Выбор стола:", chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=table_builder.as_markup())
        await callback_query.answer()

@router.callback_query(ShishaCallback.filter())
async def process_add_callback(callback_query: types.CallbackQuery, callback_data: ShishaCallback):
    logger.info(f"Received callback data: {callback_query.data}")
    user_data = get_user_data(callback_query.from_user.id)
    table_id = callback_data.table_id
    user_data["current_table"] = callback_data.table_id

    if callback_data.action == "add":
        table_id = callback_data.table_id
        start_time = time.time()
        chat_id = callback_query.from_user.id  
        shisha_id = len(user_data["tables"][table_id].shishas) + 1
        new_shisha = Shisha(id=shisha_id, table_id=table_id, start_time=start_time, chat_id=chat_id, coal_changes=0)
        db_id = db.insert_shisha(table_id, new_shisha.start_time, callback_query.from_user.id, new_shisha.coal_changes)  # Add the new shisha to the database
        new_shisha.db_id = db_id  # Store the id of the inserted shisha in the Shisha object
        user_data["tables"][table_id].shishas[db_id] = new_shisha  # Store the new Shisha object in the dictionary
        shisha = user_data["tables"][table_id].shishas[db_id]  # Retrieve the shisha object from the dictionary
        await callback_query.answer("Кальян добавлен.")
        await update_status(callback_query.message)
        user_data["current_table"] = table_id  # Ensure the current table is set to the table where the shisha was added
        # Define new_content here
        new_content = f'{user_data["tables"][table_id].name}. Выбрать или добавить кальян:'
        # Create a submenu builder
        submenu_builder = InlineKeyboardBuilder()
        # Add buttons for each active shisha
        for shisha in user_data["tables"][table_id].shishas.values():
            if shisha is not None:
                submenu_builder.button(text=f'{user_data["tables"][table_id].name} Кальян {shisha.id}', callback_data=ShishaMenuCallback(action="shisha", table_id=table_id, shisha_db_id=shisha.db_id).pack())
        submenu_builder.button(text='Добавить кальян', callback_data=ShishaCallback(action="add", table_id=table_id).pack())
        # Add button to go back to table selection
        submenu_builder.button(text='Выбор стола', callback_data=TableCallback(action="back", table_id=0).pack())
        submenu_builder.adjust(2, 2)

        new_markup = submenu_builder.as_markup()

        # Get the current message content and reply markup
        current_content = callback_query.message.text
        current_markup = callback_query.message.reply_markup

        # Only edit the message if the content or reply markup has changed
        if new_content != current_content or new_markup != current_markup:
            try:
                await bot.edit_message_text(new_content, chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=new_markup)
            except TelegramBadRequest as e:
                if 'message is not modified' in str(e):
                    pass  # Ignore the 'message is not modified' error
                else:
                    raise  # Re-raise the exception if it's a different error

@router.callback_query(ShishaMenuCallback.filter())
async def process_shisha_callback(callback_query: types.CallbackQuery, callback_data: ShishaMenuCallback):
    logger.info(f"Received callback data: {callback_query.data}")
    user_data = get_user_data(callback_query.from_user.id)
    table_id = callback_data.table_id
    shisha_db_id = callback_data.shisha_db_id
    # Find the shisha with the matching db_id
    shisha = user_data["tables"][table_id].shishas.get(shisha_db_id)

    if shisha is None:
        await callback_query.answer("No shisha found with the given ID.")
        return

    if callback_data.action == "shisha":
        table_id = user_data['current_table']
        shisha = user_data["tables"][table_id].shishas[shisha_db_id]
        new_content = f'{user_data["tables"][table_id].name}. Кальян {shisha.id}. Выберите действие:' 
        submenu_builder = InlineKeyboardBuilder()
        submenu_builder.button(text=f'Замена угля ({shisha.coal_changes})', callback_data=ShishaMenuCallback(action="reset", table_id=table_id, shisha_db_id=shisha_db_id).pack())
        submenu_builder.button(text='Удалить кальян', callback_data=ShishaMenuCallback(action="delete", table_id=table_id, shisha_db_id=shisha_db_id).pack())
        submenu_builder.button(text='Выбор кальянов', callback_data=TableCallback(action="select", table_id=user_data["current_table"]).pack())
        submenu_builder.adjust(2,2)  # Adjust the row width before converting to markup
        new_markup = submenu_builder.as_markup()  # Convert the builder to markup after adjusting
        await bot.edit_message_text(new_content, chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=new_markup)
    elif callback_data.action == "reset":
        shisha = user_data["tables"][table_id].shishas[shisha_db_id]
        shisha.start_time = time.time()
        shisha.coal_changes += 1
        shisha.last_coal_change = time.time()
        db.update_shisha(shisha.db_id, shisha.start_time, shisha.coal_changes, shisha.last_coal_change)  # Update the shisha in the database
        await asyncio.sleep(0.1)  # Add a small delay
        await callback_query.answer("Уголь заменен.")
        await update_status(callback_query.message)
        await process_shisha_callback(callback_query, ShishaMenuCallback(action="shisha", table_id=table_id, shisha_db_id=shisha_db_id))
    elif callback_data.action == "delete":
        shisha = user_data["tables"][table_id].shishas[shisha_db_id]
        db.delete_shisha(shisha.db_id)  # Delete the shisha from the database using its db_id
        del user_data["tables"][table_id].shishas[shisha_db_id]  # Remove the shisha from the in-memory data structure
        await callback_query.answer("Кальян удален.")
        await asyncio.sleep(0.1)  # Add a small delay
        await update_status(callback_query.message)
        await process_table_callback(callback_query, TableCallback(action="select", table_id=table_id))
        db.increment_total_shishas()
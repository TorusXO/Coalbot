from aiogram import Bot, types
import time
import asyncio

from app.variables import user_data, tables, active_chats, db
from config import TOKEN

bot = Bot(token=TOKEN)


def get_user_data(chat_id):
    if chat_id not in user_data:
        user_data[chat_id] = {
            "status_message": None,
            "current_table": None,
            "menu_message": None,
            "updater": None,
            "chat_id_updater": None,
            "tables": tables  # All users share the same tables
        }
    return user_data[chat_id]

async def update_status(message: types.Message):
    user_data = get_user_data(message.chat.id)
    status_text = ''
    total_shishas = db.get_total_shishas()
    floor_1_changes = 0
    floor_2_changes = 0
    for table_id, table in user_data["tables"].items():
        shishas = db.get_shishas(table_id)
        for j, shisha in enumerate(shishas):
            elapsed_time = time.time() - shisha.start_time
            remaining_time = max(15 * 60 - elapsed_time, 0)
            formatted_time = format_time(remaining_time)
            if shisha.coal_changes > 2:
                emoji = '☑️'
            elif remaining_time <= 2 * 60:
                emoji = '🔴'
            elif remaining_time <= 8 * 60:
                emoji = '🟡'
            else:
                emoji = '🟢'
            shisha_text = f'{emoji} {table.name} Кальян {j + 1} {formatted_time} Замен: {shisha.coal_changes}'
            status_text += shisha_text + '\n'
            if shisha.coal_changes < 3:
                if table.floor == 1:
                    floor_1_changes += 1
                else:
                    floor_2_changes += 1
    status_text += f'1ый этаж на замену: {floor_1_changes}\n'
    status_text += f'2ой этаж на замену: {floor_2_changes}\n'
    status_text += f'Всего кальянов: {total_shishas}\n'
    if status_text == '':
        status_text = 'Нет активных кальянов'

    prev_status_text = user_data.get("status_text", "")
    if status_text != prev_status_text:
        # Delete the existing status message (if any)
        if user_data["status_message"] is not None:
            await bot.delete_message(chat_id=message.chat.id, message_id=user_data["status_message"].message_id)

        # Send the new status message
        user_data["status_message"] = await message.answer(status_text)
        user_data["status_text"] = status_text  # Update the stored status text

async def status_updater():
    while True:
        for chat_id in active_chats:
            user_data = get_user_data(chat_id)
            if user_data["status_message"] is not None:
                await update_status(user_data["status_message"])
        await asyncio.sleep(10)


def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f'{int(minutes)}:{int(seconds):02}'

def calculate_remaining_time(start_time):
    elapsed_time = time.time() - start_time  # Calculate the elapsed time
    total_time = 15*60  # The total time for a shisha is 15 minutes
    remaining_time = total_time - elapsed_time  # Calculate the remaining time
    remaining_time = max(remaining_time, 0)  # Return the remaining time, or 0 if the shisha is finished

    # Convert the remaining time to minutes and seconds
    minutes = int(remaining_time // 60)
    seconds = int(remaining_time % 60)

    # Return the remaining time in a 'minutes:seconds' format
    return f'{minutes}:{seconds:02}'
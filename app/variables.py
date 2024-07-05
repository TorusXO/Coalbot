from aiogram.utils.keyboard import InlineKeyboardBuilder
from .Classes import TableCallback, Table
from db_manager import DBManager

table_names = ['2 стол', '3 стол', 'слева бар', 'центр бар', 'справа бар', '4 стол', '5 стол', '6 стол', '7 стол', '8 стол', '9 стол', '10 стол','11 стол']
table_floors = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2]
# Create tables as a dictionary mapping table IDs to Table objects
tables = {id: Table(id, name, floor) for id, (name, floor) in enumerate(zip(table_names, table_floors), start=1)}
user_data = {}
active_chats = []
status_messages = {}

table_builder = InlineKeyboardBuilder()
# Create buttons for each table
for table_id, table in tables.items():
    table_builder.button(text=f'{table.name}', callback_data=TableCallback(action="select", table_id=table_id).pack())
table_builder.adjust(5, 5)
submenu_builder = InlineKeyboardBuilder()
submenu_builder.adjust(2, 2)
db = DBManager()
stop_flag = False

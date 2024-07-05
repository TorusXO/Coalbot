from aiogram.filters.callback_data import CallbackData
from typing import Optional
import time
# Define a class for your callback data with structure
class ShishaCallback(CallbackData, prefix='shisha'):
    action: str
    table_id: int
    shisha_id: int = 0  # Set a default value for shisha_id

class TableCallback(CallbackData, prefix='table_cb'):
    action: str
    table_id: int

class ShishaMenuCallback(CallbackData, prefix='shisha_menu'):
    action: str
    table_id: int
    shisha_db_id: Optional[int] = None  # Make shisha_db_id an optional field

class Shisha:
    def __init__(self, id, table_id, start_time, chat_id, coal_changes=0, last_update=None, db_id=None, last_coal_change=None):
        self.id = id
        self.table_id = table_id
        self.start_time = start_time
        self.chat_id = chat_id
        self.coal_changes = coal_changes
        self.last_update = last_update if last_update is not None else time.time()
        self.db_id = db_id
        self.last_coal_change = last_coal_change if last_coal_change is not None else time.time()

class Table:
    def __init__(self, id, name, floor, shishas=None):
        self.id = id
        self.name = name
        self.floor = floor
        self.shishas = shishas if shishas is not None else {}

    def copy(self):
        # Create a new Table object with the same properties
        return Table(self.id, self.name, self.floor, self.shishas.copy())
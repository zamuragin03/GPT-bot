from aiogram.fsm.state import State,StatesGroup

class FSMAdmin(StatesGroup):
    choosing_action = State()
    typing_new_keyword = State()
    selecting_keyword_to_remove = State()
from aiogram.fsm.state import State, StatesGroup


class FSMAdmin(StatesGroup):
    choosing_action = State()
    type_mass_message = State()
    choosing_type = State()

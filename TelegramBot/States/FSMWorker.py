from aiogram.fsm.state import State,StatesGroup

class FSMWorker(StatesGroup):
    beginning = State()
    choosing_action = State()
    
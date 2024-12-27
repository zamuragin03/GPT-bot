from aiogram.fsm.state import State, StatesGroup


class FSMUser(StatesGroup):
    choosing_language = State()
    choosing_action = State()
    select_mode = State()
    in_fereal_sytem = State()


class FSMCodeHelper(StatesGroup):
    typing_message = State()


class FSMChartCreator(StatesGroup):
    typing_request = State()


class FSMAbstracthelper(StatesGroup):
    typing_topic = State()


class FSMCourseWorkHelper(StatesGroup):
    typing_topic = State()
    choosing_action_with_plan = State()
    typing_new_details_to_plan = State()
    typing_comments_on_plan = State()


class FSMPhotoProblem(StatesGroup):
    sending_message = State()

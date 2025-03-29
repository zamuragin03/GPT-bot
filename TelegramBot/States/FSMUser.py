from aiogram.fsm.state import State, StatesGroup


class FSMUser(StatesGroup):
    choosing_language = State()
    choosing_action = State()
    select_mode = State()
    in_fereal_sytem = State()
    choosing_action_with_sub = State()
    in_payment = State()
    typing_promocode = State()
    choosing_action_with_my_profile = State()
    choosing_reasoning_effort = State()


class FSMCodeHelper(StatesGroup):
    typing_message = State()
    choosing_reasoning_effort = State()


class FSMChartCreator(StatesGroup):
    choosing_action = State()
    typing_request = State()


class FSMAbstracthelper(StatesGroup):
    choosing_action = State()
    typing_topic = State()
    selecting_pages_number = State()
    typing_manual_plan = State()
    choosing_plan_generation = State()
    choosing_action_with_plan = State()
    proceed_action = State()


class FSMEssayhelper(StatesGroup):
    choosing_action = State()
    typing_topic = State()
    selecting_pages_number = State()
    typing_manual_plan = State()
    choosing_plan_generation = State()
    choosing_action_with_plan = State()
    proceed_action = State()


class FSMCourseWorkHelper(StatesGroup):
    choosing_action = State()
    typing_topic = State()
    selecting_pages_number = State()
    typing_manual_plan = State()
    choosing_plan_generation = State()
    choosing_action_with_plan = State()
    proceed_action = State()


class FSMPhotoProblem(StatesGroup):
    sending_message = State()


class FSMRewritingHelper(StatesGroup):
    sending_document = State()


class FSMPPTXHelper(StatesGroup):
    choosing_action = State()
    typing_topic = State()
    change_verbosity = State()
    change_language = State()
    setting_options = State()
    change_length = State()
    change_template = State()
    change_fetch_images = State()
    change_tone = State()

class FSMAntiplagitHelper(StatesGroup):
    choosing_action = State()
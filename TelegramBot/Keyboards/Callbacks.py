from aiogram.filters.callback_data import CallbackData


class Callbacks:

    class page_number_callback(CallbackData, prefix='get_page_number'):
        page_number: int
        
    class verbosity_callback(CallbackData, prefix='verbosity'):
        verbosity: str

    class tone_callback(CallbackData, prefix='tone'):
        tone: str
        
    class fetch_image_callback(CallbackData, prefix='fetch_image'):
        fetch_image: bool

    # class plan_type_callback(CallbackData, prefix='plan_type'):
    #     plan_type: str

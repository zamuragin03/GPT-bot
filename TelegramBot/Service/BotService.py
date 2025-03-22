import itertools
import time
from PIL import Image, ImageEnhance, ImageOps
import re
from datetime import datetime, timedelta
import random
import aiofiles
import docx
from Service import LocalizationService, TelegramUserSubscriptionService
import base64
from docx import Document
from docx.oxml.ns import qn
# ИМПОРТ ДЛЯ eval
import numpy as np
from docx.shared import Pt
import matplotlib.pyplot as plt
from aiogram.types import FSInputFile
from Config import PATH_TO_TEMP_FILES, SUBSCRIPTION_LIMITATIONS, GROUP_LINK_URL, DAILY_LIMITATIONS, PATH_TO_DOWNLOADED_FILES, PATH_TO_TEMP_WATERMARK
from DataModels.ChartCreatorDataModel import ChartResponse
import matplotlib
from aiogram import types, Bot
import asyncio
from aiogram.enums.parse_mode import ParseMode

matplotlib.use('Agg')

matplotlib.rc('text.latex', preamble=r'\usepackage{amsmath}')


class BotService:
    progress_indicators = ["◒", "◐", "◓", "◑"]  # Разные символы вращения
    progress_cycle = itertools.cycle(progress_indicators)

    @staticmethod
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    @staticmethod
    def invert_image(base_image_path, output_path):
        """
        Инвертирует изображение (фон -> черный, текст -> белый).
        """
        # Открываем изображение
        base_image = Image.open(base_image_path).convert("RGB")

        # Инвертируем цвета изображения
        inverted_image = ImageOps.invert(base_image)

        # Сохраняем инвертированное изображение
        inverted_image.save(output_path, "JPEG")

    @staticmethod
    def latex_to_image(latex_code, external_id):
        # Генерация изображения на основе LaTeX
        fig, ax = plt.subplots()
        latex_code = str(latex_code).replace('\n', '')
        latex_code_lines = latex_code.split(r'\\')
        full_code = "\n".join(
            [f"${line.strip()}$" for line in latex_code_lines])

        ax.text(
            x=0.5, y=0.5,
            s=full_code.replace('$$', '').replace(
                '\end{align*}', '').replace('\begin{align*}', ''),
            horizontalalignment="center",
            verticalalignment="center",
            fontsize=20, ha='center', va='center',
        )
        ax.axis('off')
        plt.ioff()
        fig.set_size_inches(8, 4)

        # Сохраняем временное изображение
        base_path = PATH_TO_TEMP_FILES.joinpath(
            str(external_id)).joinpath('solution.jpg')
        base_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(base_path, bbox_inches='tight', pad_inches=0.5, dpi=300)
        plt.close(fig)

        # Инвертируем изображение
        inverted_path = PATH_TO_TEMP_FILES.joinpath(
            str(external_id)).joinpath('solution_inverted.jpg')
        BotService.invert_image(base_image_path=base_path,
                                output_path=inverted_path)

        # Путь к финальному изображению с водяным знаком
        final_path = PATH_TO_TEMP_FILES.joinpath(
            str(external_id)).joinpath('solution_with_watermark.jpg')

        # Путь к файлу водяного знака

        # Наложение водяного знака
        BotService.add_watermark(base_image_path=inverted_path,
                                 watermark_path=PATH_TO_TEMP_WATERMARK, output_path=final_path)

        return FSInputFile(path=final_path, filename="solution_with_watermark.jpg")

    def add_watermark(base_image_path, watermark_path, output_path):
        """
        Накладывает водяной знак с сохранением пропорций и регулируемой прозрачностью.
        """
        from PIL import ImageEnhance

        # Открываем базовое изображение и водяной знак
        base_image = Image.open(base_image_path).convert("RGBA")
        watermark = Image.open(watermark_path).convert("RGBA")

        # Масштабируем водяной знак с учётом `contain`
        base_width, base_height = base_image.size
        watermark_ratio = min(base_width / watermark.width,
                              base_height / watermark.height)
        watermark_width = int(watermark.width * watermark_ratio)
        watermark_height = int(watermark.height * watermark_ratio)
        watermark = watermark.resize(
            (watermark_width, watermark_height), Image.Resampling.LANCZOS)

        # Устанавливаем прозрачность водяного знака
        alpha = watermark.split()[3]  # Канал альфа (прозрачность)
        alpha = ImageEnhance.Brightness(alpha).enhance(0.5)  # Прозрачность 15%
        watermark.putalpha(alpha)

        # Позиция для водяного знака (по центру)
        position = (
            (base_width - watermark_width) // 2,
            (base_height - watermark_height) // 2
        )

        # Создаём слой для объединения изображений
        transparent = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
        transparent.paste(base_image, (0, 0))
        transparent.paste(watermark, position, watermark)

        # Сохраняем итоговое изображение
        # Преобразуем в RGB для сохранения в JPEG
        transparent = transparent.convert("RGB")
        transparent.save(output_path, "JPEG")

    @staticmethod
    def create_image_by_user_requset(result: ChartResponse, external_id: int):
        plt.clf()

    # Отключаем интерактивный режим, чтобы не открывалось окно
        plt.ioff()
        x = eval(result.x_range)
        y = eval(result.y_range)
        plt.plot(x, y, label=result.title)

        plt.xlabel('x')
        plt.ylabel('y')
        plt.title(result.title)

        plt.legend()
        plt.grid(True)

        end_path = PATH_TO_TEMP_FILES.joinpath(
            str(external_id)).joinpath('chart.jpg')
        end_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(end_path, bbox_inches='tight', pad_inches=0.5, dpi=300)
        plt.close()
        return FSInputFile(path=end_path, filename="chart.jpg")

    @staticmethod
    async def check_user_subscription(event: types.Message):
        from Keyboards.keyboards import Keyboard
        try:
            member = await event.bot.get_chat_member('@student_helper_news', event.from_user.id)
            if member.status not in ["member", "creator", "administrator"]:
                await event.bot.send_message(
                    event.from_user.id,
                    text=LocalizationService.BotTexts.GetSubscriptionRequirements(
                        'ru'),
                    reply_markup=Keyboard.Get_Link_To_Channel('ru'),
                )
                return False
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def calculate_remaining_time(subscription):
        if not subscription:
            return {
                "days": 0,
                "hours": 0,
                "minutes": 0
            }
        expiration_time = datetime.strptime(
            subscription.get('till'), '%Y-%m-%dT%H:%M:%S.%f')

        now = datetime.now()

        remaining_time = expiration_time - now

        if remaining_time.total_seconds() > 0:
            # Получаем количество дней и часов из оставшегося времени
            remaining_days = remaining_time.days
            remaining_seconds = remaining_time.seconds
            remaining_hours = remaining_seconds // 3600
            remaining_minutes = (remaining_seconds % 3600) // 60

            return {
                "days": remaining_days,
                "hours": remaining_hours,
                "minutes": remaining_minutes
            }
        else:
            return {
                "days": 0,
                "hours": 0,
                "minutes": 0
            }

    @staticmethod
    def get_my_profile_text(user, user_obj, subscription, selected_language):
        def format_limit(limit):
            if limit == 99999:
                return LocalizationService.BotTexts.GetUnlimitedTranslation(selected_language)
            elif limit == 0:
                return 0
            return limit

        localized_name = LocalizationService.BotTexts.GetsubscriptionName(
            name=subscription['sub_type']['name'] if subscription else 'inactive',
            selected_language=selected_language
        )
        remained_time = BotService.calculate_remaining_time(subscription)
        first_name = user.first_name

        if subscription:
            limitation_object = TelegramUserSubscriptionService.GetUserLimitations(
                user.id)
            limits = SUBSCRIPTION_LIMITATIONS
        else:
            limitation_object = TelegramUserSubscriptionService.GetUserDailyLimitations(
                user.id)
            limits = DAILY_LIMITATIONS

        limitations_remaining = limitation_object.get('limitations')

        localized_text = LocalizationService.BotTexts.GetMyProfileText(
            selected_language)

        return localized_text.format(
            first_name=first_name,
            user_id=user.id,
            localized_name=localized_name,
            days=remained_time['days'],
            hours=remained_time['hours'],
            minutes=remained_time['minutes'],
            default_mode=format_limit(limits["default_mode"]),
            default_mode_remain=limits["default_mode"] -
            max(0, limitations_remaining["default_mode"]),
            code_helper=format_limit(limits["code_helper"]),
            code_helper_remain=limits["code_helper"] -
            max(0, limitations_remaining["code_helper"]),
            abstract_writer=format_limit(limits["abstract_writer"]),
            abstract_writer_remain=limits["abstract_writer"] -
            max(0, limitations_remaining["abstract_writer"]),
            course_work_helper=format_limit(limits["course_work_helper"]),
            course_work_helper_remain=limits["course_work_helper"] -
            max(0, limitations_remaining["course_work_helper"]),
            final_paper_helper=format_limit(limits["final_paper_helper"]),
            final_paper_helper_remain=limits["final_paper_helper"] -
            max(0, limitations_remaining["final_paper_helper"]),
            essay_helper=format_limit(limits["essay_helper"]),
            essay_helper_remain=limits["essay_helper"] -
            max(0, limitations_remaining["essay_helper"]),
            photo_issue_helper=format_limit(limits["photo_issue_helper"]),
            photo_issue_helper_remain=limits["photo_issue_helper"] -
            max(0, limitations_remaining["photo_issue_helper"]),
            chart_creator_helper=format_limit(limits["chart_creator_helper"]),
            chart_creator_helper_remain=limits["chart_creator_helper"] - max(
                0, limitations_remaining["chart_creator_helper"]),
            power_point_helper=format_limit(limits["power_point_helper"]),
            power_point_helper_remain=limits["power_point_helper"] -
            max(0, limitations_remaining["power_point_helper"]),
            rewriting_helper=format_limit(limits["rewriting_helper"]),
            rewriting_helper_remain=limits["rewriting_helper"] -
            max(0, limitations_remaining["rewriting_helper"])
        )

    @staticmethod
    def parse_work_plan(text):
        # Создаем паттерны для заголовков первого и второго уровня
        header1_pattern = re.compile(r"<h1>(.*?)<\/h1>")
        header2_pattern = re.compile(r"<h2>(.*?)<\/h2>")

        result = []

        text = header1_pattern.sub(lambda m: f"• <b>{m.group(1)}</b>", text)
        text = header2_pattern.sub(lambda m: f"•• {m.group(1)}", text)

        lines = text.split("\n")
        for line in lines:
            result.append(line)

        return "\n".join(result)

    @staticmethod
    def getChangeLanguageText():
        ...

    @staticmethod
    async def GetTXTFileContent(bot: Bot, message: types.Message):
        document = message.document
        file = await bot.get_file(document.file_id)
        photo_folder = PATH_TO_DOWNLOADED_FILES.joinpath(
            str(message.from_user.id))
        photo_folder.mkdir(parents=True, exist_ok=True)
        file_path = photo_folder.joinpath(f'{file.file_unique_id}.jpg')
        await bot.download(file=document.file_id, destination=file_path)
        content = ""
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
        return content

    @staticmethod
    async def WriteFileToTXT(content, external_id):
        end_path = PATH_TO_TEMP_FILES.joinpath(
            str(external_id)).joinpath(f'result{random.randint(1,10000)}.txt')
        async with aiofiles.open(end_path, 'w') as f:
            await f.write(content)
        return FSInputFile(path=end_path, filename="result.txt")

    @staticmethod
    async def GetWordFileContent(bot: Bot, message: types.Message):
        document = message.document
        file = await bot.get_file(document.file_id)
        file_folder = PATH_TO_DOWNLOADED_FILES.joinpath(
            str(message.from_user.id))
        file_folder.mkdir(parents=True, exist_ok=True)
        file_path = file_folder.joinpath(f'{file.file_unique_id}.docx')
        await bot.download(file=document.file_id, destination=file_path)
        doc = docx.Document(file_path)
        content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])

        return content

    @staticmethod
    async def WriteFileToDOCX(content, external_id):
        end_path = PATH_TO_TEMP_FILES.joinpath(
            str(external_id)).joinpath(f'result{random.randint(1,10000)}.docx')
        end_path.parent.mkdir(parents=True, exist_ok=True)
        doc = docx.Document()
        doc.add_paragraph(content)
        doc.save(end_path)
        return FSInputFile(path=end_path, filename="result.docx")

    @staticmethod
    def GetPPTXSettings(selected_language: str,
                        **kwargs):
        plain_text = kwargs.get("plain_text")
        language = kwargs.get("language")
        length = kwargs.get("length")
        template = kwargs.get("template")
        tone = kwargs.get("tone")
        fetch_images = kwargs.get("fetch_images")
        verbosity = kwargs.get("verbosity")

        base_settings = LocalizationService.BotTexts.GetPPTXSettings(
            selected_language)
        not_specified = LocalizationService.BotTexts.GetNotSpecified(
            selected_language)
        return base_settings.format(
            plain_text=plain_text if plain_text else not_specified,
            language=LocalizationService.BotTexts.GetHumanReadableLanguage(
                language) if language else not_specified,
            length=length if length else not_specified,
            template=template if template else not_specified,
            tone=LocalizationService.BotTexts.GetPPTXToneHR(
                tone, selected_language) if tone else not_specified,
            fetch_images=fetch_images if fetch_images else not_specified,
            verbosity=LocalizationService.BotTexts.GetPPTXVerbosityHR(
                verbosity, selected_language) if verbosity else not_specified
        )

    @staticmethod
    async def run_with_progress(message, task, total_time, *args, **kwargs):
        """
        Метод для отображения прогресс-бара с заданным временем, выполнения задачи и удаления сообщения.

        :param message: Сообщение, куда отправлять прогресс
        :param task: Асинхронная задача, которую нужно выполнить
        :param total_time: Общее время выполнения в секундах
        :param args: Аргументы для задачи
        :param kwargs: Именованные аргументы для задачи
        """
        progress_indicators = ["◒", "◐", "◓", "◑"]
        progress_cycle = itertools.cycle(progress_indicators)
        total_steps = 10  # Количество шагов для прогресс-бара
        step_time = total_time / total_steps  # Время на один шаг
        start_time = time.time()

        # Отправляем начальное сообщение
        progress_message = await message.answer("Прогресс начат...")

        for i in range(total_steps + 1):
            # Вычисляем оставшееся время
            remaining_time = max(total_time - (time.time() - start_time), 0)

            # Генерируем прогресс-бар и анимацию
            progress_bar = BotService.create_progress_bar(i, total_steps)
            animated_indicator = next(progress_cycle)

            # Обновляем текст сообщения
            await progress_message.edit_text(
                f"{progress_bar} {animated_indicator} (Осталось: {remaining_time:.1f} сек)"
            )

            # Задержка на заданный интервал
            if remaining_time > 0:
                await asyncio.sleep(step_time)

        # Выполняем задачу
        result = await task(*args, **kwargs)

        # Удаляем сообщение с прогресс-баром
        await progress_message.delete()

        # Возвращаем результат выполнения задачи
        return result

    @staticmethod
    def create_progress_bar(progress, total=10):
        """Создает строку с индикатором прогресса (эмодзи)."""
        filled_char = '⬛️'  # Черный квадрат
        empty_char = '⬜️'   # Белый квадрат
        filled_length = int(progress / total * total)
        empty_length = total - filled_length
        return filled_char * filled_length + empty_char * empty_length + f" {int(progress / total * 100)}%"

    async def send_long_message(target, text: str, parse_mode: str = None, disable_web_page_preview: bool = False, reply_markup=None):
        """
        Отправляет длинное сообщение в несколько батчей, поддерживая как Message, так и CallbackQuery.

        :param target: Объект типа `types.Message` или `types.CallbackQuery`.
        :param text: Текст сообщения.
        :param parse_mode: Режим разметки текста (например, Markdown или HTML).
        :param disable_web_page_preview: Отключение предпросмотра веб-страниц.
        """
        max_length = 4096  # Максимальная длина сообщения в Telegram

        # Разбиваем текст на батчи
        text_batches = [text[i:i + max_length]
                        for i in range(0, len(text), max_length)]

        # Определяем метод отправки в зависимости от типа объекта
        send_method = (
            target.reply if isinstance(
                target, types.Message) else target.message.reply
        )

        # Отправляем каждую часть сообщения
        for batch in text_batches:
            await send_method(
                text=batch,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview, reply_markup=reply_markup
            )

    def formatReferals(referal_obj: list, period:str):
        translation = {
            'last_month': 'в прошлом месяце',
            'this_month': 'в этом месяце',
            'all_time': 'за все время'
        }
        message = f"Топ рефералов{translation[period]} :\n"
        for i, referral in enumerate(referal_obj, start=1):
            username = referral.get('referal__username', 'Не указан')
            external_id = referral.get('referal__external_id', 'Не указан')
            invite_count = referral.get('invite_count', 0)
            message += f"{i}. Имя: {username}, ID: {external_id}, Кол-во приглашенных: {invite_count}\n"
        if len(referal_obj)==0:
            message+='Данных нет'
        return message

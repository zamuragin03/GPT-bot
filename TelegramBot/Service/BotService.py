import os
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
from Config import PATH_TO_TEMP_FILES, SUBSCRIPTION_LIMITATIONS, GROUP_LINK_URL, DAILY_LIMITATIONS,PATH_TO_DOWNLOADED_FILES
from DataModels.ChartCreatorDataModel import ChartResponse
import matplotlib
from aiogram import types, Bot
import asyncio
from aiogram.enums.parse_mode import ParseMode

matplotlib.use('Agg')

matplotlib.rc('text.latex', preamble=r'\usepackage{amsmath}')


class BotService:

    @staticmethod
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    @staticmethod
    def latex_to_image(latex_code, external_id):
        fig, ax = plt.subplots()
        latex_code = str(latex_code).replace('\n', '')
        latex_code_lines = latex_code.split(r'\\')  # Разделяем по строкам
        # Собираем обратно в многострочный формат
        full_code = "\n".join(
            [f"${line.strip()}$" for line in latex_code_lines])

        ax.text(
            x=0.5, y=0.5,
            s=full_code.replace('$$', '').replace(
                '\end{align*}', '').replace('\begin{align*}', ''),  # Многострочный LaTeX

            horizontalalignment="center",
            verticalalignment="center",
            fontsize=20, ha='center', va='center',
        )
        ax.axis('off')
        plt.ioff()
        fig.set_size_inches(8, 4)
        end_path = PATH_TO_TEMP_FILES.joinpath(
            str(external_id)).joinpath('solution.jpg')
        end_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(end_path, bbox_inches='tight', pad_inches=0.5, dpi=300)
        return FSInputFile(path=end_path, filename="solution.jpg")

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
            limitation_object = TelegramUserSubscriptionService.GetUserLimitations(user.id)
            limits = SUBSCRIPTION_LIMITATIONS
        else:
            limitation_object = TelegramUserSubscriptionService.GetUserDailyLimitations(user.id)
            limits = DAILY_LIMITATIONS

        limitations_remaining = limitation_object.get('limitations')

        localized_text = LocalizationService.BotTexts.GetMyProfileText(selected_language)

        return localized_text.format(
            first_name=first_name,
            user_id=user.id,
            localized_name=localized_name,
            days=remained_time['days'],
            hours=remained_time['hours'],
            minutes=remained_time['minutes'],
            default_mode=format_limit(limits["default_mode"]),
            default_mode_remain=limits["default_mode"] - max(0, limitations_remaining["default_mode"]),
            code_helper=format_limit(limits["code_helper"]),
            code_helper_remain=limits["code_helper"] - max(0, limitations_remaining["code_helper"]),
            abstract_writer=format_limit(limits["abstract_writer"]),
            abstract_writer_remain=limits["abstract_writer"] - max(0, limitations_remaining["abstract_writer"]),
            course_work_helper=format_limit(limits["course_work_helper"]),
            course_work_helper_remain=limits["course_work_helper"] - max(0, limitations_remaining["course_work_helper"]),
            final_paper_helper=format_limit(limits["final_paper_helper"]),
            final_paper_helper_remain=limits["final_paper_helper"] - max(0, limitations_remaining["final_paper_helper"]),
            essay_helper=format_limit(limits["essay_helper"]),
            essay_helper_remain=limits["essay_helper"] - max(0, limitations_remaining["essay_helper"]),
            photo_issue_helper=format_limit(limits["photo_issue_helper"]),
            photo_issue_helper_remain=limits["photo_issue_helper"] - max(0, limitations_remaining["photo_issue_helper"]),
            chart_creator_helper=format_limit(limits["chart_creator_helper"]),
            chart_creator_helper_remain=limits["chart_creator_helper"] - max(0, limitations_remaining["chart_creator_helper"]),
            power_point_helper=format_limit(limits["power_point_helper"]),
            power_point_helper_remain=limits["power_point_helper"] - max(0, limitations_remaining["power_point_helper"]),
            rewriting_helper=format_limit(limits["rewriting_helper"]),
            rewriting_helper_remain=limits["rewriting_helper"] - max(0, limitations_remaining["rewriting_helper"])
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

    async def countdown(call=None, countdown_message: types.Message = None, duration=250, interval: int = 5, new_text: str = "", finish_text: str = ''):
        try:
            for remaining in range(duration, 0, -interval):
                await asyncio.sleep(interval)
                formatted_text = new_text.format(
                    minutes=remaining // 60, seconds=remaining % 60, url=GROUP_LINK_URL)
                if countdown_message.text != formatted_text:
                    await countdown_message.edit_text(formatted_text, parse_mode=ParseMode.HTML)
            await countdown_message.edit_text(finish_text)
        except Exception as e:
            print(e)
        except asyncio.CancelledError:
            pass

    @staticmethod
    def getChangeLanguageText():
        ...

    @staticmethod
    async def GetTXTFileContent(bot: Bot, message: types.Message):
        document = message.document
        file = await bot.get_file(document.file_id)
        photo_folder = PATH_TO_DOWNLOADED_FILES.joinpath(str(message.from_user.id))
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
    async def GetWordFileContent(bot: Bot, document: types.Document):
        file = await bot.get_file(document.file_id)
        file_path = f'./{file.file_unique_id}.docx'
        await bot.download(file=document.file_id, destination=file_path)
        doc = docx.Document(file_path)
        content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])

        return content

    @staticmethod
    async def WriteFileToDOCX(content, external_id):
        end_path = PATH_TO_TEMP_FILES.joinpath(
            str(external_id)).joinpath('result.docx')
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

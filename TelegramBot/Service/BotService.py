from datetime import datetime, timedelta
from Service import LocalizationService
import base64
from docx import Document
from docx.oxml.ns import qn
# ИМПОРТ ДЛЯ eval
import numpy as np
from docx.shared import Pt
import matplotlib.pyplot as plt
from aiogram.types import FSInputFile
from Config import PATH_TO_TEMP_FILES
from DataModels.ChartCreatorDataModel import ChartResponse
import matplotlib
from aiogram import types
matplotlib.use('Agg')
import re

matplotlib.rc('text.latex', preamble=r'\usepackage{amsmath}')

BotTexts = LocalizationService.BotTexts


class BotService:

    @staticmethod
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    @staticmethod
    def create_word_document(content):
        doc = Document()
        # Установка стиля для формул
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Arial'
        font.size = Pt(12)

        paragraphs = content.split("\n")
        for paragraph in paragraphs:
            if "<code>" in paragraph and "</code>" in paragraph:
                # Если параграф содержит формулу
                formula = paragraph.replace(
                    "<code>", "").replace("</code>", "")
                doc.add_paragraph().add_run(formula).font.name = 'Cambria Math'
            else:
                doc.add_paragraph(paragraph)

        doc.save("output.docx")

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
                    text=BotTexts.GetSubscriptionRequirements('ru'),
                    reply_markup=Keyboard.Get_Link_To_Channel('ru'),
                )
                return False
            return True
        except Exception as e:
            return False

    @staticmethod
    def calculate_remaining_time(subscription):
        created_at = datetime.fromisoformat(subscription["created_at"])

        duration_hours = subscription["sub_type"]["duration"]

        expiration_time = created_at + timedelta(hours=duration_hours)

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
    def get_my_profile_text(user, subscription, selected_language):
        localized_name = LocalizationService.BotTexts.GetsubscriptionName(
            subscription['sub_type']['name'],selected_language)
        remained_time = BotService.calculate_remaining_time(subscription)
        first_name = user.first_name
        last_name = user.last_name
        username = user.username
        localized_text = LocalizationService.BotTexts.GetMyProfileText(selected_language)
        return localized_text.format(
            first_name=first_name,
            last_name=last_name,
            username=username,
            localized_name=localized_name,
            days=remained_time['days'],
            hours=remained_time['hours'],
            minutes=remained_time['minutes'],
            
        )
    
    @staticmethod
    def parse_course_work_plan(text):
        # Создаем паттерны для заголовков первого и второго уровня
        header1_pattern = re.compile(r"<h1>(.*?)<\/h1>")
        header2_pattern = re.compile(r"<h2>(.*?)<\/h2>")
        
        result = []
        
        text = header1_pattern.sub(lambda m: f"• {m.group(1)}", text)
        text = header2_pattern.sub(lambda m: f"•• {m.group(1)}", text)
    
        lines = text.split("\n")
        for line in lines:
            result.append(line)
        
        return "\n".join(result)

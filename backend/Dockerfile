FROM python:3.11

WORKDIR /app

COPY requirements.txt .

COPY . .
RUN mkdir -p /app/db

RUN pip install --no-cache-dir -r requirements.txt


ENTRYPOINT [ "python3", "manage.py","runserver","0.0.0.0:80" ]
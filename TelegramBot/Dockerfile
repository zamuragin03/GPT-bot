FROM python:3.10-alpine

WORKDIR /app
RUN apt-get update && apt-get upgrade -y && apt-get install -y
COPY /requirements.txt .
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python3", "app.py", "--build" ]
# syntax=docker/dockerfile:1.4
FROM python:3.10-alpine

WORKDIR /www

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./src ./src

CMD ["python", "./src/bot.py"]
# syntax=docker/dockerfile:1.4
FROM python:3.10-alpine

WORKDIR /www

COPY ./setup.sh .

RUN chmod +x ./setup.sh

COPY ./requirements.txt .

RUN pip install -r ./requirements.txt

COPY ./config.yml .

COPY ./src ./src

CMD ["./setup.sh"]
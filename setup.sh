#!/bin/sh

cd src

alembic revision --autogenerate

alembic upgrade heads

cd /www

python ./src/bot.py
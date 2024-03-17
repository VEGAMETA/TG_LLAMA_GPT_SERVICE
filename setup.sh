#!/bin/sh

cd src

alembic upgrade heads

cd /www

python ./src/bot.py
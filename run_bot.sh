#!/bin/sh
cd ./src
alembic revision --autogenerate
alembic upgrade heads
cd ..
python ./src/bot.py
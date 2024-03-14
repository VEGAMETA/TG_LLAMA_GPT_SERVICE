#!/bin/sh

cd src

alembic upgrade heads

cd ..

python ./src/bot.py
import logging
from src.ollama_bot.misc.yaml_parser import parse_yaml_lines

with open('config.yml') as f:
    lines = f.readlines()

config = parse_yaml_lines(lines)
for key, value in config.items():
    if value == "False":
        config[key] = False

models = config.get('Models', {})
if not models:
    logging.error('Models not found in config')
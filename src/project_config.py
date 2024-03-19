import logging

try:
    from src.ollama_bot.misc.yaml_parser import parse_yaml
except ModuleNotFoundError:
    from ollama_bot.misc.yaml_parser import parse_yaml

try:
    file = open('config.yml')
except FileNotFoundError as _:
    file = open('../config.yml')
finally:
    lines = file.readlines()
    file.close()

config = parse_yaml(lines)
for key, value in config.items():
    if value == "False":
        config[key] = False

models = config.get('Models', {})
if not models:
    logging.error('Models not found in config')

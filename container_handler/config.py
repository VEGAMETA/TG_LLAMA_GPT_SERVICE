from src.ollama_bot.misc.yaml_parser import parse_yaml_lines

with open('config.yml') as f:
    lines = f.readlines()

config = parse_yaml_lines(lines)

from ollama_bot.models.language import Languages

commands = {
    "command_stop": set(),
    "command_help": set(),
    "command_clear": set(),
    "command_set_language": set(),
    "command_set_model": set(),
    "command_subscription": set(),
    "cancel": set(),
}

for language in Languages:
    for command_name, command in language.value.dictionary.items():
        if command_name.startswith("command_") or command_name == "cancel":
            commands.get(command_name).add(command)

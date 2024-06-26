from ollama_bot.misc.language import Languages

commands_f: str = "\n".join((
    "",
    "/stop",
    "/clear",
    "/help",
    "/set_model",
    "/set_language",
    "/subscription",
))

commands: dict[str, set] = {
    "command_stop": set(),
    "command_clear": set(),
    "command_help": set(),
    "command_set_model": set(),
    "command_set_language": set(),
    "command_subscription": set(),
    "cancel": set(),
    "subscription_check": set(),
    "subscription_pay_100": set(),
    "subscription_pay_month": set(),
}

for language in Languages:
    for command_name, command in language.value.dictionary.items():
        if command_name.startswith(("command_", "subscription_")) or command_name == "cancel":
            commands.get(command_name).add(command)

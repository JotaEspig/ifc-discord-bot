import os

import discord

import ifcbot


def main() -> None:
    print(discord.version_info)
    intents = discord.Intents(messages=True, guilds=True, reactions=True,
                              members=True, presences=True, message_content=True)
    bot = ifcbot.BotIFC(command_prefix="!", intents=intents)

    token = os.getenv("IFC_BOT_TOKEN")
    if token == None:
        with open("./token.config", "r") as file:
            token = file.readline();

    bot.run(token)


if __name__ == "__main__":
    main()

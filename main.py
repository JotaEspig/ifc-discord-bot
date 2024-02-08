import os

import discord
from discord.ext import commands

from ifcbot import hello


intents = discord.Intents(messages = True, guilds = True, reactions = True,
                          members = True, presences = True)
client = commands.Bot(command_prefix="$", intents=intents)

@client.event
async def on_ready() -> None:
    await client.change_presence(activity=discord.Game("sexo"))


@commands.command()
async def sexo(ctx) -> None:
    print("aaa")
    await ctx.send("muito sexo")


token = os.getenv("IFC_BOT_TOKEN")
if token == None:
    exit(1)

client.run(token)

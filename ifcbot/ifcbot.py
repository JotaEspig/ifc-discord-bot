import os

import discord
from discord.ext import commands


class BotIFC(commands.Bot):
    async def on_ready(self) -> None:
        await self._load_all_extensions()
        await self.change_presence(activity=discord.Game("Lethal Company"))

    async def _load_all_extensions(self) -> None:
        for filename in os.listdir("./ifcbot/cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"ifcbot.cogs.{filename[:-3]}")

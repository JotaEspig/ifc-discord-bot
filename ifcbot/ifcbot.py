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

    async def missing_role_error(self, ctx: commands.Context, error: commands.MissingRole) -> None:
        role = error.missing_role
        if isinstance(role, str):
            await ctx.reply(f"Missing role: {role}")

        elif isinstance(role, int):
            if ctx.guild != None:
                role = discord.utils.get(ctx.guild.roles, id=role)
                if role != None:
                    await ctx.reply(f"Missing role: {role.name}")
            else:
                await ctx.reply(f"Missing role: {role}")

    async def on_command_error(self, ctx: commands.Context, error, /) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(f":hand_splayed: You are not allowed to use this command\n:hand_splayed: {error}")
        elif isinstance(error, commands.MissingRole):
            await self.missing_role_error(ctx, error)
        else:
            await ctx.author.send(error)

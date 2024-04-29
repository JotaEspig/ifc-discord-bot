import discord
from discord.ext import commands


class Other(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(aliases=["PING"])
    async def ping(self, ctx: commands.Context):
        embed_var = discord.Embed(
            title="Ping",
            description=f"{round(self.bot.latency * 1000)}ms",
            color=0x349a46
        )
        if self.bot.user != None and self.bot.user.avatar != None:
            embed_var.set_thumbnail(url=self.bot.user.avatar.url)

        await ctx.send(embed=embed_var)

    @commands.command()
    async def reply(self, ctx: commands.Context) -> None:
        """ Replies with "{username} é muito gay\""""
        await ctx.message.delete()
        await ctx.send(f"{ctx.author.display_name} é muito gay")

    @commands.command()
    async def say(self, ctx: commands.Context, *, msg: str) -> None:
        await ctx.message.delete()
        await ctx.send(msg)

    @commands.command()
    async def tts(self, ctx: commands.Context, *, msg: str) -> None:
        await ctx.message.delete()
        await ctx.send(msg, tts=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Other(bot))

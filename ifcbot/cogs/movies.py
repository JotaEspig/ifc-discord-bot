import sqlite3
import random

import discord
from discord.ext import commands


class Movies(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.conn = sqlite3.connect("movies.db")
        self.conn.execute("""
                          CREATE TABLE IF NOT EXISTS movies (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              server_id INTEGER,
                              name TEXT,
                              watched INTEGER
                          );
                          """)


    def __del__(self) -> None:
        self.conn.close()


    def guild_id(self, ctx: commands.Context) -> int:
        return ctx.message.guild.id if ctx.message.guild else 0


    @commands.command(aliases=["ADD_MOVIE", "am", "AM"])
    @commands.has_permissions(administrator=True)
    async def add_movie(self, ctx: commands.Context, *, moviename: str):
        cursor = self.conn.cursor()
        cursor = cursor.execute(
                """INSERT INTO "movies" ("server_id", "name", "watched") VALUES (?, ?, ?)""",
                [self.guild_id(ctx), moviename, 0]
        )

        if cursor.lastrowid != 0:
            self.conn.commit()
            await ctx.send(f"Added movie \"{moviename}\"\nMovie ID: {cursor.lastrowid}")

        cursor.close()


    @commands.command(aliases=["PICK_ONE_MOVIE", "pom", "POM"])
    async def pick_one_movie(self, ctx: commands.Context):
        cursor = self.conn.cursor()
        cursor.execute("""SELECT * FROM "movies" WHERE "server_id" = ? AND "watched" = 0 """, [self.guild_id(ctx)])
        movies = cursor.fetchall()

        choosed_row = random.choice(movies)
        movie_id = int(choosed_row[0])
        movie_name = str(choosed_row[2])
        movie_str = f"Picked Movie:\nID: {movie_id} - {movie_name} "
        await ctx.reply(movie_str)
        cursor.close()


    @commands.command(aliases=["LIST_MOVIES", "lm", "LM"])
    async def list_movies(self, ctx: commands.Context, page: int = 1):
        cursor = self.conn.cursor()
        cursor.execute("""SELECT count() as count FROM "movies" WHERE "server_id" = ?""",
                       [self.guild_id(ctx)])
        count = cursor.fetchone()[0]
        cursor.execute("""SELECT * FROM "movies" WHERE "server_id" = ? LIMIT 25 OFFSET ?""",
                       [self.guild_id(ctx), (page - 1) * 25])
        movies = cursor.fetchall()

        embed_title = f"Movies from {ctx.guild.name}" if ctx.guild else "Movies"
        embed = discord.Embed(
            title=embed_title,
            description=f"Page: {page}/{(count - 1) // 25 + 1}",
            color=0x349a46
        )
        if ctx.author.avatar != None:
            embed.set_footer(text=f"Replying: {ctx.author.display_name}", icon_url=ctx.author.avatar.url)

        for row in movies:
            movie_id = int(row[0])
            movie_name = str(row[2])
            has_watched = bool(row[3])
            movie_str = f"ID: {movie_id} - Watched? " \
                        + (":white_check_mark:" if has_watched else ":x:")
            embed.add_field(name=movie_name, value=movie_str, inline=True)

        await ctx.send(embed=embed)
        cursor.close()


    @commands.command(aliases=["LIST_UNWATCHED_MOVIES", "lum", "LUM"])
    async def list_unwatched_movies(self, ctx: commands.Context, page: int = 1):
        cursor = self.conn.cursor()
        cursor.execute("""SELECT count() as count FROM "movies" WHERE "server_id" = ? AND "watched" = 0""",
                       [self.guild_id(ctx)])
        count = cursor.fetchone()[0]
        cursor.execute("""SELECT * FROM "movies" WHERE "server_id" = ? AND watched = 0 LIMIT 25 OFFSET ?""",
                       [self.guild_id(ctx), (page - 1) * 25])
        movies = cursor.fetchall()

        embed_title = f"Unwatched movies from {ctx.guild.name}" if ctx.guild else "Unwatched movies"
        embed = discord.Embed(
            title=embed_title,
            description=f"Page: {page}/{(count - 1) // 25 + 1}",
            color=0x349a46
        )
        if ctx.author.avatar != None:
            embed.set_footer(text=f"Replying: {ctx.author.display_name}", icon_url=ctx.author.avatar.url)

        for row in movies:
            movie_id = int(row[0])
            movie_name = str(row[2])
            movie_str = f"ID: {movie_id}"
            embed.add_field(name=movie_name, value=movie_str, inline=True)

        await ctx.send(embed=embed)
        cursor.close()


    @commands.command(aliases=["WATCH_MOVIE", "wm", "WM"])
    @commands.has_permissions(administrator=True)
    async def watch_movie(self, ctx: commands.Context, movie_id: int):
        cursor = self.conn.cursor()
        cursor.execute("""UPDATE "movies" SET watched = 1 WHERE server_id = ? AND id = ?""",
                       [self.guild_id(ctx), movie_id])
        if cursor.rowcount > 0:
            self.conn.commit()
            await ctx.message.add_reaction("✅")

        cursor.close()


    @commands.command(aliases=["REMOVE_MOVIE", "rmm", "RMM"])
    @commands.has_permissions(administrator=True)
    async def remove_movie(self, ctx: commands.Context, movie_id: int):
        cursor = self.conn.cursor()
        cursor.execute("""DELETE FROM "movies" WHERE server_id = ? AND id = ?""",
                       [self.guild_id(ctx), movie_id])
        if cursor.rowcount > 0:
            self.conn.commit()
            await ctx.message.add_reaction("✅")

        cursor.close()


    @commands.command(aliases=["REMOVE_ALL_MOVIES", "rmmall", "RMMALL"])
    @commands.has_permissions(administrator=True)
    async def remove_all_movies(self, ctx: commands.Context):
        cursor = self.conn.cursor()
        cursor.execute("""DELETE FROM "movies" WHERE server_id = ?""",
                       [self.guild_id(ctx)])
        if cursor.rowcount > 0:
            self.conn.commit()
            await ctx.message.add_reaction("✅")

        cursor.close()


async def setup(bot: commands.Bot):
    await bot.add_cog(Movies(bot))

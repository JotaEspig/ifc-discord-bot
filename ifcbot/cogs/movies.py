import sqlite3
import random
from time import sleep
from typing import Union

import discord
from discord.ext import commands


class Movies(commands.Cog):
    poll_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣",
                   "8️⃣", "9️⃣"]

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.conn = sqlite3.connect("movies.db")
        self.conn.execute("""
                          CREATE TABLE IF NOT EXISTS "movies" (
                              "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                              "server_id" INTEGER,
                              "name" TEXT,
                              "watched" INTEGER
                          )
                          """)
        self.conn.execute("""
                          CREATE TABLE IF NOT EXISTS "servers_roles" (
                              "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                              "server_id" INTEGER,
                              "role_id" INTEGER
                          )
                          """)

    def __del__(self) -> None:
        self.conn.close()

    def guild_id(self, ctx: commands.Context) -> int:
        return ctx.message.guild.id if ctx.message.guild else 0

    def check_role(self, ctx: commands.Context) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("""SELECT "role_id" FROM "servers_roles" WHERE "server_id" = ?""",
                       [self.guild_id(ctx)])
        row = cursor.fetchone()
        if row == None or len(row) == 0:
            cursor.close()
            return False

        role_id = row[0]
        if isinstance(ctx.author, discord.Member):
            if ctx.author.get_role(role_id) == None:
                cursor.close()
                raise commands.MissingRole(role_id)

        cursor.close()
        return True

    @commands.command(aliases=["SETUP_MOVIES", "sm", "Sm", "SM"])
    @commands.has_permissions(administrator=True)
    async def setup_movies(self, ctx: commands.Context, role: discord.Role):
        cursor = self.conn.cursor()
        cursor.execute("""SELECT count() FROM "servers_roles" WHERE "server_id" = ?""", [
                       self.guild_id(ctx)])
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute("""INSERT INTO "servers_roles" ("server_id", "role_id") VALUES (?, ?)""",
                           [self.guild_id(ctx), role.id])
        else:
            cursor.execute("""UPDATE "servers_roles" SET "role_id" = ? WHERE "server_id" = ?""",
                           [role.id, self.guild_id(ctx)])

        if cursor.rowcount > 0:
            self.conn.commit()
            await ctx.message.add_reaction("✅")
        else:
            await ctx.message.add_reaction("❌")

        cursor.close()

    @commands.command(aliases=["POLL_MOVIES", "pm", "Pm", "PM"])
    @commands.has_permissions(administrator=True)
    async def poll_movies(self, ctx: commands.Context, amount: int = 4) -> None:
        ok = self.check_role(ctx)
        if not ok:
            await ctx.message.add_reaction("❌")
            await ctx.reply("You should use \"!setup_movies\" first")
            return

        if amount > 9:
            await ctx.send("Invalid amount")
            return

        cursor = self.conn.cursor()
        cursor.execute("""SELECT "name" FROM "movies" WHERE "server_id" = ? AND "watched" = 0""", [
                       self.guild_id(ctx)])
        movies = cursor.fetchall()
        choosed_movies = random.sample(movies, amount)
        embed = discord.Embed(
            title="Choose the movie!",
            color=0x349a46
        )
        for i in range(amount):
            row = choosed_movies[i]
            emoji = self.poll_emojis[i]
            movie_name = row[0]
            embed.add_field(name=movie_name, value=emoji, inline=False)

        msg = await ctx.send(embed=embed)
        for i in range(amount):
            await msg.add_reaction(self.poll_emojis[i])

        cursor.close()

    @commands.command(aliases=["ADD_MOVIE", "am", "Am", "AM"])
    async def add_movie(self, ctx: commands.Context, *, moviename: str):
        ok = self.check_role(ctx)
        if not ok:
            await ctx.message.add_reaction("❌")
            await ctx.reply("You should use \"!setup_movies\" first")
            return

        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO "movies" ("server_id", "name", "watched") VALUES (?, ?, ?)""",
            [self.guild_id(ctx), moviename, 0]
        )

        if cursor.lastrowid != 0:
            self.conn.commit()
            await ctx.send(f"Added movie \"{moviename}\"\nMovie ID: {cursor.lastrowid}")

        cursor.close()

    @commands.command(aliases=["PICK_ONE_MOVIE", "pom", "Pom", "POM"])
    async def pick_one_movie(self, ctx: commands.Context, seconds: int = 0):
        cursor = self.conn.cursor()
        cursor.execute(
            """SELECT * FROM "movies" WHERE "server_id" = ? AND "watched" = 0 """, [self.guild_id(ctx)])
        movies = cursor.fetchall()

        choosed_row = random.choice(movies)
        movie_id = int(choosed_row[0])
        movie_name = str(choosed_row[2])
        movie_str = f"Picked Movie:\nID: {movie_id} - **{movie_name}**"

        if seconds > 0:
            await ctx.send(f"Revealing in {seconds} seconds")
        while seconds > 0:
            await ctx.send(f"{seconds}...")
            sleep(1)
            seconds -= 1

        await ctx.send(movie_str)
        cursor.close()

    @commands.command(aliases=["LIST_MOVIES", "lm", "Lm", "LM"])
    async def list_movies(self, ctx: commands.Context, page: int = 1):
        cursor = self.conn.cursor()
        cursor.execute("""SELECT count() FROM "movies" WHERE "server_id" = ?""",
                       [self.guild_id(ctx)])
        count = cursor.fetchone()[0]
        cursor.execute("""SELECT * FROM "movies" WHERE "server_id" = ? LIMIT 25 OFFSET ?""",
                       [self.guild_id(ctx), (page - 1) * 25])
        movies = cursor.fetchall()

        embed_title = f"Movies from {
            ctx.guild.name}" if ctx.guild else "Movies"
        embed = discord.Embed(
            title=embed_title,
            description=f"Page: {page}/{(count - 1) // 25 + 1}",
            color=0x349a46
        )
        if ctx.author.avatar != None:
            embed.set_footer(text=f"Replying: {
                             ctx.author.display_name}", icon_url=ctx.author.avatar.url)

        for row in movies:
            movie_id = int(row[0])
            movie_name = str(row[2])
            has_watched = bool(row[3])
            movie_str = f"ID: {movie_id} - Watched? " \
                + (":white_check_mark:" if has_watched else ":x:")
            embed.add_field(name=movie_name, value=movie_str, inline=True)

        await ctx.send(embed=embed)
        cursor.close()

    @commands.command(aliases=["LIST_UNWATCHED_MOVIES", "lum", "Lum", "LUM"])
    async def list_unwatched_movies(self, ctx: commands.Context, page: int = 1):
        cursor = self.conn.cursor()
        cursor.execute("""SELECT count() FROM "movies" WHERE "server_id" = ? AND "watched" = 0""",
                       [self.guild_id(ctx)])
        count = cursor.fetchone()[0]
        cursor.execute("""SELECT * FROM "movies" WHERE "server_id" = ? AND watched = 0 LIMIT 25 OFFSET ?""",
                       [self.guild_id(ctx), (page - 1) * 25])
        movies = cursor.fetchall()

        embed_title = f"Unwatched movies from {
            ctx.guild.name}" if ctx.guild else "Unwatched movies"
        embed = discord.Embed(
            title=embed_title,
            description=f"Page: {page}/{(count - 1) // 25 + 1}",
            color=0x349a46
        )
        if ctx.author.avatar != None:
            embed.set_footer(text=f"Replying: {
                             ctx.author.display_name}", icon_url=ctx.author.avatar.url)

        for row in movies:
            movie_id = int(row[0])
            movie_name = str(row[2])
            movie_str = f"ID: {movie_id}"
            embed.add_field(name=movie_name, value=movie_str, inline=True)

        await ctx.send(embed=embed)
        cursor.close()

    @commands.command(aliases=["WATCH_MOVIE", "wm", "Wm", "WM"])
    @commands.has_permissions(administrator=True)
    async def watch_movie(self, ctx: commands.Context, movie_id: int):
        cursor = self.conn.cursor()
        cursor.execute("""UPDATE "movies" SET watched = 1 WHERE server_id = ? AND id = ?""",
                       [self.guild_id(ctx), movie_id])
        if cursor.rowcount > 0:
            self.conn.commit()
            await ctx.message.add_reaction("✅")

        cursor.close()

    @commands.command(aliases=["REMOVE_MOVIE", "rmm", "Rmm", "RMM"])
    @commands.has_permissions(administrator=True)
    async def remove_movie(self, ctx: commands.Context, movie_id: int):
        cursor = self.conn.cursor()
        cursor.execute("""DELETE FROM "movies" WHERE server_id = ? AND id = ?""",
                       [self.guild_id(ctx), movie_id])
        if cursor.rowcount > 0:
            self.conn.commit()
            await ctx.message.add_reaction("✅")

        cursor.close()

    @commands.command(aliases=["REMOVE_ALL_MOVIES", "rmmall", "Rmmall", "RMMALL"])
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

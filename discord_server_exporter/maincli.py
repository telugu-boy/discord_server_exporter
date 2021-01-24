"""
    Discord Server Exporter - exports and import servers as json
    Copyright (C) 2021 telugu_boy

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import json
import logging

# This is the CLI for Discord Server Exporter.
from discord.ext import commands

bot = commands.Bot(command_prefix=">", description="")

import discord_server_exporter as dse


@bot.command()
async def req_dump(ctx):
    await ctx.send("sent")


guildid = None
# Events
@bot.event
async def on_ready():
    if not os.path.exists("my_servers"):
        os.mkdir("my_servers")
    for gld in bot.guilds:
        biswas = dse.dump_server(gld)
        with open(f"my_servers/{biswas['name']}.json", "w") as f:
            f.write(json.dumps(biswas))
    logging.info("Bot started")


@bot.listen()
async def on_message(message):
    print(message.content)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    with open("token.txt") as f:
        tok, gid = map(lambda a: a.strip(), f.readlines())
    guildid = int(gid)
    bot.run(tok, bot=False)

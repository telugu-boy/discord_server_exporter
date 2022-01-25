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
import re
import json
import logging

import discord
from discord.ext import commands

import discord_server_exporter as dse
import discord_server_importer as dsi

intents = discord.Intents.all()
bot = discord.Client(intents=intents)

LOG_FILENAME = "import_log.log"
LOG_LEVEL = logging.INFO
LOG_FILE_MODE = "w"
LOG_FORMAT = "[%(levelname)s] %(asctime)s %(name)s: %(message)s"
LOG_DATE_FORMAT = "[%Y/%m/%d %H:%M:%S]"

guildid = None
# Events
@bot.event
async def on_ready():
    logging.info("Bot started")

    gld = bot.get_guild(guildid)
    dse.write_emojis_to_dir(gld)
    
    logging.info("All OK")


if __name__ == "__main__":
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    with open("token.txt") as f:
        tok, gid = map(lambda a: a.strip(), f.readlines())
    guildid = int(gid)
    bot.run(tok, bot=False)

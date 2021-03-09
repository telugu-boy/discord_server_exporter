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

# This file is meant to be run as an example of discord_server_exporter module.

# Token is to be supplied in token.txt on the first line
# Change below variable accordingly.
IS_BOT_TOKEN = False

# Once ran, a folder named `my_servers` will be created
# With all the layout of the servers in their own files.
# There will also be a file named after the ID of the bot user
# containing the layout of each server .

# The resulting files can be imported with discord_server_importer.py
# Schema of the server is in the schemas folder, as with other relevant structures
# should you wish to export individual parts.

# Notice: exporting members with a user token does not work.
# Warning: selfbotting is against Discord TOS.

import os
import re
import json
import time
import logging

import discord
from discord.ext import commands

import discord_server_exporter as dse

intents = discord.Intents.all()
bot = discord.Client(intents=intents)

LOG_FILENAME = "export_log.log"
LOG_LEVEL = logging.INFO
LOG_FILE_MODE = "w"
LOG_FORMAT = "[%(levelname)s] %(asctime)s %(name)s: %(message)s"
LOG_DATE_FORMAT = "[%Y/%m/%d %H:%M:%S]"

guildid = None
# Events
@bot.event
async def on_ready():
    logging.info("Bot started")

    if not os.path.exists("my_servers"):
        os.mkdir("my_servers")

    servers = []
    export_files_dir = f"exported_{int(time.time())}"
    for gld in bot.guilds:
        biswas = dse.dump_server(
            gld, export_files_dir=export_files_dir
        )  # Exporting members does not work due to intents      "
        servers.append(biswas)
        srv_name_clean = re.sub(
            r"\W+", "", biswas["name"]
        )  # To clean out any characters except alphanumeric and _
        with open(f"my_servers/{srv_name_clean}.json", "w") as f:
            f.write(json.dumps(biswas))

    with open(f"my_servers/{bot.user.id}.json", "w") as f:
        f.write(json.dumps(servers))

    logging.info("All OK")


if __name__ == "__main__":
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    with open("token.txt") as f:
        tok, gid = map(lambda a: a.strip(), f.readlines())
    guildid = int(gid)
    bot.run(tok, bot=IS_BOT_TOKEN)

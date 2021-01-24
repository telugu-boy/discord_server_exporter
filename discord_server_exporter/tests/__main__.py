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

import logging

from . import role_schema_test, emoji_schema_test, text_channel_schema_test, voice_channel_schema_test, category_schema_test, server_schema_test
from discord.ext import commands

import json
import pathlib
import jsonschema

import discord
import discord_server_exporter as dse

bot = commands.Bot(command_prefix=">", description="")

guildid = None


@bot.event
async def on_ready():
    logging.info("Bot started")
    gld = bot.get_guild(guildid)
    role_schema_test.test_role_schema_validation(gld)
    emoji_schema_test.test_emoji_schema_validation(gld)
    text_channel_schema_test.test_text_channel_schema_validation(gld)
    voice_channel_schema_test.test_voice_channel_schema_validation(gld)
    category_schema_test.test_category_schema_validation(gld)
    server_schema_test.test_server_schema_validation(gld)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    logging.info("Running all tests")

    print(pathlib.Path().absolute())

    # Getting creds and target test server
    with open("token.txt") as f:
        tok, gid = map(lambda a: a.strip(), f.readlines())
    guildid = int(gid)

    bot.run(tok)

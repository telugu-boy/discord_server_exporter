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
import jsonschema
import logging

import discord
import discord_server_exporter as dse


def test_text_channel_schema_validation(gld: discord.Guild):
    logging.info("Running text channel schema validation test")

    text_channel_schema_path = "schemas/text_channel_schema.json"
    with open(text_channel_schema_path) as f:
        text_channel_schema = json.load(f)

    resolver = jsonschema.RefResolver(
        "file:///" + os.getcwd() + "/schemas/", text_channel_schema
    )

    biswas = dse.dump_text_channels(gld)

    for text_channel in biswas:
        jsonschema.validate(text_channel, text_channel_schema, resolver=resolver)

    logging.info("OK")
    logging.info("Validate text channels foregoing role permissions export")

    biswas = dse.dump_text_channels(gld, False, True)

    for text_channel in biswas:
        jsonschema.validate(text_channel, text_channel_schema, resolver=resolver)

    logging.info("OK")
    logging.info("Validate text channels foregoing user permissions export")

    biswas = dse.dump_text_channels(gld, True, False)

    for text_channel in biswas:
        jsonschema.validate(text_channel, text_channel_schema, resolver=resolver)

    logging.info("OK")
    logging.info("Validate text channels foregoing both permissions export")

    biswas = dse.dump_text_channels(gld, False, False)

    for text_channel in biswas:
        jsonschema.validate(text_channel, text_channel_schema, resolver=resolver)

    logging.info("OK")

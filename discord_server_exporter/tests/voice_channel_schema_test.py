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


def test_voice_channel_schema_validation(gld: discord.Guild):
    logging.info("Running voice channel schema validation test")

    voice_channel_schema_path = "schemas/voice_channel_schema.json"
    with open(voice_channel_schema_path) as f:
        voice_channel_schema = json.load(f)

    resolver = jsonschema.RefResolver(
        "file:///" + os.getcwd() + "/schemas/", voice_channel_schema
    )

    biswas = dse.dump_voice_channels(gld)

    for voice_channel in biswas:
        jsonschema.validate(voice_channel, voice_channel_schema, resolver=resolver)

    logging.info("OK")
    logging.info("Validate voice_channels foregoing role permissions export")

    biswas = dse.dump_voice_channels(gld, False, True)

    for voice_channel in biswas:
        jsonschema.validate(voice_channel, voice_channel_schema, resolver=resolver)

    logging.info("OK")
    logging.info("Validate voice_channels foregoing user permissions export")

    biswas = dse.dump_voice_channels(gld, True, False)

    for voice_channel in biswas:
        jsonschema.validate(voice_channel, voice_channel_schema, resolver=resolver)

    logging.info("OK")
    logging.info("Validate voice_channels foregoing both permissions export")

    biswas = dse.dump_voice_channels(gld, False, False)

    for voice_channel in biswas:
        jsonschema.validate(voice_channel, voice_channel_schema, resolver=resolver)

    logging.info("OK")

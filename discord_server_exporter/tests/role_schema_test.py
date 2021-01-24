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

async def test_role_schema_validation(gld: discord.Guild):
    logging.info("Running role schema validation test")

    biswas = await dse.dump_roles(gld)

    role_schema_path = "schemas/role_schema.json"
    with open(role_schema_path) as f:
        role_schema = json.load(f)

    resolver = jsonschema.RefResolver("file:///" + os.getcwd() + "/schemas/", role_schema)

    for role in biswas:
        jsonschema.validate(role, role_schema, resolver=resolver)

    logging.info("OK")

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


def test_member_schema_validation(gld: discord.Guild):
    logging.info("Running member schema validation test")

    member_schema_path = "schemas/member_schema.json"
    with open(member_schema_path) as f:
        member_schema = json.load(f)

    resolver = jsonschema.RefResolver(
        "file:///" + os.getcwd() + "/schemas/", member_schema
    )

    biswas = dse.dump_members(gld)

    for member in biswas:
        jsonschema.validate(member, member_schema, resolver=resolver)

    logging.info("OK")
    logging.info("Validate members foregoing nickname export")

    biswas = dse.dump_members(gld, False, True)
    for member in biswas:
        jsonschema.validate(member, member_schema, resolver=resolver)

    logging.info("OK")
    logging.info("Validate members foregoing roles export")

    biswas = dse.dump_members(gld, True, False)
    for member in biswas:
        jsonschema.validate(member, member_schema, resolver=resolver)

    logging.info("OK")
    logging.info("Validate members foregoing both export")

    biswas = dse.dump_members(gld, False, False)
    for member in biswas:
        jsonschema.validate(member, member_schema, resolver=resolver)

    logging.info("OK")

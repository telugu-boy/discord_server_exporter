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


def test_category_schema_validation(gld: discord.Guild):
    logging.info("Running categories schema validation test")

    category_schema_path = "schemas/category_schema.json"
    with open(category_schema_path) as f:
        category_schema = json.load(f)

    resolver = jsonschema.RefResolver(
        "file:///" + os.getcwd() + "/schemas/", category_schema
    )

    biswas = dse.dump_categories(gld)

    for category in biswas:
        jsonschema.validate(category, category_schema, resolver=resolver)

    logging.info("OK")
    logging.info("Validate categories foregoing role permissions export")

    biswas = dse.dump_categories(gld, False, True)

    for category in biswas:
        jsonschema.validate(category, category_schema, resolver=resolver)

    logging.info("OK")
    logging.info("Validate categories foregoing user permissions export")

    biswas = dse.dump_categories(gld, True, False)

    for category in biswas:
        jsonschema.validate(category, category_schema, resolver=resolver)

    logging.info("OK")
    logging.info("Validate categories foregoing both permissions export")

    biswas = dse.dump_categories(gld, False, False)

    for category in biswas:
        jsonschema.validate(category, category_schema, resolver=resolver)

    logging.info("OK")

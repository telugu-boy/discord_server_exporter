"""
    Discord Server Exporter - exports and import servers as json
    Copyright (C) 2021 telugu_boy

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
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
from urllib.request import urlopen

import discord
import jsonschema

"""
Creates a guild with a dictionary conforming to the server schema
The schema for server is in the schemas folder, as with all other relevant structures

Arguments:
    bot -- a discord.py client object. AutoShardedClient has not been tested.
    server -- a discord.py guild object

Exceptions:
    Server unable to be created. Return value `None`
    Invalid server dict. Exception thrown.
"""


async def create_server(bot: discord.Client, server: dict):
    logging.info("Validating server JSON...")

    server_schema_path = "schemas/server_schema.json"
    with open(server_schema_path) as f:
        server_schema = json.load(f)

    # We need this for the json pointers in the schemas to work
    resolver = jsonschema.RefResolver(
        "file:///" + os.getcwd() + "/schemas/", server_schema
    )

    # Validate the server dict
    jsonschema.validate(server, server_schema, resolver=resolver)

    logging.info(f"OK: server name \"{server['name']}\"")

    # Download the server icon. The icon argument for create_guild takes a bytes-like object
    with urlopen(server["icon_url"]) as f:
        server_icon_bytes = f.read()

    # A bot account in over 10 guilds cannot create guilds and will throw an HTTPException
    # We have no way of verifying if `bot` is a real bot or a user account
    try:
        await bot.create_guild(
            server["name"], region=server["voice_region"], icon=server_icon_bytes
        )
    except discord.HTTPException:
        logging.critical(
            """
        Could not create guild.
            Known problem: Bot accounts in more than 10 guilds are not allowed to create guilds.
            Solution: use `overwrite_server`

            Known problem: User is in too many guilds
            Solution: leave a guild or use alternate account or use `overwrite_server`
        """
        )
        return None

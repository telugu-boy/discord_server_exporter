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

import os
import json
import logging
from urllib.request import Request, urlopen

import discord
import jsonschema

"""
Gets a server icon under 10mb if the original is over

Return: bytes-like object with the downloaded icon

Arguments:
    url -- URL to the server icon
"""


def get_icon_under_10mb(url: str):
    # This header is needed or else we get 403 forbidden '-'
    # The user agent and accept* are copied from a random Chrome request
    hdr = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }

    icon_sizes = (2048, 1024, 512, 256, 128)

    # Sorted in ascending order of size.  GIFs are added to the front
    # if the supplied URL points to a GIF.
    formats = ["webp", "jpg", "png"]

    # Try original first
    req = Request(url, None, hdr)
    server_icon_req = urlopen(req)

    # file cannot be larger than 10240.0 kb
    if int(server_icon_req.info()["Content-Length"]) > 10240000:
        logging.warning(
            "Original server icon larger than 10.240MB limit. Searching for smaller..."
        )
    else:
        return server_icon_req.read()

    # to determine if GIF or not
    # Icons are of the format `URL.ext?size=xxx`
    # after the last dot and before the first exclamation mark is
    # where the extension lies.
    icon_ext = url.split(".")[-1].split("?")[0]

    # GIFs are not processed for non animated icons, so accessing it would give
    # an error
    if icon_ext == "gif":
        formats.insert(0, "gif")

    # The URL without an extension or size.
    icon_url_no_ext = ".".join(url.split(".")[:-1])

    # We want the highest resolution images, so try 2048 on all formats and
    # then the next highest size 1024 and so on
    for icon_size in icon_sizes:
        for format in formats:
            logging.info(f"Trying {format} and {icon_size}")

            candidate_icon_url = f"{icon_url_no_ext}.{format}?size={icon_size}"
            req = Request(candidate_icon_url, None, hdr)
            server_icon_req = urlopen(req)

            file_size = int(server_icon_req.info()["Content-Length"])
            # not <= just to be safe '-'
            if file_size < 10240000:
                logging.info(
                    f"Found suitable icon with extension {format}, resolution {icon_size} ({file_size}b)"
                )
                return server_icon_req.read()


"""
Converts a role dict to a discord.py create_role compatible kwargs dict.

Arguments:
    role_dict -- a dict representing a role as specified by role_schema.json
"""


def role_dict_to_dpy(role_dict: dict):
    res = {}
    res["name"] = role["name"]
    res["color"] = int(role["color"])
    res["mentionable"] = bool(role["mentionable"])
    res["permissions"] = int(role["permission_value"])
    res["position"] = int(role["position"])
    res["hoisted"] = bool(role["hoisted"])
    return res


"""
Append roles to the end of the heirarchy.
This will truncate roles if they cannot fit.
This will not touch the @everyone role.

Arguments:
    bot -- a discord.py client object.
    existing_guild -- the target guild.
    server -- a discord server dict following the server schema
"""


async def append_roles(
    bot: discord.Client,
    existing_guild: discord.Guild,
    server: dict,
    overwrite_prompt=True,
):
    # See comment of `write_roles`
    free_spaces_left = 251 - len(existing_guild.roles)
    logging.info(
        f"{free_spaces_left} role spaces available for server '{existing_guild.name}'"
    )

    if overwrite_prompt and len(server["roles"]) > free_spaces_left:
        logging.warning(
            "Not enough free role spaces left for server '{existing_guild.name}'"
        )
        inp = input(
            f"""
        There are too many roles to fit in server '{existing_guild.name}'.
        The bottom {len(server["roles"]) - free_spaces_left - 1} roles will not be added.
        Use `write_roles` to overwrite roles.
        Y/n : """
        ).lower()

        if inp[0] == "y":
            logging.info("Append roles for server '{existing_guild.name}'")
        else:
            logging.info("Abort append_roles for server '{existing_guild.name}'")

    # We need to sort the roles so they are in the correct position
    sorted_server_roles = sorted(
        server["roles"], key=lambda role: int(role["position"])
    )

    for role in range(free_spaces_left):
        logging.info(f"Appending role '{role.name}' for server '{existing_guild.name}'")
        await existing_guild.create_role(
            **role_dict_to_dpy(role), reason="Automatic role appending"
        )


"""
Overwrites roles starting from the role below the highest role of the client.
This will overwrite ALL roles and DELETE remaining ones if the client is the owner of existing_guild.

Arguments:
    bot -- a discord.py client object.
    existing_guild -- the target guild.
    server -- a discord server dict following the server schema
"""


async def write_roles(
    bot: discord.Client,
    existing_guild: discord.Guild,
    server: dict,
    overwrite_prompt=True,
):
    # We need `len(server["roles"])` of free spaces for roles.
    # As discord has a role limit of 250 + @everyone, `251 - len(existing_guild.roles)`
    # is the amount of free spaces left.  Issue an input() to ask user
    free_spaces_left = 251 - len(existing_guild.roles)
    logging.info(
        f"{free_spaces_left} role spaces available for server '{existing_guild.name}'"
    )

    if overwrite_prompt and len(server["roles"]) > free_spaces_left:
        logging.warning(
            "Not enough free role spaces left for server '{existing_guild.name}'"
        )
        inp = input(
            f"""
        There are too many roles to fit in server '{existing_guild.name}'.
        Continuing to write roles will destroy all roles starting from the highest role of the user/bot.
        Use `append_roles` to add roles to the end of the heirarchy.
        Y/n : """
        ).lower()

        if inp[0] == "y":
            logging.info(
                "Overwrite roles under highest role of client for server '{existing_guild.name}'"
            )
        else:
            logging.info("Abort write_roles for server '{existing_guild.name}'")
            return None

    # We need to sort the roles so they are in the correct position
    sorted_server_roles = sorted(
        server["roles"], key=lambda role: int(role["position"])
    )

    amt_to_write = min(len(existing_guild.roles), len(sorted_server_roles))
    # Overwriting
    for idx in range(amt_to_write):
        logging.info(
            f"Writing role '{sorted_server_roles[idx].name}' in place of role '{role.name}' for server '{existing_guild.name}'"
        )

        await role.edit(
            **role_dict_to_dpy(sorted_server_roles[idx]),
            reason="Automatic role writing",
        )

    # Appending
    if len(sorted_server_roles) > len(existing_guild.roles):
        # amount of roles left (to write)
        amt_roles_left = len(sorted_server_roles) - len(existing_guild.roles)
        for i in range(amt_to_write, amt_roles_left):
            role = sorted_server_roles[i]
            logging.info(
                f"Appending role '{role.name}' for server '{existing_guild.name}'"
            )
            await existing_guild.create_role(
                **role_dict_to_dpy(role), reason="Automatic role appending"
            )
    # Erasing
    else:
        amt_roles_to_erase = len(existing_guild.roles) - len(sorted_server_roles)
        for i in range():
            pass


"""
Creates a guild with a dictionary conforming to the server schema
The schema for server is in the schemas folder, as with all other relevant structures

Arguments:
    bot -- a discord.py client object. AutoShardedClient has not been tested.
    server -- a discord server dict following the server schema

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

    # Download the server icon.  The icon argument for create_guild takes a
    # bytes-like object
    logging.info("Downloading server icon...")

    try:
        # Server icon cannot be over 10.240MB
        server_icon_bytes = get_icon_under_10mb(server["icon_url"])
    except discord.errors.HTTPException:
        logging.error("Could not download server icon, falling back to default")
        server_icon_bytes = None

    # A bot account in over 10 guilds cannot create guilds and will throw an
    # HTTPException
    # We have no way of verifying if `bot` is a real bot or a user account
    try:
        new_guild = await bot.create_guild(
            server["name"],
            region=discord.VoiceRegion(server["voice_region"]),
            icon=server_icon_bytes,
        )
    except discord.errors.HTTPException as e:

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

    # After the server is created, we can add the roles and stuff with other functions
    # which can be used in  `overwrite_server`
    # first: roles
    await write_roles(bot, new_guild, server)
    # second: categories, for synced perms

    # third: channels, for perm overrides

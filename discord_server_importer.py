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
import asyncio
import threading
from urllib.request import Request, urlopen

import discord
import jsonschema

from ds_common_funcs import req_hdr, get_icon_under_10mb, boost_emoji_count

"""
Append emojis to the end of the collection.
This will not add the last emojis passed in if they cannot fit.
This will append emojis in the order they are passed.

Arguments:
    bot -- a discord.py client object.
    existing_guild -- the target guild.
    emojis -- a discord emoji list, each element following the emoji schema
"""


async def append_emojis(
    existing_guild: discord.Guild, emojis: list, import_folder="", append_prompt=True
):
    logging.info(f"Appending emojis for server '{existing_guild.name}'")
    amt_existing_emojis = len(existing_guild.emojis)
    amt_emoji_slots = boost_emoji_count[existing_guild.premium_tier]
    # premium tier is an int
    free_spaces_left = amt_emoji_slots - amt_existing_emojis

    logging.info(
        f"{free_spaces_left} emoji spaces available for server '{existing_guild.name}'"
    )

    if append_prompt and amt_existing_emojis > free_spaces_left:
        logging.warning(
            f"Not enough free emoji spaces left for server ' {existing_guild.name}'"
        )
        inp = input(
            f"""
        There are too many emojis to fit in server '{existing_guild.name}'.
        The bottom {len(emojis) - free_spaces_left} emojis will not be added.
        Use `write_emojis` to completely replace emojis.
        Y/n : """
        ).lower()

        if inp[0] == "y":
            logging.info(f"Append emojis for server '{existing_guild.name}'")
        else:
            logging.info(f"Abort append_emojis for server '{existing_guild.name}'")
            return None

    emoji_download = None

    for emoji in emojis:

        if import_folder:
            gemojidir = f"{import_folder}/emojis/{existing_guild.id}/"
            files = [f for f in os.listdir(gemojidir) if f.startwith(emoji["name"])]
            if len(files) == 0:
                logging.warning(f"Emoji file not found in import folder '{gemojidir}', skipping")
                continue
            with open(files[0]) as f:
                emoji_download = f.read()
        else:
            req = Request(emoji["url"], None, req_hdr)
            emoji_req = urlopen(req)

            file_size = int(emoji_req.info()["Content-Length"])
            # 256kb limit
            if file_size > 256000:
                logging.info(
                    f"Emoji '{emoji['name']}' is {file_size}b > 256kb and will be skipped."
                )
                continue

            emoji_download = emoji_req.read()


        logging.info(
            f"Downloaded and appending emoji '{emoji['name']}' ({file_size}b) for server '{existing_guild.name}'"
        )

        await existing_guild.create_custom_emoji(
            name=emoji["name"], image=emoji_download, reason="Automatic emoji appending"
        )


"""
Delete all emojis and then call `append_emojis`.
This will write emojis in the order they are passed.

Arguments:
    bot -- a discord.py client object.
    existing_guild -- the target guild.
    emojis -- a discord emoji list, each element following the emoji schema
"""


async def write_emojis(
    existing_guild: discord.Guild, emojis: list, import_folder="", overwrite_prompt=True,
):
    logging.info(f"Writing emojis for server '{existing_guild.name}'")
    if overwrite_prompt:
        inp = input(
            f"""
        Continuing to write emojis will destroy all emojis and replace them with the supplied list.
        Use `append_emojis` to add emojis to the collection.
        Y/n : """
        ).lower()

        if inp[0] == "y":
            logging.info(
                f"Overwrite emojis under highest role of client for server '{existing_guild.name}'"
            )
        else:
            logging.info(f"Abort write_emojis for server '{existing_guild.name}'")
            return None

    for emoji in existing_guild.emojis:
        logging.info(f"Delete emoji '{emoji.name}' for server '{existing_guild.name}'")
        await emoji.delete()

    logging.info(f"Pass control to `append_emojis` for server '{existing_guild.name}'")
    await append_emojis(existing_guild.emojis, import_folder, False)


"""
Converts a role dict to a discord.py create_role compatible kwargs dict.

Arguments:
    role -- a dict representing a role as specified by role_schema.json
"""


def role_dict_to_dpy(role: dict):
    res = {}
    res["name"] = role["name"]
    res["color"] = role["color"]
    res["mentionable"] = bool(role["mentionable"])
    res["permissions"] = discord.Permissions(int(role["permission_value"]))
    res["position"] = int(role["position"])
    res["hoist"] = bool(role["hoist"])
    return res


"""
Checks if a role's attributes (listed in the schema, excluding id) are equal, specifically:
    color
    hoist
    mentionable
    name
    permission_value

Arguments:
    role_dpy -- a discord.py role object
    role_dict -- a dict representing a role as specified by role_schema.json
"""


def check_roles_equal(role_dpy: discord.Role, role_dict: dict):
    return (
        role_dpy.color.value == role_dict["color"]
        and role_dpy.hoist == role_dict["hoist"]
        and role_dpy.mentionable == role_dict["mentionable"]
        and role_dpy.name == role_dict["name"]
        and role_dpy.permissions.value == int(role_dict["permission_value"])
    )


"""
Append roles to the end of the heirarchy.
This will truncate roles if they cannot fit.
This will not touch the @everyone role.

Arguments:
    bot -- a discord.py client object.
    existing_guild -- the target guild.
    roles -- a discord roles list, each element following the role schema
"""


async def append_roles(existing_guild: discord.Guild, roles: list, append_prompt=True):
    logging.info(f"Appending roles for server '{existing_guild.name}'")
    # See comment of `write_roles`
    free_spaces_left = 250 - len(existing_guild.roles)
    logging.info(
        f"{free_spaces_left} role spaces available for server '{existing_guild.name}'"
    )

    if append_prompt and len(roles) > free_spaces_left:
        logging.warning(
            f"Not enough free role spaces left for server '{existing_guild.name}'"
        )
        inp = input(
            f"""
        There are too many roles to fit in server '{existing_guild.name}'.
        The bottom {len(roles) - free_spaces_left - 1} roles will not be added.
        Use `write_roles` to overwrite roles.
        Y/n : """
        ).lower()

        if inp[0] == "y":
            logging.info(f"Append roles for server '{existing_guild.name}'")
        else:
            logging.info(f"Abort append_roles for server '{existing_guild.name}'")
            return None

    # We need to sort the roles so they are in the correct position
    # Pop off the last one because we do not want @everyone
    sorted_server_roles = list(
        reversed(sorted(roles, key=lambda role: int(role["position"])))
    )[:-1]

    for role in sorted_server_roles:
        logging.info(
            f"Appending role '{role['name']}' for server '{existing_guild.name}'"
        )
        dpy_role = role_dict_to_dpy(role)
        del dpy_role["position"]
        await existing_guild.create_role(**dpy_role, reason="Automatic role appending")


"""
This will overwrite ALL roles and DELETE remaining ones if the client is the owner of existing_guild.
This will not work if the client is not the owner of existing_guild.

Arguments:
    bot -- a discord.py client object.
    existing_guild -- the target guild.
    server -- a discord server dict following the server schema
"""


async def write_roles(
    existing_guild: discord.Guild, roles: list, overwrite_prompt=True
):
    """
    Algorithm:
        Let R_s = roles (dict)
        Let R_e = existing_guild.roles (dpy)
        Reverse before applying algorithm because @everyone is the first element in both sequences.

        R_s shall be written to R_e with minimal API requests.

        root is always at the start of both sequences. This does not have to exist in R_e or R_s.
        because the boundaries are not touched in the algorithm (other boundary is @everyone)
        @everyone is always at the end of both sequences.

        An edit (including position shift) is equal to creation with a predefined position, in the sense that it is one API request.

        1. Find longest common subsequence of R_e and R_s
            * Example (rx is a random role):
                R_s: root, Owner, Admin, Mod, Helper, Member, @everyone
                R_e: root, Owner, r1, r2, Mod, Member, Admin, @everyone
                LCS: root, Owner, Mod, Member, @everyone

        2. Iterate through the roles that consecutive elements of the LCS surround in R_e and execute step 3 until finished.
            * Example:
                R_e: root, Owner, r1, r2, Mod, Member, Admin, @everyone
                LCS: root, Owner, Mod, Member, @everyone
                |LCS| - 1 iterations: root -> Owner (encompasses nothing)
                                  Owner -> Mod (encompasses r1, r2)
                                  Mod -> Member (encompasses nothing)
                                  Member -> @everyone (encompasses Admin)

        3. Place/edit/delete roles in between LCS roles (do not touch any role in LCS).
            * Let enc(R_s) and enc(R_e) be the sequence of roles that are encompassed in a given iteration
              for R_s and R_e respectively. Reminder: R_s is immutable, R_e is being changed
            * |LCS| - 1 iterations

            * Cases:
                Encompassing R_s and R_e nil: skip iteration (`continue`)
                Encompassing R_s nil: Deletion only
                Encompassing R_e nil: Creation only
                Encompassing both:
                    if |enc(R_s)| > |enc(R_e)|: Rewrite, then creation
                    elif |enc(R_s)| < |enc(R_e)|: Rewrite, then deletion
                    else (same length): Rewrite only

            * Example:
                R_s: root, Owner, Admin, Mod, Helper, Member, @everyone
                R_e: root, r3, Owner, r1, r2, Mod, Member, Admin, @everyone
                LCS: root, Owner, Mod, Member, @everyone

                |LCS| - 1 = 5 - 1 = 4 iterations

                Iteration 1:
                    Traverse: root -> Owner
                    Encompassing in R_s: nil
                    Encompassing in R_e: r3
                    Create: nil
                    Rewrite: nil
                    Delete: r3 (R_e: Owner, r1, r2 Admin, Mod, Member, Admin)

                Iteration 2:
                    Traverse: Owner -> Mod
                    Encompassing in R_s: Admin
                    Encompassing in R_e: r1, r2
                    Create: nil
                    Rewrite: r1 -> Admin  (R_e: Owner, Admin, r2, Mod, Member, Admin)
                    Delete: r2  (R_e: Owner, Admin, Mod, Member, Admin)

                New R_e: Owner, Admin, Mod, Member, Admin, @everyone
                Iteration 3:
                    Traverse: Mod -> Member
                    Encompassing in R_s: Helper
                    Encompassing in R_e: nil
                    Rewrite: nil
                    Create: Helper (R_e: Owner, Admin, Mod, Helper, Member, Admin)
                    Delete: nil

                New R_e: Owner, Admin, Mod, Helper, Member, Admin, @everyone
                Iteration 4:
                    Traverse: Member -> @everyone
                    Encompassing in R_s: nil
                    Encompassing in R_e: Admin
                    Create: nil
                    Rewrite: nil
                    Delete: Admin (R_e: Owner, Admin, Mod, Helper, Member)

                R_e == R_s. Done.

    """

    logging.info(f"Writing roles for server '{existing_guild.name}'")

    # We need `len(roles)` of free spaces for roles.
    # As discord has a role limit of 250 (including @everyone), `250 -
    # len(existing_guild.roles)`
    # is the amount of free spaces left.  Issue an input() to ask user
    free_spaces_left = 250 - len(existing_guild.roles)
    logging.info(
        f"{free_spaces_left} role spaces available for server '{existing_guild.name}'"
    )

    if overwrite_prompt:
        inp = input(
            f"""
        Continuing to write roles will destroy all roles, and only works if the client is the owner of the server.
        Use `append_roles` to add roles to the end of the heirarchy.
        Y/n : """
        ).lower()

        if inp[0] == "y":
            logging.info(
                f"Overwrite roles under highest role of client for server '{existing_guild.name}'"
            )
        else:
            logging.info(f"Abort write_roles for server '{existing_guild.name}'")
            return None

    # We need to sort the roles so they are in the correct position
    sorted_server_roles = list(
        reversed(sorted(roles, key=lambda role: int(role["position"])))
    )

    # minus 1 because @everyone is included in the list of roles.
    amt_to_write = min(len(existing_guild.roles), len(sorted_server_roles)) - 1
    everyonedict = role_dict_to_dpy(sorted_server_roles[0])
    # del everyonedict['position']
    # Overwrite the @everyone role
    logging.info(f"Overwrite default role for server '{existing_guild.name}'")
    await existing_guild.default_role.edit(
        permissions=everyonedict["permissions"], reason="Automatic role writing"
    )

    roles_top_to_bottom = list(reversed(existing_guild.roles))

    # Overwriting
    for idx in range(amt_to_write):
        role = roles_top_to_bottom[idx]
        replacement_role_dict = sorted_server_roles[idx]

        if check_roles_equal(role, replacement_role_dict):
            logging.info(
                f"Skipping role overwrite of '{replacement_role_dict['name']}' for server '{existing_guild.name}' - role is equal"
            )
            continue

        logging.info(
            f"Writing role '{replacement_role_dict['name']}' in place of role '{role.name}' for server '{existing_guild.name}'"
        )

        dpy_role_dict = role_dict_to_dpy(replacement_role_dict)
        del dpy_role_dict["position"]
        await role.edit(**dpy_role_dict, reason="Automatic role writing")

    # Appending
    if len(sorted_server_roles) > len(existing_guild.roles):
        # amount of roles left (to write)
        amt_roles_left = len(sorted_server_roles) - len(existing_guild.roles)
        for i in range(amt_to_write, amt_to_write + amt_roles_left):
            role = sorted_server_roles[i]
            logging.info(
                f"Appending role '{role['name']}' for server '{existing_guild.name}'"
            )
            dpy_role_dict = role_dict_to_dpy(role)
            del dpy_role_dict["position"]
            await existing_guild.create_role(
                **dpy_role_dict, reason="Automatic role appending"
            )
    # Erasing
    else:
        amt_roles_to_erase = len(existing_guild.roles) - len(sorted_server_roles)
        # last amt_roles_to_erase from list
        # Since @everyone is the 0th role, we offset it by 1 to get actual
        # roles.
        # Reversed so it starts deleting from the last overwritten role
        roles_to_erase = reversed(existing_guild.roles[1 : amt_roles_to_erase + 1])
        for role in roles_to_erase:
            logging.info(
                f"Deleting role '{role.name}' for server '{existing_guild.name}'"
            )
            await role.delete()


"""
Converts a dict conforming to permission_override_schemas.json#/permission_override_list_schema
to a dpy PermissionOverwrite object

Arguments:
    override_dict -- the override dictionary
"""


def override_to_dpy(override_dict: dict):
    # dict comprehension because the structure might change later
    return discord.PermissionOverwrite(**{k: v for (k, v) in override_dict.items()})


"""
Turns role overrides for text, voice and category channels to a dpy compatible PermissionOverwrite dict.
This is async because of fetch_roles() API call. This is needed because the guild object is not guaranteed
to have updated by the time this function is called.

Arguments:
    bot -- a discord.py client object. needed for user overrides
    abcchannel -- either a category, text or voice channel as specified by the schema
    existing_guild -- a guild object with the roles in place
"""


async def get_dpy_overrides(
    bot: discord.Client, existing_guild: discord.Guild, abcchannel: dict
):
    overrides = {}

    # we need an actual api request to make sure the guild is updated
    existing_guild_roles = await existing_guild.fetch_roles()
    # this returns @everyone followed by the role heirarchy, #1 role at idx 1
    existing_guild_roles.append(existing_guild_roles.pop(0))
    existing_guild_roles.reverse()

    for role_override in abcchannel["role_permission_overrides"]:
        role_pos = role_override["position"]
        candidate_role = existing_guild_roles[role_pos]
        if candidate_role.name == role_override["name"]:
            logging.info(
                f"Adding override for role '{role_override['name']}' for abcchannel '{abcchannel['name']}' for server '{existing_guild.name}'"
            )

            overrides[candidate_role] = override_to_dpy(role_override["permissions"])
        else:
            logging.warning(
                f"Skipping role override for abcchannel '{abcchannel['name']}' for server '{existing_guild.name}': candidate role '{candidate_role.name}' at position {role_pos} does not share the same name as override '{role_override['name']}'"
            )

    for user_override in abcchannel["user_permission_overrides"]:
        usr = bot.get_user(int(user_override["id"]))
        if usr:
            logging.info(
                f"Adding override for user '{usr.name}' for abcchannel '{abcchannel['name']}' for server '{existing_guild.name}'"
            )
            overrides[usr] = override_to_dpy(user_override["permissions"])
        else:
            logging.warning(
                f"Skipping user override for abcchannel '{abcchannel['name']}' for server '{existing_guild.name}': candidate user '{candidate_role.name}' does not exist"
            )
    return overrides


"""
Adds a dpy textchannel to a category, None if uncategorized

Arguments:
    bot -- a discord.py client object. needed for user overrides
    channel -- the text channel following the textchannel schema
    category -- the category which to add the channel to

"""


async def append_textchannel(
    bot: discord.Client,
    textchannel: dict,
    category: discord.CategoryChannel,
    add_perms=True,
):
    existing_guild = category.guild
    logging.info(
        f"Append text channel '{textchannel['name']}' for category '{category.name}' for server '{existing_guild.name}'"
    )
    overrides = (
        await get_dpy_overrides(bot, existing_guild, textchannel) if add_perms else {}
    )
    await existing_guild.create_text_channel(
        name=textchannel["name"],
        overwrites=overrides,
        category=category,
        topic=textchannel["topic"],
        slowmode_delay=textchannel["slowmode"],
    )


async def write_textchannel(
    bot: discord.Client,
    textchannel: dict,
    existing_textchannel: discord.TextChannel,
    add_perms=True,
):
    existing_guild = category.guild
    logging.info(
        f"Write text channel '{textchannel['name']}' for category '{category.name}' for server '{existing_guild.name}'"
    )
    overrides = (
        await get_dpy_overrides(bot, existing_guild, textchannel) if add_perms else {}
    )
    await existing_textchannel.edit(
        name=textchannel["name"],
        overwrites=overrides,
        category=category,
        topic=textchannel["topic"],
        slowmode_delay=textchannel["slowmode"],
    )


"""
Adds a dpy voice channel to a category, None if uncategorized

Arguments:
    bot -- a discord.py client object. needed for user overrides
    channel -- the voice channel following the voicechannel schema
    category -- the category which to add the channel to

"""


async def append_voicechannel(
    bot: discord.Client,
    voicechannel: dict,
    category: discord.CategoryChannel,
    add_perms=True,
):
    existing_guild = category.guild
    logging.info(
        f"Append voice channel '{voicechannel['name']}' for category '{category.name}' for server '{existing_guild.name}'"
    )
    overrides = (
        await get_dpy_overrides(bot, existing_guild, voicechannel) if add_perms else {}
    )
    ulimit = voicechannel["user_limit"] if voicechannel["user_limit"] != 0 else None
    bitrate = min(voicechannel["bitrate"], existing_guild.bitrate_limit)
    if voicechannel["bitrate"] > existing_guild.bitrate_limit:
        logging.warning(
            "Bitrate limited to {existing_guild.bitrate_limit}bps from {voicechannel['bitrate']}bps for '{voicechannel['name']}' for server '{existing_guild.name}'"
        )

    await existing_guild.create_voice_channel(
        name=voicechannel["name"],
        overwrites=overrides,
        category=category,
        bitrate=bitrate,
        user_limit=ulimit,
    )


"""
Appends categories conforming to category_schema.json to a guild

Arguments:
    bot -- a discord.py client object. needed for user overrides
    existing_guild -- the target guild
    categories -- a discord category list, each element following the category schema

"""


async def append_categories(
    bot: discord.Client,
    existing_guild: discord.Guild,
    categories: list,
    add_channels=True,
    add_perms=True,
    append_prompt=True,
):
    logging.info(
        f"Appending categories roles for server '{existing_guild.name}' (add_channels={add_channels})"
    )

    for category in categories:
        # Uncategorized channels have an empty category name
        created_category = None

        if category["name"] != "":
            overrides = (
                await get_dpy_overrides(bot, existing_guild, category)
                if add_perms
                else {}
            )

            logging.info(
                f"Creating category '{category['name']}' for server '{existing_guild.name}'"
            )
            created_category = await existing_guild.create_category(
                name=category["name"], overwrites=overrides
            )

        if add_channels:
            for text_channel in category["text_channels"]:
                await append_textchannel(bot, text_channel, created_category)

            for voice_channel in category["voice_channels"]:
                await append_voicechannel(bot, voice_channel, created_category)


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


async def create_server(bot: discord.Client, server: dict, import_folder="", add_emojis=True):
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

    server_icon_bytes = None

    # Download the server icon.  The icon argument for create_guild takes a
    # bytes-like object
    if import_folder and server["id"]:
        logging.info("Trying to find server icon in import folder...")
        candidate_path = f"{import_folder}/icons/{server['id']}"

        if os.path.exists(candidate_path):
            with open(candidate_path, "rb") as f:
                server_icon_bytes = f.read()
    else:
        logging.info("Downloading server icon...")

        try:
            # Server icon cannot be over 10.240MB
            # first element is the icon, second is the extension
            server_icon_bytes = get_icon_under_10mb(server["icon_url"])[0]
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

    # After the server is created, we can add the roles and stuff with other
    # functions
    # which can be used in `overwrite_server`
    # first: roles
    await append_roles(new_guild, server["roles"])

    # second: categories, for synced perms
    # this adds channels with their perm overrides.
    await append_categories(bot, new_guild, server["categories"])

    # third: emojis
    if add_emojis:
        await append_emojis(new_guild, server["emojis"], import_folder)
    """
    await asyncio.gather(
        append_roles(bot, new_guild, server['roles']),
        append_emojis(bot, new_guild, server['emojis']),
    )
    """
    # return the server
    return new_guild

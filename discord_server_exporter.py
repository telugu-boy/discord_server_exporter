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

import os
import discord
import time
from urllib.request import Request, urlopen
import threading
import json

from ds_common_funcs import req_hdr, get_icon_under_10mb

"""
Maps a role to a dictionary that conforms to the role schema.

Arguments:
    role -- a discord.py role object
"""


def conv_role_obj(role: discord.Role, export_perms=True) -> dict:
    logging.info(f"Dumping role '{role.name}' for server '{role.guild.name}'")
    res = {}
    res["name"] = role.name
    # this is the colour integer
    # a value of 0 means transparent
    res["color"] = role.color.value
    res["mentionable"] = role.mentionable
    res["position"] = role.position
    res["id"] = str(role.id)
    res["hoist"] = role.hoist
    # this is the permission integer
    if export_perms:
        logging.info(
            f"Dumping role permissions for role '{role.name}' for server '{role.guild.name}'"
        )
        res["permission_value"] = str(role.permissions.value)
    return res


"""
Return a list of roles in the guild.
The schema for role is in the schemas folder, as with all other relevant structures

Arguments:
    guild -- a discord.py guild object
"""


def dump_roles(guild: discord.Guild, export_perms=True) -> list:
    logging.info(f"Dumping roles for server '{guild.name}'")
    res = []
    # this returns all roles in order not including @everyone.
    for role in guild.roles:
        # converts the role object into the role schema
        res.append(conv_role_obj(role, export_perms))
    return res


"""
Maps a role to a dictionary that conforms to the role schema.

Arguments:
    role -- a discord.py role object
"""


def conv_emoji_obj(emoji: discord.Emoji) -> dict:
    logging.info(f"Dumping emoji '{emoji.name}' for server '{emoji.guild.name}'")
    res = {}
    res["name"] = emoji.name
    res["url"] = str(emoji.url)
    return res

"""
Return a list of the emojis in a guild as a bytes-like object

Arguments:
    guild -- a discord.py guild object
"""

def get_emoji_bytes(guild: discord.Guild) -> list:
  res_emojis = []
  for emoji in guild.emojis:
    logging.info(f"Downloading emoji '{emoji.name}' from server '{guild.name}'")
    req = Request(str(emoji.url), None, req_hdr)
    server_icon_req = urlopen(req)

    # gets extension of the icon from the url
    icon_ext = str(emoji.url).split(".")[-1].split("?")[0]

    res_emojis.append(server_icon_req.read())
  return res_emojis

"""
Write a list of emojis from a guild to a directory

Arguments:
    guild -- a discord.py guild object
"""
def write_emojis_to_dir(guild: discord.Guild, dir_prefix="exported"):
    guild_emoji_folder_path = f"{dir_prefix}/emojis/{guild.id}"
    os.makedirs(guild_emoji_folder_path)
    emojis_bytes = get_emoji_bytes(guild)
    for idx, emoji in enumerate(guild.emojis):
        emoji_bytes = emojis_bytes[idx]
        icon_ext = str(emoji.url).split(".")[-1].split("?")[0]
        with open(f"{guild_emoji_folder_path}/{emoji.name}.{icon_ext}", "wb") as f:
            f.write(emoji_bytes)
            
    logging.info(f"Finished writing emojis from server '{guild.name}'")

"""
Return a list of roles of emojis in the guild.
The schema for emoji is in the schemas folder, as with all other relevant structures

Arguments:
    guild -- a discord.py guild object
"""


def dump_emojis(guild: discord.Guild, export_emojis=False, dir_prefix="exported") -> list:
    logging.info(f"Dumping emojis for server '{guild.name}'")
    res = []
    if export_emojis:
        thread = threading.Thread(target=write_emojis_to_dir, args=(guild, dir_prefix))
        thread.daemon = True
        thread.start()
    for emoji in guild.emojis:
        res.append(conv_emoji_obj(emoji))
    return res


"""
Return the permission overrides for a text or voice channel.
Structure:
    Dict:
        "roles": [ dict of role id, permission override list ]
        "users": [ dict of user id, permission override list ]
The schema for permission override list is in the schemas folder, as with all other relevant structures

Arguments:
    guild -- a discord.py guild object
"""


def get_permission_overrides(channel: discord.abc.ChannelType) -> dict:
    # roles: list of tuples (role position, permission override list)
    # users: list of tuples (user ID, permission override list)
    res = {"roles": [], "users": []}
    for entity, overwrite in channel.overwrites.items():
        # This can also be found in permission_override_schemas.json
        valid_perm_set = overwrite.VALID_NAMES
        permission_override_list = {}
        # False is explicitly disabled
        # True is explicitly enabled
        # if a permission does NOT have an override, it is omitted from the
        # dump
        # Look at permission_setting_schemas.json for the schema itself.
        for perm_name in valid_perm_set:
            # If it doesn't exist, we don't want to add it as well
            perm_status = getattr(overwrite, perm_name, None)
            if perm_status is not None:
                permission_override_list[perm_name] = perm_status

        if isinstance(entity, discord.Role):
            res["roles"].append(
                {
                    "id": str(entity.id),
                    "name": entity.name,
                    "position": entity.position,
                    "permissions": permission_override_list,
                }
            )
        elif isinstance(entity, discord.User):
            res["users"].append(
                {"id": str(entity.id), "permissions": permission_override_list}
            )

    return res


"""
Maps a text channel to a dictionary that conforms to the text channel schema.

Arguments:
    channel -- a discord.py textchannel object
"""


def conv_text_channel_obj(
    channel: discord.TextChannel, export_role_overrides=True, export_user_overrides=True
):
    logging.info(f"Dumping text channel '{channel.name}' in '{channel.guild.name}'")
    res = {}
    res["name"] = channel.name
    res["slowmode"] = channel.slowmode_delay
    res["nsfw"] = channel.is_nsfw()
    res["topic"] = channel.topic
    res["id"] = str(channel.id)

    perms = get_permission_overrides(channel)
    if export_role_overrides:
        logging.info(
            f"Dumping role permission overrides for text channel '{channel.name}' in '{channel.guild.name}'"
        )
        res["role_permission_overrides"] = perms["roles"]
    if export_user_overrides:
        logging.info(
            f"Dumping user permission overrides for text channel '{channel.name}' in '{channel.guild.name}'"
        )
        res["user_permission_overrides"] = perms["users"]

    return res


"""
Return a list of text channels in the guild.
The schema for channel is in the schemas folder, as with all other relevant structures

Arguments:
    guild -- a discord.py guild object
"""


def dump_text_channels(
    guild: discord.Guild, export_role_overrides=True, export_user_overrides=True
) -> list:
    logging.info(f"Dumping text channels for server '{guild.name}'")
    res = []
    for channel in guild.text_channels:
        res.append(
            conv_text_channel_obj(channel, export_role_overrides, export_user_overrides)
        )
    return res


"""
Maps a voice channel to a dictionary that conforms to the text channel schema.

Arguments:
    channel -- a discord.py voicechannel object
"""


def conv_voice_channel_obj(
    channel: discord.VoiceChannel,
    export_role_overrides=True,
    export_user_overrides=True,
):
    logging.info(f"Dumping voice channel '{channel.name}' in '{channel.guild.name}'")
    res = {}
    res["name"] = channel.name
    res["bitrate"] = channel.bitrate
    res["user_limit"] = channel.user_limit
    res["id"] = str(channel.id)

    perms = get_permission_overrides(channel)
    if export_role_overrides:
        logging.info(
            f"Dumping role permission overrides for voice channel '{channel.name}' in '{channel.guild.name}'"
        )
        res["role_permission_overrides"] = perms["roles"]
    if export_user_overrides:
        logging.info(
            f"Dumping user permission overrides for voice channel '{channel.name}' in '{channel.guild.name}'"
        )
        res["user_permission_overrides"] = perms["users"]

    return res


"""
Return a list of voice channels in the guild.
The schema for channel is in the schemas folder, as with all other relevant structures

Arguments:
    guild -- a discord.py guild object
"""


def dump_voice_channels(
    guild: discord.Guild, export_role_overrides=True, export_user_overrides=True
) -> list:
    logging.info(f"Dumping voice channels for server '{guild.name}'")
    res = []
    for channel in guild.voice_channels:
        res.append(
            conv_voice_channel_obj(
                channel, export_role_overrides, export_user_overrides
            )
        )
    return res


"""
Maps a category to a dictionary that conforms to the category schema.

Arguments:
    channel -- a discord.py voicechannel object
"""


def conv_category_obj(
    category: discord.CategoryChannel,
    export_text_channels=True,
    export_voice_channels=True,
    export_role_overrides=True,
    export_user_overrides=True,
):
    guild = category.guild
    logging.info(f"Dumping category '{category.name}' for server '{guild.name}'")
    res = {}
    res["name"] = category.name

    if export_text_channels:
        logging.info(
            f"Dumping text channels for category '{category.name}' in '{category.guild.name}'"
        )
        res["text_channels"] = []
        for channel in category.text_channels:
            res["text_channels"].append(
                conv_text_channel_obj(
                    channel, export_role_overrides, export_user_overrides
                )
            )

    if export_voice_channels:
        logging.info(
            f"Dumping voice channels for category '{category.name}' in '{category.guild.name}'"
        )
        res["voice_channels"] = []
        for channel in category.voice_channels:
            res["voice_channels"].append(
                conv_voice_channel_obj(
                    channel, export_role_overrides, export_user_overrides
                )
            )

    perms = get_permission_overrides(category)
    if export_role_overrides:
        logging.info(
            f"Dumping role overrides for category '{category.name}' in '{guild.name}'"
        )
        res["role_permission_overrides"] = perms["roles"]
    if export_user_overrides:
        logging.info(
            f"Dumping user overrides for category '{category.name}' in '{guild.name}'"
        )
        res["user_permission_overrides"] = perms["users"]

    return res


"""
Return a list of categories in the guild.
The schema for category is in the schemas folder, as with all other relevant structures

Arguments:
    guild -- a discord.py guild object
"""


def dump_categories(
    guild: discord.Guild,
    uncategorized=True,
    export_text_channels=True,
    export_voice_channels=True,
    export_role_overrides=True,
    export_user_overrides=True,
) -> list:

    res = []

    if len(guild.by_category()) <= 0:
        return res

    if uncategorized:
        logging.info(f"Dumping uncategorized channels for server '{guild.name}'")
        dummy_cat = {}
        dummy_cat["name"] = ""
        dummy_cat["text_channels"] = []
        dummy_cat["voice_channels"] = []
        for channel in guild.by_category()[0]:
            if isinstance(channel, discord.TextChannel):
                dummy_cat["text_channels"].append(
                    conv_text_channel_obj(
                        channel, export_role_overrides, export_user_overrides
                    )
                )
            elif isinstance(channel, discord.VoiceChannel):
                dummy_cat["voice_channels"].append(
                    conv_voice_channel_obj(
                        channel, export_role_overrides, export_user_overrides
                    )
                )
        res.append(dummy_cat)

    logging.info(f"Dumping categories for server '{guild.name}'")
    for category in guild.categories:
        res.append(
            conv_category_obj(
                category,
                export_text_channels,
                export_voice_channels,
                export_role_overrides,
                export_user_overrides,
            )
        )
    return res


"""
Maps a member to a dictionary that conforms to the member schema.

Arguments:
    guild -- a discord.py member object
"""


def conv_member_obj(
    member: discord.Member, export_nickname=True, export_roles=True
) -> dict:
    logging.info(
        f"Dumping member '{member.name}#{member.discriminator}' ({member.id}) in server '{member.guild.name}'"
    )
    res = {}

    res["name"] = member.name
    res["discrim"] = member.discriminator
    res["id"] = str(member.id)

    if export_nickname and member.nick is not None:
        res["nickname"] = member.nick
    if export_roles:
        res["roles"] = [str(role.id) for role in member.roles]

    return res


"""
Return a list of members in the guild.
The schema for member is in the schemas folder, as with all other relevant structures

Arguments:
    guild -- a discord.py member object
"""


def dump_members(guild: discord.Guild, export_nickname=True, export_roles=True) -> list:
    logging.info(f"Dumping members for server '{guild.name}'")
    res = []
    for member in guild.members:
        res.append(conv_member_obj(member, export_nickname, export_roles))
    return res

"""

"""
def dump_server_icon(guild: discord.Guild, dir_prefix="exported"):
    logging.info(f"Downloading server icon for server '{guild.name}'")
    iconurl = str(guild.icon_url)

    if not iconurl:
        return
        
    icon = get_icon_under_10mb(iconurl)
    with open(f"{dir_prefix}/icons/{guild.id}.{icon[1]}", "wb") as f:
        f.write(icon[0])


"""
Return a dict object representing a single server.
The schema for server is in the schemas folder, as with all other relevant structures

WARNING: Exporting members may increase the size of the resulting dictionary considerably.

Arguments:
    guild -- a discord.py guild object
"""


def dump_server(guild: discord.Guild, export_emojis=True, export_server_icon=True, export_schemas=True, export_files_dir="exported", export_members=False) -> dict:
    logging.info(f"Dumping server '{guild.name}'")
    res = {}

    res["name"] = guild.name
    res["id"] = str(guild.id)
    res["icon_url"] = str(guild.icon_url)
    res["voice_region"] = guild.region.value

    if guild.afk_channel:
        res["inactive_channel"] = str(guild.afk_channel.id)
        res["inactive_timeout"] = guild.afk_timeout
    else:
        logging.info(f"No AFK channel present in '{guild.name}'; omitting")

    if guild.system_channel:
        res["system_message_channel"] = str(guild.system_channel.id)
    else:
        logging.info(f"No system channel present in '{guild.name}'; omitting")

    res["join_broadcast"] = guild.system_channel_flags.join_notifications
    res["boost_broadcast"] = guild.system_channel_flags.premium_subscriptions
    res["default_notifications"] = bool(guild.default_notifications.value)
    res["verification_level"] = guild.verification_level.value
    res["content_filter"] = guild.explicit_content_filter.value
    res["emojis"] = dump_emojis(guild, export_emojis, export_files_dir)
    res["roles"] = dump_roles(guild)
    res["categories"] = dump_categories(guild)

    if export_members:
        res["members"] = dump_members(guild)

    if export_server_icon:
        os.makedirs(f"{export_files_dir}/icons", exist_ok=True)
        dump_server_icon(guild, export_files_dir)

    if export_schemas:
        os.makedirs(f"{export_files_dir}/schemas", exist_ok=True)
        with open(f"{export_files_dir}/schemas/{guild.id}.json", "w") as f:
            json.dump(res, f)

    return res

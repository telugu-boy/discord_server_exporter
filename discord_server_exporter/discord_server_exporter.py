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

import discord
import json

"""
Maps a role to a dictionary that conforms to the role schema.

Arguments:
    role -- a discord.py role object
"""
def conv_role_obj(role: discord.Role, export_perms=True) -> dict:
    res = {}
    res['name'] = role.name
    # this is the colour integer
    res['color'] = role.color.value
    res['mentionable'] = role.mentionable
    res['position'] = role.position
    # this is the permission integer
    if export_perms:
        res['permission_value'] = role.permissions.value
    return res

"""
Return a list of roles in the guild.
The schema for role is in the schemas folder, as with all other relevant structures

Arguments:
    guild -- a discord.py guild object
"""
def dump_roles(guild: discord.Guild, export_perms=True) -> list:
    res = []
    # this returns all roles in order not including @everyone.
    for role in guild.roles[1:]:
        # converts the role object into the role schema
        res.append(conv_role_obj(role, export_perms))
    return res

"""
Maps a role to a dictionary that conforms to the role schema.

Arguments:
    role -- a discord.py role object
"""
def conv_emoji_obj(emoji: discord.Emoji) -> dict:
    res = {}
    res['name'] = emoji.name
    res['url'] = str(emoji.url)
    return res

"""
Return a list of roles of emojis in the guild.
The schema for emoji is in the schemas folder, as with all other relevant structures

Arguments:
    guild -- a discord.py guild object
"""
def dump_emojis(guild: discord.Guild) -> list:
    res = []
    for emoji in guild.emojis:
        res.append(conv_emoji_obj(emoji))
    return res

"""
Return the permission overrides for a text or voice channel.
Structure:
    Dict:
        "roles": [ dict of role position, permission override list ]
        "users": [ dict of user id, permission override list ]
The schema for permission override list is in the schemas folder, as with all other relevant structures

Arguments:
    guild -- a discord.py guild object
"""
def get_permission_overrides(channel: discord.abc.ChannelType) -> dict:
    # roles: list of tuples (role position, permission override list)
    # users: list of tuples (user ID, permission override list)
    res = {
        "roles": [],
        "users": []
        }
    for entity, overwrite in channel.overwrites.items():
        # This can also be found in permission_override_schemas.json
        valid_perm_set = overwrite.VALID_NAMES
        permission_override_list = {}
        # False is explicitly disabled
        # True is explicitly enabled
        # if a permission does NOT have an override, it is omitted from the dump
        # Look at permission_setting_schemas.json for the schema itself.
        for perm_name in valid_perm_set:
            # If it doesn't exist, we don't want to add it as well
            perm_status = getattr(overwrite, perm_name, None)
            if perm_status is not None:
                permission_override_list[perm_name] = perm_status

        if type(entity) == discord.Role:
            res['roles'].append( {"role_position": entity.position, "permissions": permission_override_list} )
        elif type(entity) == discord.User:
            res['users'].append( {"user_id": entity.id, "permissions": permission_override_list} )

    return res


"""
Maps a text channel to a dictionary that conforms to the text channel schema.

Arguments:
    channel -- a discord.py textchannel object
"""
def conv_text_channel_obj(channel: discord.TextChannel,
                          export_role_overrides=True,
                          export_user_overrides=True):
    res = {}
    res['name'] = channel.name
    res['slowmode'] = channel.slowmode_delay

    perms = get_permission_overrides(channel)
    if export_role_overrides:
        res['role_permission_overrides'] = perms['roles']
    if export_user_overrides:
        res['user_permission_overrides'] = perms['users']

    return res

"""
Return a list of roles of channels in the guild.
The schema for channel is in the schemas folder, as with all other relevant structures

Arguments:
    guild -- a discord.py guild object
"""
def dump_text_channels(guild: discord.Guild,
                  export_role_overrides=True,
                  export_user_overrides=True) -> list:
    res = []
    for channel in guild.text_channels:
        res.append(conv_text_channel_obj(channel,
                                    export_role_overrides,
                                    export_user_overrides))
    return res

"""
Return a dict object representing a single server.
The schema for server is in the schemas folder, as with all other relevant structures

Arguments:
    guild -- a discord.py guild object
"""
async def dump_server(guild: discord.Guild) -> dict:
    pass

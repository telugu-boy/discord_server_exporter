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
    # a value of 0 means transparent
    res['color'] = role.color.value
    res['mentionable'] = role.mentionable
    res['position'] = role.position
    res['id'] = str(role.id)
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
        "roles": [ dict of role id, permission override list ]
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
        # if a permission does NOT have an override, it is omitted from the
        # dump
        # Look at permission_setting_schemas.json for the schema itself.
        for perm_name in valid_perm_set:
            # If it doesn't exist, we don't want to add it as well
            perm_status = getattr(overwrite, perm_name, None)
            if perm_status is not None:
                permission_override_list[perm_name] = perm_status

        if type(entity) == discord.Role:
            res['roles'].append({"role_id": entity.id, "permissions": permission_override_list})
        elif type(entity) == discord.User:
            res['users'].append({"user_id": entity.id, "permissions": permission_override_list})

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
    res['nsfw'] = channel.is_nsfw()
    res['news'] = channel.is_news()
    res['id'] = str(channel.id)

    perms = get_permission_overrides(channel)
    if export_role_overrides:
        res['role_permission_overrides'] = perms['roles']
    if export_user_overrides:
        res['user_permission_overrides'] = perms['users']

    return res

"""
Return a list of text channels in the guild.
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
Maps a voice channel to a dictionary that conforms to the text channel schema.

Arguments:
    channel -- a discord.py voicechannel object
"""
def conv_voice_channel_obj(channel: discord.VoiceChannel,
                          export_role_overrides=True,
                          export_user_overrides=True):
    res = {}
    res['name'] = channel.name
    res['bitrate'] = channel.bitrate
    res['user_limit'] = channel.user_limit
    res['id'] = str(channel.id)

    perms = get_permission_overrides(channel)
    if export_role_overrides:
        res['role_permission_overrides'] = perms['roles']
    if export_user_overrides:
        res['user_permission_overrides'] = perms['users']

    return res

"""
Return a list of voice channels in the guild.
The schema for channel is in the schemas folder, as with all other relevant structures

Arguments:
    guild -- a discord.py guild object
"""
def dump_voice_channels(guild: discord.Guild,
                  export_role_overrides=True,
                  export_user_overrides=True) -> list:
    res = []
    for channel in guild.voice_channels:
        res.append(conv_voice_channel_obj(channel,
                                    export_role_overrides,
                                    export_user_overrides))
    return res

"""
Maps a category to a dictionary that conforms to the category schema.

Arguments:
    channel -- a discord.py voicechannel object
"""
def conv_category_obj(category: discord.CategoryChannel,
                      export_text_channels=True,
                  export_voice_channels=True,
                          export_role_overrides=True,
                          export_user_overrides=True):
    res = {}
    res['name'] = category.name
    
    if export_text_channels:
        res['text_channels'] = []
        for channel in category.text_channels:
            res['text_channels'].append(conv_text_channel_obj(channel,
                                    export_role_overrides,
                                    export_user_overrides))

    if export_voice_channels:
        res['voice_channels'] = []
        for channel in category.voice_channels:
            res['voice_channels'].append(conv_voice_channel_obj(channel,
                                    export_role_overrides,
                                    export_user_overrides))

    perms = get_permission_overrides(category)
    if export_role_overrides:
        res['role_permission_overrides'] = perms['roles']
    if export_user_overrides:
        res['user_permission_overrides'] = perms['users']

    return res

"""
Return a list of categories in the guild.
The schema for category is in the schemas folder, as with all other relevant structures

Arguments:
    guild -- a discord.py guild object
"""
def dump_categories(guild: discord.Guild,
                    uncategorized=True,
                  export_text_channels=True,
                  export_voice_channels=True,
                  export_role_overrides=True,
                  export_user_overrides=True) -> list:
    res = []

    if len(guild.by_category()) <= 0:
        return res

    if uncategorized:
        dummy_cat = {}
        dummy_cat['name'] = ""
        dummy_cat['text_channels'] = []
        dummy_cat['voice_channels'] = []
        for channel in guild.by_category()[0]:
            if type(channel) == discord.TextChannel:
                dummy_cat.append(conv_text_channel_obj(channel, export_role_overrides, export_user_overrides))
            elif type(channel) == discord.VoiceChannel:
                dummy_cat.append(conv_voice_channel_obj(channel, export_role_overrides, export_user_overrides))
        res.append(dummy_cat)

    for category in guild.categories:
        res.append(conv_category_obj(category, export_text_channels, export_voice_channels, export_role_overrides, export_user_overrides))
    return res

"""
Return a dict object representing a single server.
The schema for server is in the schemas folder, as with all other relevant structures

Arguments:
    guild -- a discord.py guild object
"""
def dump_server(guild: discord.Guild) -> dict:
    res = {}

    res['name'] = guild.name
    res['icon_url'] = str(guild.icon_url)
    res['voice_region'] = guild.region.value
    if guild.afk_channel:
        res['inactive_channel'] = str(guild.afk_channel.id)
        res['inactive_timeout'] = guild.afk_timeout
    res['system_message_channel'] = str(guild.system_channel.id)
    res['join_broadcast'] = guild.system_channel_flags.join_notifications
    res['boost_broadcast'] = guild.system_channel_flags.premium_subscriptions
    res['default_notifications'] = bool(guild.default_notifications.value)
    res['verification_level'] = guild.verification_level.value
    res['content_filter'] = guild.explicit_content_filter.value
    res['emojis'] = dump_emojis(guild)
    res['roles'] = dump_roles(guild)
    res['categories'] = dump_categories(guild)

    return res

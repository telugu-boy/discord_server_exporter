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
Return a list of roles in the guild.
The schema for role is in the schemas folder, as with all other relevant structures

Arguments:
    guild -- a discord.py guild object
"""
def conv_role_obj(role: discord.Role) -> dict:
    res = {}
    res['name'] = role.name
    # this is the colour integer
    res['color'] = role.color.value
    res['mentionable'] = role.mentionable
    res['position'] = role.position
    # this is the permission integer
    res['permission_value'] = role.permissions.value
    return res


async def dump_roles(guild: discord.Guild) -> list:
    res = []
    roles = await guild.fetch_roles()
    # this returns all roles in order not including @everyone.
    for role in roles[1:]:
        # converts the role object into the role schema
        res.append(conv_role_obj(role))
    return res


"""
Return a dict object representing a single server.
The schema for server is in the schemas folder, as with all other relevant structures

Arguments:
    guild -- a discord.py guild object
"""
async def dump_server(guild: discord.Guild) -> dict:
    pass

'''
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
'''

import jsonschema

role_schema = {
    "title": "Discord role",
    "description": "Represents a single role on Discord",
    "type": "object",
    "properties": {
        "name": {
            "description": "The name of the role",
            "type": "string"
        },
        "color": {
            "description": "The colour of the role, represented as a 24 bit int",
            "type": "integer",
            "minimum": 0, # will be zero for transparent
            "exclusiveMaximum": 2**24
        },
        "mentionable": {
            "description": "Whether or not the role is mentionable",
            "type": "boolean"
        },
        "position": {
            "description": "The position of the role in the heirarchy",
            "type": "integer",
            "minimum": 1, # position 0 is taken by the @everyone role.
            "exclusiveMaximum": 250 # 250 is the maximum amount of roles
        },
        "permissions_value": {
            "description": "The 53-bit integer that represents the permissions for this role",
            "type": "integer",
            "minimum": 0,
            "exclusiveMaximum": 2**53 # 53 bit integer minus 1 is exclusive
        }
    },
    "required": ["name", "color", "mentionable", "position"]
}

perm_settings_schema = {
    "title": "Discord permission settings",
    "description": "Represents permission settings for a channel or category",
    "type": "object"
}

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This code is part of the TrinityX software suite
# Copyright (C) 2023  ClusterVision Solutions b.v.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>

import requests
from config import settings, get_token

class LunaRequestHandler():
    endpoints = {
        'users': {
            'list': f'{settings.api.protocol}://{settings.api.endpoint}/config/osuser',
            'get': f'{settings.api.protocol}://{settings.api.endpoint}/config/osuser/{{name}}',
            'update': f'{settings.api.protocol}://{settings.api.endpoint}/config/osuser/{{name}}',
            'delete': f'{settings.api.protocol}://{settings.api.endpoint}/config/osuser/{{name}}/_delete'
        },
        'groups': {
            'list': f'{settings.api.protocol}://{settings.api.endpoint}/config/osgroup',
            'get': f'{settings.api.protocol}://{settings.api.endpoint}/config/osgroup/{{name}}',
            'update': f'{settings.api.protocol}://{settings.api.endpoint}/config/osgroup/{{name}}',
            'delete': f'{settings.api.protocol}://{settings.api.endpoint}/config/osgroup/{{name}}/_delete'
        }
    }
    def __init__(self):
        self.session = requests.Session()

    @classmethod
    def get_token(cls):
        return get_token()

    @classmethod
    def get_auth_header(cls):
        """
        This method will get the authentication header.
        """
        return {'x-access-tokens': cls.get_token()}

    def list(self, target):
        """
        This method will get all the groups/users from the database.
        """
        resp = self.session.get(self.endpoints[target]['list'], headers=self.get_auth_header(), verify=(settings.api.verify_certificate.lower() == 'true'))
        print(resp.text)
        if resp.status_code not in [200, 201, 204]:
            raise Exception(f"Error {resp.text} while listing {target}, received status code {resp.status_code}")
        return  resp.json()['config'][f"os{target[:-1]}"]

    def get(self, target, name):
        """
        This method will get the group/user from the database.
        """
        resp = self.session.get(self.endpoints[target]['get'].format(name=name), headers=self.get_auth_header(), verify=(settings.api.verify_certificate.lower() == 'true'))
        if resp.status_code not in [200, 201, 204]:
            raise Exception(f"Error {resp.text} while getting {target}, received status code {resp.status_code}")
        return  resp.json()['config'][f"os{target[:-1]}"][name]

    def delete(self, target, name):
        """
        This method will delete the group/user from the database.
        """
        resp = self.session.get(self.endpoints[target]['delete'].format(name=name), headers=self.get_auth_header(), verify=(settings.api.verify_certificate.lower() == 'true'))
        if resp.status_code not in [200, 201, 204]:
            raise Exception(f"Error {resp.text} while deleting {target}, received status code {resp.status_code}")
        return  {"message", 'User Updated successfully'}
    
    def update(self, target, name, data):
        """
        This method will update the group/user from the database.
        """
        payload = {
            "config" : {
                f"os{target[:-1]}":{
                    name:data
                }
            }
        }
        resp = self.session.post(self.endpoints[target]['update'].format(name=name), headers=self.get_auth_header(), json=payload, verify=(settings.api.verify_certificate.lower() == 'true'))
        if resp.status_code not in [200, 201, 204]:
            raise Exception(f"Error {resp.text} while updating {target}, received status code {resp.status_code}")
        return  {"message", 'User Updated successfully'}

if __name__ == "__main__":
    handler = LunaRequestHandler()

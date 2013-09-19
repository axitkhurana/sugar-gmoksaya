# Copyright (c) 2013 Akshit Khurana - axitkhurana@gmail.com
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA.

import settings
from urlparse import urlparse

from helpers import url_for, url_for_media

from grestful.object import Object
from grestful.helpers import param_upload
from grestful.decorators import asynchronous


class Project(Object):
    def __init__(self):
        Object.__init__(self)
        settings.paths['project'] = 'projects/'
        settings.paths['profile'] = 'profile/'

    @asynchronous
    def create(self, profile_id, title, description, project_file, screenshot):
        profile_url = url_for('profile', profile_id, False)
        user = urlparse(profile_url).path
        params = [
            ('user', user),
            ('title', title),
            ('desc', description),
        ]

        project_url = url_for('project')
        files = [param_upload('src', project_file),
                 param_upload('screenshot', screenshot)]

        self._post(project_url, params, files)

    def list(self, profile_id):
        profile_url = url_for('profile', profile_id)
        # extract projects from profile dict
        self._get(profile_url)

    @asynchronous
    def get(self, project_id):
        project_url = url_for('project', project_id)
        self._get(project_url)

    @asynchronous
    def download_file(self, file_path):
        file_url = url_for_media(file_path)
        self._get(file_url)


class User(Object):
    def __init__(self):
        Object.__init__(self)
        settings.paths['user'] = 'user/'

    @asynchronous
    def info(self, username):
        user_url = url_for('user', username)
        self._get(user_url)

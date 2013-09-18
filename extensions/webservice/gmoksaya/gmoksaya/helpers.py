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

from urllib import urlencode
from urlparse import urljoin

from settings import credentials, paths, BASE_URL


def url_for(resource, resource_id='', add_credentials=True):
    params = _authentication_params(add_credentials)
    if resource_id:
        resource_id = '{}/'.format(resource_id)

    path = '{0}{1}{2}'.format(paths[resource], resource_id, params)
    return urljoin(BASE_URL, path)


def url_for_media(media_path, add_credentials=True):
    params = _authentication_params(add_credentials)
    path = '{0}{1}'.format(media_path, params)
    return urljoin(BASE_URL, path)


def _authentication_params(add_credentials):
    if add_credentials:
        return '?{}'.format(urlencode(credentials))
    else:
        return ''

# Copyright (c) 2013 Akshit Khurana <axitkhurana@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

import logging
import urllib2
import json
import base64
from gettext import gettext as _

from gi.repository import GConf, Gtk, Gdk

from jarabe.webservice import accountsmanager
from cpsection.webaccount.web_service import WebService
from sugar3.graphics import style

class WebService(WebService):
    def __init__(self):
        self._account = accountsmanager.get_account('gmoksaya')
        logging.error(self._account)

    def get_icon_name(self):
        return 'network-mesh'


    def _get_key(self, username, password):
        # FIXME make this asynchronous
        url = 'http://127.0.0.1:8000/api/v1/token/auth/?format=json'
        request = urllib2.Request(url)
        base64string = base64.encodestring('%s:%s' % (username,
                                           password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        result = urllib2.urlopen(request)
        response = json.loads(result.read())
        return response.get('key', None)

    def _get_public_id_cb(self, user, info):
        client = GConf.Client.get_default()
        client.set_string(self._account.PUBLIC_ID, info['id'])

    def _save_credentials(self, username, password):
        logging.error('SAVE CREDENTIALS')
        client = GConf.Client.get_default()
        client.set_string(self._account.USERNAME, username)

        api_key = self._get_key(username, password)
        client.set_string(self._account.API_KEY, api_key)

        user = self._account.users.User()
        user.connect('completed', self._get_public_id_cb)
        user.info(username)

    def config_service_cb(self, widget, event, container):
        separator = Gtk.HSeparator()

        title = Gtk.Label(label=_('Moksaya: Project Sharing Website'))
        title.set_alignment(0, 0)

        info = Gtk.Label(_("Your password is not saved, it is used to "
                           "fetch an API key"))
        info.set_alignment(0, 0)
        info.set_line_wrap(True)

        ulabel = Gtk.Label(_('Username'))
        ulabel.set_alignment(1, 0.5)
        ulabel.modify_fg(Gtk.StateType.NORMAL,
                         style.COLOR_SELECTION_GREY.get_gdk_color())

        self._uentry = Gtk.Entry()
        self._uentry.set_alignment(0)
        self._uentry.set_size_request(int(Gdk.Screen.width() / 3), -1)

        plabel = Gtk.Label(_('Password'))
        plabel.set_alignment(1, 0.5)
        plabel.modify_fg(Gtk.StateType.NORMAL,
                         style.COLOR_SELECTION_GREY.get_gdk_color())

        self._pentry = Gtk.Entry()
        self._pentry.set_alignment(0)
        self._pentry.set_size_request(int(Gdk.Screen.width() / 3), -1)

        form = Gtk.HBox(spacing=style.DEFAULT_SPACING)
        form.pack_start(ulabel, False, True, 0)
        form.pack_start(self._uentry, False, True, 0)
        form.pack_start(plabel, False, True, 0)
        form.pack_start(self._pentry, False, True, 0)

        vbox = Gtk.VBox()
        vbox.set_border_width(style.DEFAULT_SPACING * 2)
        vbox.set_spacing(style.DEFAULT_SPACING)
        vbox.pack_start(info, False, True, 0)
        vbox.pack_start(form, False, True, 0)

        for c in container.get_children():
            container.remove(c)

        container.pack_start(separator, False, False, 0)
        container.pack_start(title, False, True, 0)
        container.pack_start(vbox, False, True, 0)
        container.show_all()

        self._restore_project_name()


def get_service():
    logging.error('GET FB SERVICE')
    return WebService()

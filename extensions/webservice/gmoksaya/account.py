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

from gettext import gettext as _
import logging
import tempfile

from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import GConf
from gi.repository import GObject

from sugar3.datastore import datastore
from sugar3.graphics.alert import NotifyAlert
from sugar3.graphics.icon import Icon
from sugar3.graphics.menuitem import MenuItem

from jarabe.journal import journalwindow
from jarabe.webservice import account, accountsmanager

ACCOUNT_NAME = _('Moksaya')
ACCOUNT_ICON = 'network-mesh'


class Account(account.Account):

    API_KEY = "/desktop/sugar/collaboration/gmoksaya_access_token"
    USERNAME = "/desktop/sugar/collaboration/gmoksaya_username"
    PUBLIC_ID = "/desktop/sugar/collaboration/gmoksaya_public_id"

    def __init__(self):
        self.gmoksaya = accountsmanager.get_service('gmoksaya')
        self._client = GConf.Client.get_default()
        self._shared_journal_entry = None

        self.gmoksaya.settings.credentials['username'] = \
            self._client.get_string(self.USERNAME)
        self.gmoksaya.settings.credentials['api_key'] = \
            self._client.get_string(self.API_KEY)

    def get_description(self):
        return 'gmoksaya'

    def get_token_state(self):
        return self.STATE_VALID

    def get_shared_journal_entry(self):
        if self._shared_journal_entry is None:
            self._shared_journal_entry = _SharedJournalEntry(self)
        return self._shared_journal_entry

    def get_public_id(self):
        client = GConf.Client.get_default()
        return client.get_string(self.PUBLIC_ID)

    def get_latest_post(self, public_id):
        return get_post(public_id)


class _SharedJournalEntry(account.SharedJournalEntry):
    __gsignals__ = {
        'transfer-state-changed': (GObject.SignalFlags.RUN_FIRST, None,
                                   ([str])),
    }

    def __init__(self, account):
        self._account = account
        self._alert = None

    def get_share_menu(self, metadata):
        menu = _ShareMenu(self._account, metadata, True)
        self._connect_transfer_signals(menu)
        return menu

    def _connect_transfer_signals(self, transfer_widget):
        transfer_widget.connect('transfer-state-changed',
                                self.__display_alert_cb)

    def __display_alert_cb(self, widget, message):
        if self._alert is None:
            self._alert = NotifyAlert()
            self._alert.props.title = ACCOUNT_NAME
            self._alert.connect('response', self.__alert_response_cb)
            journalwindow.get_journal_window().add_alert(self._alert)
            self._alert.show()
        self._alert.props.msg = message

    def __alert_response_cb(self, alert, response_id):
        journalwindow.get_journal_window().remove_alert(alert)
        self._alert = None


class _ShareMenu(MenuItem):
    __gsignals__ = {
        'transfer-state-changed': (GObject.SignalFlags.RUN_FIRST, None,
                                   ([str])),
    }

    def __init__(self, account, metadata, is_active):
        MenuItem.__init__(self, ACCOUNT_NAME)

        self._account = account
        self.set_image(Icon(icon_name=ACCOUNT_ICON,
                            icon_size=Gtk.IconSize.MENU))
        self.show()
        self._metadata = metadata

        self.connect('activate', self.__share_menu_cb)

    def _image_file_from_metadata(self, image_path):
        """ Load a pixbuf from a Journal object. """
        pixbufloader = \
            GdkPixbuf.PixbufLoader.new_with_mime_type('image/png')
        pixbufloader.set_size(300, 225)
        try:
            pixbufloader.write(self._metadata['preview'])
            pixbuf = pixbufloader.get_pixbuf()
        except Exception as ex:
            logging.debug("_image_file_from_metadata: %s" % (str(ex)))
            pixbuf = None

        pixbufloader.close()
        if pixbuf:
            pixbuf.savev(image_path, 'png', [], [])

    def __share_menu_cb(self, menu_item):
        self.emit('transfer-state-changed', _('Upload started'))
        project = self._account.gmoksaya.Project()
        project.connect('completed', self.__completed_cb)
        project.connect('updated', self.__updated_cb)
        project.connect('failed', self.__failed_cb)

        profile_id = self._account.get_public_id()
        title = str(self._metadata.get('title', _('Untitled')))
        description = self._metadata.get('description', _('No description'))

        jobject = datastore.get(self._metadata['uid'])
        project_file = str(jobject.file_path)

        __, screenshot_path = tempfile.mkstemp()
        self._image_file_from_metadata(screenshot_path)

        project.create(profile_id, title, description,
                       project_file, screenshot_path)

    def __updated_cb(self, project, tdown, down, tup, up):
        message = _('Uploading %d of %d KBs') % (up, tup)
        self.emit('transfer-state-changed', message)

    def __completed_cb(self, project, info):
        self.emit('transfer-state-changed',
                  _('Successfully uploaded'))

    def __failed_cb(self, project, info):
        self.emit('transfer-state-changed',
                  _('Cannot be uploaded this time, sorry! %s' % info))


class _MoksayaPost(account.WebServicePost):
    def __init__(self, message, title=None, link=None):
        self._title = title
        self._message = message
        self._picture = ACCOUNT_ICON
        self._link = link

    def get_title(self):
        return self._title

    def get_message(self):
        return self._message

    def get_picture(self):
        return self._picture

    def get_link(self):
        return self._link


def get_account():
    return Account()

def get_post(public_id):
    gmoksaya = accountsmanager.get_service('gmoksaya')
    project = gmoksaya.Project()
    projects_list = project.list(public_id)['projects']
    if projects_list:
        project_name = projects_list[0]['title']
        message = 'I shared a new project {}'.format(project_name)
        return _MoksayaPost(message=message)
    logging.debug('No posts found!')
    return None

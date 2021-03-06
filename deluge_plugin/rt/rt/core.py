#
# core.py
#
# Copyright (C) 2009 Muali <m-moskvitin92@yandex.ru>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2009 Damien Churchill <damoxc@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#

from deluge.log import LOG as log
from deluge.plugins.pluginbase import CorePluginBase
import deluge.component as component
import deluge.configmanager
from deluge.core.rpcserver import export
from twisted.internet.task import LoopingCall
from torrents_storage import TorrentsStorage
from sysv_ipc import MessageQueue
from threading import Thread

DEFAULT_PREFS = {
    "test":"NiNiNi"
}

class Core(CorePluginBase):
    def enable(self):
        self.config = deluge.configmanager.ConfigManager("myplugin.conf", DEFAULT_PREFS)
        
        core = component.get("Core")
        self.requests_queue = MessageQueue(87532)
        self.responces_queue = MessageQueue(98531)
        self.torrents_storage = TorrentsStorage(core)
        self.config = deluge.configmanager.ConfigManager("rt.conf", DEFAULT_PREFS)
        self.disabled = False
        self.thread = Thread(target=self.main)
        self.thread.start()

    def main(self):
        while not self.disabled:
            self.process_vfs_request()

    def parse_request_str(self, request_str):
        space_idx = request_str.find(' ')
        return int(request_str[:space_idx]), request_str[space_idx + 1:]

    def process_vfs_request(self):
        request_str, request_id = self.requests_queue.receive()
        offset, path = self.parse_request_str(request_str)

        self.torrents_storage.on_request(offset, path, 100, request_id, self.request_callback)

    def to_resp_str(self, allowed):
        return str(allowed) + '\0'

    def request_callback(self, request_id, result):
        self.responces_queue.send(self.to_resp_str(result), type=request_id)

    def disable(self):
        self.disabled = True

    def update(self):
        pass

    @export
    def set_config(self, config):
        """Sets the config dictionary"""
        for key in config.keys():
            self.config[key] = config[key]
        self.config.save()

    @export
    def get_config(self):
        """Returns the config dictionary"""
        return self.config.config

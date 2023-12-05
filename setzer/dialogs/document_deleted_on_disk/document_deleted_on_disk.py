#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017-present Robert Griesel
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

import os.path


class DocumentDeletedOnDiskDialog(object):

    def __init__(self, main_window):
        self.main_window = main_window
        self.parameters = None

    def run(self, parameters):
        if parameters['document'] == None: return

        self.parameters = parameters

        self.setup(self.parameters['document'])

        self.view.present()
        self.signal_connection_id = self.view.connect('response', self.process_response)

    def process_response(self, view, response_id):
        self.close()

    def close(self):
        self.view.close()
        self.view.disconnect(self.signal_connection_id)
        del(self.view)

    def setup(self, document):
        self.view = Gtk.MessageDialog()
        self.view.set_transient_for(self.main_window)
        self.view.set_modal(True)
        self.view.set_property('message-type', Gtk.MessageType.WARNING)

        self.view.set_property('text', _('Document »{document}« was deleted from disk or moved.').format(document=document.get_displayname()))
        self.view.set_property('secondary-text', _('If you close it or close Setzer without saving, this document will be lost.'))

        self.view.add_buttons(_('Ok'), Gtk.ResponseType.YES)
        self.view.set_default_response(Gtk.ResponseType.YES)



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


class BuildSaveDialog(object):

    def __init__(self, main_window):
        self.main_window = main_window
        self.callback = None

    def run(self, document, callback):
        self.setup(document)
        self.view.show()
        self.callback = callback
        self.signal_connection_id = self.view.connect('response', self.process_response)

    def close(self):
        self.view.hide()
        self.view.disconnect(self.signal_connection_id)
        del(self.view)

    def process_response(self, view, response_id):
        self.callback(response_id)
        self.close()

    def setup(self, document):
        self.view = Gtk.MessageDialog()
        self.view.set_transient_for(self.main_window)
        self.view.set_modal(True)
        self.view.set_property('message-type', Gtk.MessageType.QUESTION)

        self.view.set_property('text', _('Document »{document}« has no filename.').format(document=document.get_displayname()))
        self.view.set_property('secondary-text', _('Please save your document to a file, so the build system knows where to put the .pdf (it will be in the same folder as your document).'))
        self.view.add_buttons(_('_Cancel'), Gtk.ResponseType.CANCEL, _('_Save document now'), Gtk.ResponseType.YES)
        self.view.set_default_response(Gtk.ResponseType.YES)



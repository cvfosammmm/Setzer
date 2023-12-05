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


class OpenSessionDialog(object):

    def __init__(self, main_window, workspace):
        self.main_window = main_window
        self.workspace = workspace
        self.callback = None

    def run(self, callback):
        self.callback = callback
        self.setup()
        self.view.present()
        self.signal_connection_id = self.view.connect('response', self.process_response)

    def close(self):
        self.view.close()
        self.view.disconnect(self.signal_connection_id)
        del(self.view)

    def process_response(self, view, response_id):
        if response_id == Gtk.ResponseType.OK:
            return_value = self.view.get_file().get_path()
        else:
            return_value = None
        self.close()
        self.callback(return_value)

    def setup(self):
        self.view = Gtk.FileChooserDialog()
        self.view.set_transient_for(self.main_window)
        self.view.set_modal(True)
        self.view.set_action(Gtk.FileChooserAction.OPEN)
        self.view.add_button(_('_Cancel'), Gtk.ResponseType.CANCEL)
        button_open = Gtk.Button.new_with_mnemonic(_('_Open'))
        button_open.get_style_context().add_class('suggested-action')
        self.view.add_action_widget(button_open, Gtk.ResponseType.OK)
        self.view.set_title(_('Load Session'))

        file_filter1 = Gtk.FileFilter()
        file_filter1.add_pattern('*.stzs')
        file_filter1.set_name(_('Setzer Session'))
        self.view.add_filter(file_filter1)

        self.view.set_select_multiple(False)



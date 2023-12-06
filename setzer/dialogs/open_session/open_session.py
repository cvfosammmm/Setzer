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
        self.view = None

    def run(self, callback):
        self.callback = callback
        self.setup()
        self.view.open(self.main_window, None, self.dialog_process_response)

    def setup(self):
        self.view = Gtk.FileDialog()
        self.view.set_modal(True)
        self.view.set_title(_('Load Session'))

        file_filter = Gtk.FileFilter()
        file_filter.add_pattern('*.stzs')
        file_filter.set_name(_('Setzer Session'))
        self.view.set_default_filter(file_filter)

    def dialog_process_response(self, dialog, result):
        return_value = None
        try:
            file = dialog.open_finish(result)
        except Exception: pass
        else:
            if file != None:
                return_value = file.get_path()
        self.callback(return_value)



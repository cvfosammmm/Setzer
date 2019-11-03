#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017, 2018 Robert Griesel
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
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from dialogs.dialog import Dialog

import os.path


class KeyboardShortcutsDialog(Dialog):

    def __init__(self, main_window):
        self.main_window = main_window

    def run(self):
        self.setup()
        self.view.show_all()
        del(self.view)

    def setup(self):
        builder = Gtk.Builder()
        builder.add_from_file(os.path.dirname(os.path.realpath(__file__)) + '/shortcuts_window.ui')
        self.view = builder.get_object('shortcuts-window')
        self.view.set_transient_for(self.main_window)
        


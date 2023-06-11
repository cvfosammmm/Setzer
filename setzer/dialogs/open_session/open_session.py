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
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from setzer.dialogs.dialog import Dialog

import os.path


class OpenSessionDialog(Dialog):
    ''' File chooser for opening session files '''

    def __init__(self, main_window):
        self.main_window = main_window

    def run(self):
        self.setup()
        response = self.view.run()
        if response == Gtk.ResponseType.OK:
            return_value = self.view.get_filename()
        else:
            return_value = None
        self.close()
        return return_value

    def setup(self):
        self.action = Gtk.FileChooserAction.OPEN
        self.buttons = (_('_Cancel'), Gtk.ResponseType.CANCEL, _('_Open'), Gtk.ResponseType.OK)
        self.view = Gtk.FileChooserDialog(_('Load Session'), self.main_window, self.action, self.buttons)

        headerbar = self.view.get_header_bar()
        if headerbar != None:
            for widget in headerbar.get_children():
                if isinstance(widget, Gtk.Button) and widget.get_label() == _('_Open'):
                    widget.get_style_context().add_class('suggested-action')
                    widget.set_can_default(True)
                    widget.grab_default()

        file_filter1 = Gtk.FileFilter()
        file_filter1.add_pattern('*.stzs')
        file_filter1.set_name(_('Setzer Session'))
        self.view.add_filter(file_filter1)

        self.view.set_select_multiple(False)



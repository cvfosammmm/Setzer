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

from setzer.dialogs.dialog import Dialog

import os.path


class SaveSessionDialog(Dialog):
    ''' File chooser for saving editing sessions '''

    def __init__(self, main_window, workspace):
        self.main_window = main_window
        self.workspace = workspace

    def run(self):
        self.setup()
        document = self.workspace.get_active_document()
        if document != None:
            pathname = document.get_filename()
            if pathname != None:
                self.view.set_current_folder(os.path.dirname(pathname))
            self.view.set_current_name('.stzs')
        else:
            self.view.set_current_name('.stzs')
        response = self.view.run()
        if response == Gtk.ResponseType.OK:
            filename = self.view.get_filename()
            self.workspace.save_session(filename)
            return_value = True
        else:
            return_value = False
        self.close()
        return return_value

    def setup(self):
        self.action = Gtk.FileChooserAction.SAVE
        self.buttons = ('_Cancel', Gtk.ResponseType.CANCEL, '_Save', Gtk.ResponseType.OK)
        self.view = Gtk.FileChooserDialog('Save Session', self.main_window, self.action, self.buttons)

        self.view.set_do_overwrite_confirmation(True)

        headerbar = self.view.get_header_bar()
        if headerbar != None:
            for widget in headerbar.get_children():
                if isinstance(widget, Gtk.Button) and widget.get_label() == '_Save':
                    widget.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
                    widget.set_can_default(True)
                    widget.grab_default()
        


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


class SaveSessionDialog(Dialog):
    ''' File chooser for saving editing sessions '''

    def __init__(self, main_window, workspace):
        self.main_window = main_window
        self.workspace = workspace

    def run(self):
        self.setup()

        if self.workspace.session_file_opened != None:
            self.view.set_current_folder(os.path.dirname(self.workspace.session_file_opened))
            self.view.set_current_name(os.path.basename(self.workspace.session_file_opened))
        else:
            document = self.workspace.get_root_or_active_latex_document()
            if document != None:
                pathname = document.get_filename()
                if pathname != None:
                    self.view.set_current_folder(os.path.dirname(pathname))
                self.view.set_current_name('.stzs')
            else:
                self.view.set_current_name('.stzs')

        response = self.view.run()
        if response == Gtk.ResponseType.ACCEPT:
            filename = self.view.get_filename()
            self.workspace.save_session(filename)
            return_value = True
        else:
            return_value = False
        self.close()
        return return_value

    def setup(self):
        self.action = Gtk.FileChooserAction.SAVE
        self.view = Gtk.FileChooserNative.new(_('Save Session'), self.main_window, self.action, _('_Save'), _('_Cancel'))

        self.view.set_do_overwrite_confirmation(True)


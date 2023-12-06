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
from gi.repository import Gtk, Gio

import os.path


class SaveSessionDialog(object):

    def __init__(self, main_window, workspace):
        self.main_window = main_window
        self.workspace = workspace

    def run(self):
        self.setup()
        self.view.save(self.main_window, None, self.dialog_process_response)

    def setup(self):
        self.view = Gtk.FileDialog()
        self.view.set_modal(True)
        self.view.set_title(_('Save Session'))

        if self.workspace.session_file_opened != None:
            self.view.set_initial_folder(Gio.File.new_for_path(os.path.dirname(self.workspace.session_file_opened)))
            self.view.set_initial_name(os.path.basename(self.workspace.session_file_opened))
        else:
            document = self.workspace.get_root_or_active_latex_document()
            if document != None:
                pathname = document.get_filename()
                if pathname != None:
                    self.view.set_initial_folder(Gio.File.new_for_path(os.path.dirname(pathname)))
                self.view.set_initial_name('.stzs')
            else:
                self.view.set_initial_name('.stzs')

    def dialog_process_response(self, dialog, result):
        try:
            file = dialog.save_finish(result)
        except Exception: pass
        else:
            if file != None:
                filename = file.get_path()
                self.workspace.save_session(filename)



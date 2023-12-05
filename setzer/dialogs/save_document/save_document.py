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


class SaveDocumentDialog(object):

    def __init__(self, main_window, workspace):
        self.main_window = main_window
        self.workspace = workspace
        self.document = None

    def run(self, document):
        self.document = document
        self.setup()
        pathname = self.document.get_filename()
        if pathname != None:
            self.view.set_current_name(os.path.basename(pathname))
            self.view.set_current_folder(Gio.File.new_for_path(self.document.get_dirname()))
        else:
            if self.document.get_document_type() == 'latex':
                ending = '.tex'
            elif self.document.get_document_type() == 'bibtex':
                ending = '.bib'
            else:
                ending = ''
            self.view.set_current_name(ending)
        self.view.present()
        self.signal_connection_id = self.view.connect('response', self.process_response)

    def process_response(self, view, response_id):
        if response_id == Gtk.ResponseType.OK:
            filename = self.view.get_file().get_path()
            self.document.set_filename(filename)
            self.document.save_to_disk()
            self.workspace.update_recently_opened_document(filename)
        self.close()

    def close(self):
        self.view.close()
        self.view.disconnect(self.signal_connection_id)
        del(self.view)

    def setup(self):
        self.view = Gtk.FileChooserDialog()
        self.view.set_transient_for(self.main_window)
        self.view.set_modal(True)
        self.view.set_action(Gtk.FileChooserAction.SAVE)
        self.view.add_button(_('_Cancel'), Gtk.ResponseType.CANCEL)
        button_open = Gtk.Button.new_with_mnemonic(_('_Save'))
        button_open.get_style_context().add_class('suggested-action')
        self.view.add_action_widget(button_open, Gtk.ResponseType.OK)
        self.view.set_title(_('Save document'))



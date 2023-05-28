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
import setzer.dialogs.include_latex_file.include_latex_file_viewgtk as view

import os.path


class IncludeLaTeXFile(Dialog):

    def __init__(self, main_window):
        self.main_window = main_window
        self.pathtypes = {'rel' : _('Relative Path'), 'abs' : _('Absolute Path')}
        self.current_values = dict()

        self.view = view.IncludeLaTeXFileView(self.main_window)

        self.is_not_setup = True

    def run(self, document):
        self.document = document

        self.init_current_values()
        if self.is_not_setup:
            self.setup()
            self.is_not_setup = False

        self.view.pathtype_buttons[self.current_values['pathtype']].set_active(True)
        self.view.pathtype_buttons[self.current_values['pathtype']].toggled()
        self.view.pathtype_info_button.set_active(False)

        self.view.create_button.set_sensitive(False)
        self.view.file_chooser_button.reset()
        response = self.view.run()

        if response == Gtk.ResponseType.APPLY:
            self.insert_template()

        self.view.dialog.hide()

    def init_current_values(self):
        self.current_values['filename'] = ''
        self.current_values['pathtype'] = 'rel'
    
    def setup(self):
        file_filter1 = Gtk.FileFilter()
        file_filter1.add_pattern('*.tex')
        file_filter1.set_name(_('LaTeX Files'))
        self.view.file_chooser_button.add_filter(file_filter1)

        first_button = None
        for pathtype in self.pathtypes:
            self.view.pathtype_buttons[pathtype] = Gtk.RadioButton()
            if first_button == None: first_button = self.view.pathtype_buttons[pathtype]
            box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
            box.pack_start(Gtk.Label(self.pathtypes[pathtype]), False, False, 0)
            box.set_margin_right(6)
            box.set_margin_left(4)
            self.view.pathtype_buttons[pathtype].add(box)
            self.view.pathtype_buttons[pathtype].set_mode(False)
            if first_button != None:
                self.view.pathtype_buttons[pathtype].join_group(first_button)
            self.view.pathtype_switcher.pack_start(self.view.pathtype_buttons[pathtype], False, False, 0)
            self.view.pathtype_buttons[pathtype].connect('toggled', self.on_pathtype_chosen, pathtype)
            self.view.pathtype_info_button.connect('toggled', self.on_info_button_toggled)

        self.view.topbox.show_all()

        self.view.file_chooser_button.connect('file-set', self.on_file_chosen)

    def on_file_chosen(self, widget=None):
        self.view.create_button.set_sensitive(True)
        self.current_values['filename'] = self.view.file_chooser_button.get_filename()

    def on_info_button_toggled(self, button):
        self.view.description_revealer.set_reveal_child(button.get_active())

    def on_pathtype_chosen(self, button, pathtype):
        self.current_values['pathtype'] = pathtype

    def get_display_filename(self):
        if self.current_values['pathtype'] == 'rel':
            document_dir = self.document.get_dirname()
            return os.path.relpath(self.current_values['filename'], document_dir)
        else:
            return self.current_values['filename']

    def insert_template(self):
        text = '\\input{' + self.get_display_filename() + '}'
        self.document.content.insert_text_at_cursor_indent_and_select_dot(text)
        self.document.content.scroll_cursor_onscreen()



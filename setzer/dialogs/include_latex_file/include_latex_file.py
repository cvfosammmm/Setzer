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

import os.path, pickle

import setzer.dialogs.include_latex_file.include_latex_file_viewgtk as view
from setzer.app.service_locator import ServiceLocator


class IncludeLaTeXFile(object):

    def __init__(self, main_window):
        self.main_window = main_window
        self.settings = ServiceLocator.get_settings()
        self.pathtypes = {'rel' : _('Relative Path'), 'abs' : _('Absolute Path')}
        self.current_values = dict()

    def run(self, document):
        self.document = document

        self.init_current_values()
        self.view = view.IncludeLaTeXFileView(self.main_window)
        self.setup()

        self.view.pathtype_buttons[self.current_values['pathtype']].set_active(True)
        self.view.pathtype_buttons[self.current_values['pathtype']].toggled()
        self.view.pathtype_info_button.set_active(False)

        self.view.include_button.set_sensitive(False)
        self.view.file_chooser_button.reset()

        self.view.cancel_button.connect('clicked', self.on_cancel_button_clicked)
        self.view.include_button.connect('clicked', self.on_include_button_clicked)

        self.view.present()

    def on_cancel_button_clicked(self, button):
        self.view.close()

    def on_include_button_clicked(self, button):
        self.insert_template()

        self.view.close()

    def init_current_values(self):
        self.current_values['filename'] = ''
        self.current_values['pathtype'] = 'rel'
        try:
            presets = self.settings.get_value('app_include_latex_file_dialog', 'presets')
            presets = pickle.loads(presets)
            self.current_values['pathtype'] = presets['pathtype']
        except Exception: pass

    def setup(self):
        file_filter1 = Gtk.FileFilter()
        file_filter1.add_pattern('*.tex')
        file_filter1.set_name(_('LaTeX Files'))
        self.view.file_chooser_button.add_filter(file_filter1)

        first_button = None
        for pathtype in self.pathtypes:
            self.view.pathtype_buttons[pathtype] = Gtk.ToggleButton()
            box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
            box.append(Gtk.Label.new(self.pathtypes[pathtype]))
            box.set_margin_end(6)
            box.set_margin_start(4)
            self.view.pathtype_buttons[pathtype].set_child(box)
            if first_button != None:
                self.view.pathtype_buttons[pathtype].set_group(first_button)
            self.view.pathtype_switcher.append(self.view.pathtype_buttons[pathtype])
            self.view.pathtype_buttons[pathtype].connect('toggled', self.on_pathtype_chosen, pathtype)
            self.view.pathtype_info_button.connect('toggled', self.on_info_button_toggled)
            if first_button == None: first_button = self.view.pathtype_buttons[pathtype]

        self.view.file_chooser_button.connect('file-set', self.on_file_chosen)

    def on_file_chosen(self, widget=None):
        self.view.include_button.set_sensitive(True)
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
        self.settings.set_value('app_include_latex_file_dialog', 'presets', pickle.dumps(self.current_values))

        text = '\\input{' + self.get_display_filename() + '}'

        self.document.source_buffer.begin_user_action()
        self.document.source_buffer.delete_selection(False, False)
        self.document.source_buffer.insert_at_cursor(text)
        self.document.source_buffer.end_user_action()
        self.document.scroll_cursor_onscreen()



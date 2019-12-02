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
import dialogs.include_bibtex_file.include_bibtex_file_viewgtk as view

import pickle
import os


class IncludeBibTeXFile(Dialog):

    def __init__(self, main_window):
        self.main_window = main_window
        self.current_values = dict()

        self.view = view.IncludeBibTeXFileView(self.main_window)

        self.is_not_setup = True

    def run(self, document):
        self.document = document

        if self.is_not_setup:
            self.init_current_values()
            self.setup()
            self.is_not_setup = False

        self.view.create_button.set_sensitive(False)
        self.view.file_chooser_button.unselect_all()
        response = self.view.run()

        if response == Gtk.ResponseType.APPLY:
            self.insert_template()

        self.view.dialog.hide()

    def init_current_values(self):
        self.current_values['filename'] = ''
        self.current_values['style'] = 'plain'
    
    def setup(self):
        file_filter1 = Gtk.FileFilter()
        file_filter1.add_pattern('*.bib')
        file_filter1.set_name('BibTeX files')
        self.view.file_chooser_button.add_filter(file_filter1)

        first_button = None
        for name in ['Plain', 'Abbrv', 'Alpha', 'Apalike', 'iEEEtr']:
            style = name.lower()
            self.view.style_buttons[style] = Gtk.RadioButton()
            if first_button == None: first_button = self.view.style_buttons[style]
            box = Gtk.HBox()
            box.pack_start(Gtk.Label(name), False, False, 0)
            box.set_margin_right(6)
            box.set_margin_left(4)
            self.view.style_buttons[style].add(box)
            self.view.style_buttons[style].set_mode(False)
            if first_button != None:
                self.view.style_buttons[style].join_group(first_button)
            self.view.style_switcher.pack_start(self.view.style_buttons[style], False, False, 0)
            self.view.style_buttons[style].connect('toggled', self.on_style_chosen, style)

            image = Gtk.Image.new_from_file(os.path.dirname(__file__) + '/resources/' + style + '.png')
            self.view.preview_stack.add_named(image, style)
        self.view.topbox.show_all()

        first_button.set_active(True)
        first_button.toggled()

        self.view.file_chooser_button.connect('file-set', self.on_file_chosen)

    def on_file_chosen(self, widget=None):
        self.view.create_button.set_sensitive(True)
        self.current_values['filename'] = self.view.file_chooser_button.get_filename()

    def on_style_chosen(self, togglebutton, style):
        self.view.preview_stack.set_visible_child_name(style)
        self.current_values['style'] = style

    def get_display_filename(self):
        file_arr = self.current_values['filename'].rsplit('/', 1)
        if len(file_arr) > 1:
            return file_arr[1].rsplit('.', 1)[0]
        else:
            return '•'

    def get_style(self):
        return self.current_values['style']

    def insert_template(self):
        buffer = self.document.get_buffer()
        end_iter = buffer.get_end_iter()
        result = end_iter.backward_search('\\end{document}', Gtk.TextSearchFlags.VISIBLE_ONLY, None)
        if result != None:
            self.document.insert_text_at_iter(result[0], '''
\\bibliographystyle{''' + self.get_style() + '''}
\\bibliography{''' + self.get_display_filename() + '''}

''', False)
        else:
            self.document.insert_text_at_cursor('''\\bibliographystyle{''' + self.get_style() + '''}
\\bibliography{''' + self.get_display_filename() + '''}''')



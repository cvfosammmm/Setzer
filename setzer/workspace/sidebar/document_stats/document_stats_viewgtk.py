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


class DocumentStatsView(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)
        self.get_style_context().add_class('document-stats')

        description = Gtk.Label(_('These counts are updated after the document is saved.'))
        description.set_line_wrap(True)
        description.set_xalign(0)
        description.get_style_context().add_class('description')
        self.pack_start(description, False, False, 0)

        self.label_words_in_text = Gtk.Label()
        self.label_words_in_headers = Gtk.Label()
        self.label_words_outside_text = Gtk.Label()

        self.add_line(_('Words in text:  '), self.label_words_in_text)
        self.add_line(_('Words in headers:  '), self.label_words_in_headers)
        self.add_line(_('Words outside text:  '), self.label_words_outside_text)

        self.show_all()

    def add_line(self, description_text, values_label):
        box = Gtk.HBox()
        box.pack_start(Gtk.Label(description_text), False, False, 0)
        values_label.set_xalign(1)
        box.pack_start(values_label, False, False, 0)
        self.pack_start(box, False, False, 0)



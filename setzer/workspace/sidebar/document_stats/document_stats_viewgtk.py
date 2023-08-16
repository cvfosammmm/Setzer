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
from gi.repository import Gtk, Pango


class DocumentStatsView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('document-stats')

        description = Gtk.Label.new(_('These counts are updated after the document is saved.'))
        description.set_wrap(True)
        description.set_xalign(0)
        description.get_style_context().add_class('description')
        self.append(description)

        self.label_whole_document = Gtk.Label()
        self.label_whole_document.set_wrap(True)
        self.label_whole_document.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.label_whole_document.set_xalign(0)
        self.label_whole_document.get_style_context().add_class('stats-paragraph')
        self.append(self.label_whole_document)

        self.label_current_file = Gtk.Label()
        self.label_current_file.set_wrap(True)
        self.label_current_file.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.label_current_file.set_xalign(0)
        self.label_current_file.get_style_context().add_class('stats-paragraph')
        self.append(self.label_current_file)



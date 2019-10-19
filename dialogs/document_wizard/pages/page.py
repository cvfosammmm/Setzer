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


class Page(object):

    def load_presets(self, presets):
        pass

    def on_activation(self):
        pass


class PageView(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)
        self.get_style_context().add_class('document-wizard-page')

        self.set_margin_start(18)
        self.set_margin_top(18)
        self.set_margin_bottom(18)

        self.header = Gtk.Label()
        self.header.set_xalign(0)
        self.header.set_margin_bottom(12)
        self.header.get_style_context().add_class('document-wizard-header')
        
        self.headerbar_subtitle = ''

    def set_document_settings_page(self):
        self.headerbar_subtitle = 'Step 2'
        self.content = Gtk.HBox()
        self.left_content = Gtk.VBox()

        self.subheader_page_format = Gtk.Label('Page format')
        self.subheader_page_format.get_style_context().add_class('document-wizard-subheader')
        self.subheader_page_format.set_xalign(0)

        self.page_format_list = Gtk.ListBox()
        self.page_format_list.set_can_focus(True)
        self.page_format_list.set_size_request(348, -1)
        self.page_format_list_rows = dict()
        for name in ['B5', 'A5', 'A4', 'US Legal', 'US Letter']:
            label = Gtk.Label(name)
            label.set_xalign(0)
            self.page_format_list.prepend(label)
        for row in self.page_format_list.get_children():
            self.page_format_list_rows[row.get_child().get_text()] = row
        self.page_format_list.set_margin_right(0)
        self.page_format_list.set_vexpand(False)
        self.page_format_list.get_style_context().add_class('document-wizard-list1')
        
        self.subheader_font_size = Gtk.Label('Font size')
        self.subheader_font_size.get_style_context().add_class('document-wizard-subheader')
        self.subheader_font_size.set_xalign(0)
        self.subheader_font_size.set_margin_top(18)

        self.font_size_entry = Gtk.HScale.new_with_range(6, 18, 1)



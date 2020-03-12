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
from gi.repository import GLib
from gi.repository import Gtk

from setzer.dialogs.document_wizard.pages.page import Page, PageView

import os


class DocumentClassPage(Page):

    def __init__(self, current_values):
        self.current_values = current_values
        self.view = DocumentClassPageView()

    def observe_view(self):
        def row_selected(box, row, user_data=None):
            child_name = row.get_child().get_text().lower()
            self.current_values['document_class'] = child_name
            self.view.preview_container.set_visible_child_name(child_name)

        self.view.list.connect('row-selected', row_selected)

    def load_presets(self, presets):
        try:
            row = self.view.list_rows[presets['document_class']]
        except TypeError:
            row = self.view.list_rows[self.current_values['document_class']]
        self.view.list.select_row(row)

    def on_activation(self):
        GLib.idle_add(self.view.list.get_selected_row().grab_focus)


class DocumentClassPageView(PageView):

    def __init__(self):
        PageView.__init__(self)
            
        self.header.set_text('Choose a document class')
        self.headerbar_subtitle = 'Step 1: Choose document class'
        self.content = Gtk.HBox()
        
        self.list = Gtk.ListBox()
        self.list.set_can_focus(True)
        self.list.set_size_request(348, -1)
        self.list_rows = dict()
        for name in ['Beamer', 'Letter', 'Book', 'Report', 'Article']:
            label = Gtk.Label(name)
            label.set_xalign(0)
            self.list.prepend(label)
        for row in self.list.get_children():
            self.list_rows[row.get_child().get_text().lower()] = row
            row.set_can_focus(True)
        self.list.set_margin_right(0)
        self.list.set_vexpand(False)
        self.list.get_style_context().add_class('document-wizard-list1')
        
        self.preview_container = Gtk.Stack()
        self.preview_container.set_size_request(366, -1)
        self.preview_data = list()
        self.preview_data.append({'name': 'article', 'image': 'article1.svg', 'text': '<b>Article:</b>  For articles in scientific journals, term\npapers, handouts, short reports, ...\n\nThis class on its own is pretty simplistic and\nis often used as a starting point for more\ncustom layouts.'})
        self.preview_data.append({'name': 'book', 'image': 'book1.svg', 'text': '<b>Book:</b>  For actual books containing many chapters\nand sections.'})
        self.preview_data.append({'name': 'report', 'image': 'report1.svg', 'text': '<b>Report:</b>  For longer reports and articles containing\nmore than one chapter, small books, thesis.'})
        self.preview_data.append({'name': 'letter', 'image': 'letter1.svg', 'text': '<b>Letter:</b>  For writing letters.'})
        self.preview_data.append({'name': 'beamer', 'image': 'beamer1.svg', 'text': '<b>Beamer:</b>  A class for making presentation slides\nwith LaTeX.\n\nThere are many predefined presentation styles.'})
        for item in self.preview_data:
            box = Gtk.VBox()
            image = Gtk.Image.new_from_file(os.path.dirname(__file__) + '/../resources/' + item['image'])
            image.set_margin_bottom(6)
            label = Gtk.Label()
            label.set_markup(item['text'])
            label.set_xalign(0)
            label.set_margin_start(19)
            box.pack_start(image, False, False, 0)
            box.pack_start(label, False, False, 0)
            self.preview_container.add_named(box, item['name'])
        
        self.pack_start(self.header, False, False, 0)
        self.content.pack_start(self.list, False, False, 0)
        self.content.pack_start(self.preview_container, False, False, 0)
        self.pack_start(self.content, False, False, 0)
        self.show_all()



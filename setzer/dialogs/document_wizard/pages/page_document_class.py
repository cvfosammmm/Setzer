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
from gi.repository import GLib
from gi.repository import Gtk

from setzer.dialogs.document_wizard.pages.page import Page, PageView
from setzer.app.service_locator import ServiceLocator
import setzer.widgets.async_svg.async_svg as async_svg

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
        pass


class DocumentClassPageView(PageView):

    def __init__(self):
        PageView.__init__(self)

        self.header.set_text(_('Choose a document class'))
        self.headerbar_subtitle = _('Step') + ' 1: ' + _('Choose a document class')
        
        self.list = Gtk.ListBox()
        self.list.set_selection_mode(Gtk.SelectionMode.BROWSE)
        self.list.set_size_request(348, -1)
        self.list.set_can_focus(False)
        self.list_rows = dict()
        for document_class in ['beamer', 'letter', 'book', 'report', 'article']:
            label = Gtk.Label.new(document_class.title())
            label.set_xalign(0)
            row = Gtk.ListBoxRow()
            row.set_child(label)
            self.list_rows[row.get_child().get_text().lower()] = row
            self.list.prepend(row)

        self.list.set_vexpand(False)
        self.list.get_style_context().add_class('document-wizard-list1')
        
        self.preview_container = Gtk.Stack()
        self.preview_container.set_size_request(366, -1)
        self.preview_data = list()
        self.preview_data.append({'name': 'article', 'image': 'article1.svg', 'text': _('<b>Article:</b>  For articles in scientific journals, term papers, handouts, short reports, …\n\nThis class on its own is pretty simplistic and is often used as a starting point for more custom layouts.')})
        self.preview_data.append({'name': 'book', 'image': 'book1.svg', 'text': _('<b>Book:</b>  For actual books containing many chapters and sections.')})
        self.preview_data.append({'name': 'report', 'image': 'report1.svg', 'text': _('<b>Report:</b>  For longer reports and articles containing more than one chapter, small books, thesis.')})
        self.preview_data.append({'name': 'letter', 'image': 'letter1.svg', 'text': _('<b>Letter:</b>  For writing letters.')})
        self.preview_data.append({'name': 'beamer', 'image': 'beamer1.svg', 'text': _('<b>Beamer:</b>  A class for making presentation slides with LaTeX.\n\nThere are many predefined presentation styles.')})
        for item in self.preview_data:
            image = async_svg.AsyncSvg(os.path.join(ServiceLocator.get_resources_path(), 'document_wizard', item['image']), 374, 262)
            image.set_margin_bottom(6)

            label = Gtk.Label()
            label.set_markup(item['text'])
            label.set_xalign(0)
            label.set_wrap(True)
            label.set_margin_start(19)
            label.set_margin_end(18)

            box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
            box.append(image)
            box.append(label)

            self.preview_container.add_named(box, item['name'])
        
        self.content = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.content.append(self.list)
        self.content.append(self.preview_container)

        self.append(self.header)
        self.append(self.content)



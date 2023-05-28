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
from gi.repository import GLib
from gi.repository import Gtk

from setzer.dialogs.bibtex_wizard.pages.page import Page, PageView

import os


class CreateNewEntryPage(Page):

    def __init__(self, wizard, document_types, current_values):
        self.wizard = wizard
        self.document_types = document_types
        self.current_values = current_values
        self.view = CreateNewEntryPageView(self.document_types)

    def observe_view(self):
        def row_selected(box, row, user_data=None):
            child_name = row.document_type
            self.view.preview_container.set_visible_child_name(child_name)
            self.wizard.set_document_type(child_name)

        self.view.list.connect('row-selected', row_selected)

    def load_presets(self, presets):
        if presets != None and 'document_type' in presets:
            document_type = presets['document_type']
        else:
            document_type = self.current_values['document_type']
        row = self.view.list_rows[document_type]
        self.view.list.select_row(row)

    def on_activation(self):
        GLib.idle_add(self.view.list.get_selected_row().grab_focus)


class CreateNewEntryPageView(PageView):

    def __init__(self, document_types):
        PageView.__init__(self)
        self.document_types = document_types
            
        self.header.set_text(_('Choose a document type'))
        self.headerbar_subtitle = _('Step') + ' 1: ' + _('Choose a document type')
        self.content = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)

        self.list_wrapper = Gtk.ScrolledWindow()
        self.list_wrapper.set_size_request(350, 350)
        self.list_wrapper.get_style_context().add_class('bibtex-wizard-list1')
        self.list = Gtk.ListBox()
        self.list.set_can_focus(True)
        self.list.set_size_request(348, -1)
        self.list_rows = dict()
        for document_type, attributes in self.document_types.items():
            row = DocumentSelectionRowView(document_type, attributes['title'])
            self.list.add(row)
            self.list_rows[document_type] = row
        self.list.set_margin_right(0)
        self.list.set_vexpand(False)
        self.list_wrapper.add(self.list)

        self.preview_container = Gtk.Stack()
        self.preview_container.set_size_request(348, -1)
        self.preview_container.set_margin_right(18)
        for document_type, attributes in self.document_types.items():
            box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
            label = Gtk.Label()
            label.set_line_wrap(True)
            markup = '<b>@' + document_type + '</b>\n\n'
            markup += attributes['description'] + '\n\n'
            markup += _('Required fields') + ': '
            is_first = True
            for attribute in attributes['fields_required']:
                if not is_first:
                    markup += ', '
                is_first = False
                markup += attribute
            markup += '\n\n' + _('Optional fields') + ': '
            is_first = True
            for attribute in attributes['fields_optional']:
                if not is_first:
                    markup += ', '
                is_first = False
                markup += attribute
            label.set_markup(markup)
            label.set_xalign(0)
            label.set_margin_start(19)
            box.pack_start(label, False, False, 0)
            self.preview_container.add_named(box, document_type)
        
        self.pack_start(self.header, False, False, 0)
        self.content.pack_start(self.list_wrapper, False, False, 0)
        self.content.pack_start(self.preview_container, False, False, 0)
        self.pack_start(self.content, False, False, 0)
        self.show_all()


class DocumentSelectionRowView(Gtk.ListBoxRow):

    def __init__(self, document_type, title):
        Gtk.ListBoxRow.__init__(self)
        self.document_type = document_type
        self.set_can_focus(True)
        label = Gtk.Label(title)
        label.set_xalign(0)
        self.add(label)



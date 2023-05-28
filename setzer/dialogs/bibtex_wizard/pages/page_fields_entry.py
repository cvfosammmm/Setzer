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

from setzer.dialogs.bibtex_wizard.pages.page import Page, PageView

import os


class FieldsEntryPage(Page):

    def __init__(self, wizard, current_values):
        self.wizard = wizard
        self.current_values = current_values
        self.view = FieldsEntryPageView(self.wizard.fields)
        self.required_fields = list()
        self.blank_required_fields = list()

    def observe_view(self):
        def text_deleted(buffer, position, n_chars, field_name):
            text = buffer.get_text()
            if field_name == 'identifier':
                self.current_values['identifier'] = text
            else:
                self.current_values['fields'][field_name] = text
            if text == '' and field_name in self.required_fields:
                self.blank_required_fields.append(field_name)
            self.wizard.check_required_fields()

        def text_inserted(buffer, position, chars, n_chars, field_name):
            text = buffer.get_text()
            if field_name == 'identifier':
                self.current_values['identifier'] = text
            else:
                self.current_values['fields'][field_name] = text
            if text != '':
                try: self.blank_required_fields.remove(field_name)
                except ValueError: pass
            self.wizard.check_required_fields()

        self.view.identifier_entry.text_entry.get_buffer().connect('deleted-text', text_deleted, 'identifier')
        self.view.identifier_entry.text_entry.get_buffer().connect('inserted-text', text_inserted, 'identifier')

        for entry_view in self.view.required_entry_views.values():
            entry_view.text_entry.get_buffer().connect('deleted-text', text_deleted, entry_view.field_name)
            entry_view.text_entry.get_buffer().connect('inserted-text', text_inserted, entry_view.field_name)

        for entry_view in self.view.optional_entry_views.values():
            entry_view.text_entry.get_buffer().connect('deleted-text', text_deleted, entry_view.field_name)
            entry_view.text_entry.get_buffer().connect('inserted-text', text_inserted, entry_view.field_name)

    def load_presets(self, presets):
        if presets != None and 'include_empty_optional' in presets:
            include_empty_optional = presets['include_empty_optional']
        else: 
            include_empty_optional = False
        self.view.option_include_empty.set_active(include_empty_optional)
        self.view.identifier_entry.text_entry.set_text('')
        self.view.identifier_entry.text_entry.grab_focus()

        for entry_view in self.view.required_entry_views.values():
            entry_view.text_entry.set_text('')

        for entry_view in self.view.optional_entry_views.values():
            entry_view.text_entry.set_text('')

    def on_activation(self):
        pass


class FieldsEntryPageView(Gtk.Overlay):

    def __init__(self, fields):
        Gtk.Overlay.__init__(self)
        self.get_style_context().add_class('bibtex-wizard-page')

        self.scrolled_window = Gtk.ScrolledWindow()
        self.vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.vbox.set_margin_start(18)
        self.vbox.set_margin_top(18)
        self.vbox.set_margin_bottom(18)
        self.vbox.set_margin_right(382)
        self.scrolled_window.add(self.vbox)

        self.headerbar_subtitle = _('Step') + ' 2: ' + _('Entry fields')

        self.header1 = Gtk.Label()
        self.header1.set_xalign(0)
        self.header1.set_margin_bottom(12)
        self.header1.get_style_context().add_class('bibtex-wizard-header')
        self.header1.set_text(_('Required fields'))

        self.required_entry_views = dict()
        self.required_fields_entries = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.identifier_entry = FieldsEntryView('identifier')
        for field_name, attributes in fields.items():
            self.required_entry_views[field_name] = FieldsEntryView(field_name)

        self.header2 = Gtk.Label()
        self.header2.set_xalign(0)
        self.header2.set_margin_bottom(12)
        self.header2.set_margin_top(18)
        self.header2.get_style_context().add_class('bibtex-wizard-header')
        self.header2.set_text(_('Optional fields'))

        self.option_include_empty = Gtk.CheckButton.new_with_label(_('Insert empty optional fields'))
        self.option_include_empty.set_margin_bottom(18)

        self.optional_entry_views = dict()
        self.optional_fields_entries = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        for field_name, attributes in fields.items():
            self.optional_entry_views[field_name] = FieldsEntryView(field_name)

        self.vbox.pack_start(self.header1, False, False, 0)
        self.vbox.pack_start(self.required_fields_entries, False, False, 0)
        self.vbox.pack_start(self.header2, False, False, 0)
        self.vbox.pack_start(self.option_include_empty, False, False, 0)
        self.vbox.pack_start(self.optional_fields_entries, False, False, 0)
        self.add(self.scrolled_window)
        self.show_all()


class FieldsEntryView(Gtk.Box):

    def __init__(self, field_name):
        Gtk.Box.__init__(self, orientation = Gtk.Orientation.HORIZONTAL)
        self.field_name = field_name
        self.label = Gtk.Label(field_name + ':')
        self.label.set_xalign(0)
        self.label.set_margin_right(6)
        self.text_entry = Gtk.Entry()
        self.text_entry.set_size_request(230, -1)
        self.pack_start(self.label, True, True, 0)
        self.pack_start(self.text_entry, False, False, 0)



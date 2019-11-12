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
from gi.repository import GLib

from dialogs.document_wizard.pages.page import Page, PageView

import os


class BookSettingsPage(Page):

    def __init__(self, current_values):
        self.current_values = current_values
        self.view = BookSettingsPageView()

    def observe_view(self):
        def format_changed(box, user_data=None):
            format_name = box.get_active_text()
            self.current_values['book']['page_format'] = format_name

        def scale_change_value(scale, scroll, value, user_data=None):
            self.current_values['book']['font_size'] = int(value)

        def option_toggled(button, option_name):
            self.current_values['book']['option_' + option_name] = button.get_active()

        def margin_changed(button, side):
            self.current_values['book']['margin_' + side] = button.get_value()

        def on_orientation_toggle(button, button_name):
            if button_name == 'portrait':
                self.current_values['book']['is_landscape'] = not button.get_active()
            elif button_name == 'landscape':
                self.current_values['book']['is_landscape'] = button.get_active()

        self.view.page_format_list.connect('changed', format_changed)
        self.view.font_size_entry.connect('change-value', scale_change_value)
        self.view.option_twocolumn.connect('toggled', option_toggled, 'twocolumn')
        self.view.option_default_margins.connect('toggled', self.option_default_margins_toggled, 'default_margins')
        self.view.margins_button_left.connect('value-changed', margin_changed, 'left')
        self.view.margins_button_right.connect('value-changed', margin_changed, 'right')
        self.view.margins_button_top.connect('value-changed', margin_changed, 'top')
        self.view.margins_button_bottom.connect('value-changed', margin_changed, 'bottom')
        self.view.option_portrait.connect('toggled', on_orientation_toggle, 'portrait')
        self.view.option_landscape.connect('toggled', on_orientation_toggle, 'landscape')

    def option_default_margins_toggled(self, button, option_name=None):
        for spinbutton in [self.view.margins_button_left, self.view.margins_button_right, self.view.margins_button_top, self.view.margins_button_bottom]:
            spinbutton.set_sensitive(not button.get_active())
            if button.get_active():
                spinbutton.set_value(3.5)
        if option_name != None:
            self.current_values['book']['option_' + option_name] = button.get_active()

    def load_presets(self, presets):
        try:
            value = presets['book']['page_format']
        except TypeError:
            value = self.current_values['book']['page_format']
        self.view.page_format_list.set_active_id(value)

        try:
            value = presets['book']['font_size']
        except TypeError:
            value = self.current_values['book']['font_size']
        self.view.font_size_entry.set_value(value)

        try:
            is_active = presets['book']['option_twocolumn']
        except TypeError:
            is_active = self.current_values['book']['option_twocolumn']
        self.view.option_twocolumn.set_active(is_active)

        try:
            value = presets['book']['margin_left']
        except TypeError:
            value = self.current_values['book']['margin_left']
        self.view.margins_button_left.set_value(value)

        try:
            value = presets['book']['margin_right']
        except TypeError:
            value = self.current_values['book']['margin_right']
        self.view.margins_button_right.set_value(value)

        try:
            value = presets['book']['margin_top']
        except TypeError:
            value = self.current_values['book']['margin_top']
        self.view.margins_button_top.set_value(value)

        try:
            value = presets['book']['margin_bottom']
        except TypeError:
            value = self.current_values['book']['margin_bottom']
        self.view.margins_button_bottom.set_value(value)

        try:
            is_active = presets['book']['option_default_margins']
        except TypeError:
            is_active = self.current_values['book']['option_default_margins']
        self.view.option_default_margins.set_active(is_active)
        self.option_default_margins_toggled(self.view.option_default_margins)

        try:
            is_landscape = presets['book']['is_landscape']
        except TypeError:
            is_landscape = self.current_values['book']['is_landscape']
        self.view.option_landscape.set_active(is_landscape)

    def on_activation(self):
        GLib.idle_add(self.view.page_format_list.grab_focus)


class BookSettingsPageView(PageView):

    def __init__(self):
        PageView.__init__(self)
        self.set_document_settings_page()

        self.header.set_text('Book settings')

        self.subheader_options = Gtk.Label('Options')
        self.subheader_options.get_style_context().add_class('document-wizard-subheader')
        self.subheader_options.set_xalign(0)
        self.subheader_options.set_margin_top(18)

        self.option_twocolumn = Gtk.CheckButton.new_with_label('Two-column layout')

        self.pack_start(self.header, False, False, 0)

        self.left_content.pack_start(self.subheader_page_format, False, False, 0)
        self.left_content.pack_start(self.page_format_list, False, False, 0)
        self.left_content.pack_start(self.orientation_box, False, False, 0)
        self.left_content.pack_start(self.subheader_margins, False, False, 0)
        self.left_content.pack_start(self.option_default_margins, False, False, 0)
        self.left_content.pack_start(self.margins_box, False, False, 0)

        self.right_content.pack_start(self.subheader_font_size, False, False, 0)
        self.right_content.pack_start(self.font_size_entry, False, False, 0)
        self.right_content.pack_start(self.subheader_options, False, False, 0)
        self.right_content.pack_start(self.option_twocolumn, False, False, 0)

        self.content.pack_start(self.left_content, False, False, 0)
        self.content.pack_start(self.right_content, False, False, 0)
        self.pack_start(self.content, False, False, 0)
        self.show_all()



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


class LetterSettingsPage(Page):

    def __init__(self, current_values):
        self.current_values = current_values
        self.view = LetterSettingsPageView()

    def observe_view(self):
        def format_changed(box, user_data=None):
            format_name = box.get_active_text()
            self.current_values['letter']['page_format'] = format_name

        def scale_change_value(scale, scroll, value, user_data=None):
            self.current_values['letter']['font_size'] = int(value)

        def margin_changed(button, side):
            self.current_values['letter']['margin_' + side] = button.get_value()

        self.view.page_format_list.connect('changed', format_changed)
        self.view.font_size_entry.connect('change-value', scale_change_value)
        self.view.option_default_margins.connect('toggled', self.option_default_margins_toggled, 'default_margins')
        self.view.margins_button_left.connect('value-changed', margin_changed, 'left')
        self.view.margins_button_right.connect('value-changed', margin_changed, 'right')
        self.view.margins_button_top.connect('value-changed', margin_changed, 'top')
        self.view.margins_button_bottom.connect('value-changed', margin_changed, 'bottom')

    def option_default_margins_toggled(self, button, option_name=None):
        for spinbutton in [self.view.margins_button_left, self.view.margins_button_right, self.view.margins_button_top, self.view.margins_button_bottom]:
            spinbutton.set_sensitive(not button.get_active())
            if button.get_active():
                spinbutton.set_value(3.5)
        if option_name != None:
            self.current_values['letter']['option_' + option_name] = button.get_active()

    def load_presets(self, presets):
        try:
            value = presets['letter']['page_format']
        except TypeError:
            value = self.current_values['letter']['page_format']
        self.view.page_format_list.set_active_id(value)

        try:
            value = presets['letter']['font_size']
        except TypeError:
            value = self.current_values['letter']['font_size']
        self.view.font_size_entry.set_value(value)

        try:
            value = presets['letter']['margin_left']
        except TypeError:
            value = self.current_values['letter']['margin_left']
        self.view.margins_button_left.set_value(value)

        try:
            value = presets['letter']['margin_right']
        except TypeError:
            value = self.current_values['letter']['margin_right']
        self.view.margins_button_right.set_value(value)

        try:
            value = presets['letter']['margin_top']
        except TypeError:
            value = self.current_values['letter']['margin_top']
        self.view.margins_button_top.set_value(value)

        try:
            value = presets['letter']['margin_bottom']
        except TypeError:
            value = self.current_values['letter']['margin_bottom']
        self.view.margins_button_bottom.set_value(value)

        try:
            is_active = presets['letter']['option_default_margins']
        except TypeError:
            is_active = self.current_values['letter']['option_default_margins']
        self.view.option_default_margins.set_active(is_active)
        self.option_default_margins_toggled(self.view.option_default_margins)

    def on_activation(self):
        GLib.idle_add(self.view.page_format_list.grab_focus)


class LetterSettingsPageView(PageView):

    def __init__(self):
        PageView.__init__(self)
        self.set_document_settings_page()
            
        self.header.set_text('Letter settings')

        self.pack_start(self.header, False, False, 0)

        self.left_content.pack_start(self.subheader_page_format, False, False, 0)
        self.left_content.pack_start(self.page_format_list, False, False, 0)
        self.left_content.pack_start(self.subheader_margins, False, False, 0)
        self.left_content.pack_start(self.option_default_margins, False, False, 0)
        self.left_content.pack_start(self.margins_box, False, False, 0)

        self.right_content.pack_start(self.subheader_font_size, False, False, 0)
        self.right_content.pack_start(self.font_size_entry, False, False, 0)

        self.content.pack_start(self.left_content, False, False, 0)
        self.content.pack_start(self.right_content, False, False, 0)
        self.pack_start(self.content, False, False, 0)
        self.show_all()



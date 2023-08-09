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
from gi.repository import Gtk
from gi.repository import GLib

from setzer.dialogs.document_wizard.pages.page import Page, PageView

import os


class ArticleSettingsPage(Page):

    def __init__(self, current_values):
        self.current_values = current_values
        self.view = ArticleSettingsPageView()

    def observe_view(self):
        def format_button_toggled(button, format_name):
            if button.get_active():
                self.current_values['article']['page_format'] = format_name

        def scale_change_value(scale, scroll, value, user_data=None):
            self.current_values['article']['font_size'] = int(value)

        def option_toggled(button, option_name):
            self.current_values['article']['option_' + option_name] = button.get_active()

        def margin_changed(button, side):
            self.current_values['article']['margin_' + side] = button.get_value()

        def on_orientation_toggle(button):
            self.current_values['article']['is_landscape'] = button.get_active()

        for name, button in self.view.page_format_buttons.items():
            button.connect('toggled', format_button_toggled, name)
        self.view.font_size_entry.connect('change-value', scale_change_value)
        self.view.option_twocolumn.connect('toggled', option_toggled, 'twocolumn')
        self.view.option_default_margins.connect('toggled', self.option_default_margins_toggled, 'default_margins')
        self.view.margins_button_left.connect('value-changed', margin_changed, 'left')
        self.view.margins_button_right.connect('value-changed', margin_changed, 'right')
        self.view.margins_button_top.connect('value-changed', margin_changed, 'top')
        self.view.margins_button_bottom.connect('value-changed', margin_changed, 'bottom')
        self.view.option_landscape.connect('toggled', on_orientation_toggle)

    def option_default_margins_toggled(self, button, option_name=None):
        for spinbutton in [self.view.margins_button_left, self.view.margins_button_right, self.view.margins_button_top, self.view.margins_button_bottom]:
            spinbutton.set_sensitive(not button.get_active())
            if button.get_active():
                spinbutton.set_value(3.5)
        if option_name != None:
            self.current_values['article']['option_' + option_name] = button.get_active()

    def load_presets(self, presets):
        for setter_function, value_name in [
            (self.view.font_size_entry.set_value, 'font_size'),
            (self.view.margins_button_left.set_value, 'margin_left'),
            (self.view.margins_button_right.set_value, 'margin_right'),
            (self.view.margins_button_top.set_value, 'margin_top'),
            (self.view.margins_button_bottom.set_value, 'margin_bottom'),
            (self.view.option_twocolumn.set_active, 'option_twocolumn'),
            (self.view.option_landscape.set_active, 'is_landscape'),
            (self.view.option_default_margins.set_active, 'option_default_margins')
        ]:
            try:
                value = presets['article'][value_name]
            except TypeError:
                value = self.current_values['article'][value_name]
            setter_function(value)

        try: value = presets['article']['page_format']
        except Exception: value = self.current_values['article']['page_format']
        for name, button in self.view.page_format_buttons.items():
            button.set_active(name == value)

        self.option_default_margins_toggled(self.view.option_default_margins)

    def on_activation(self):
        pass


class ArticleSettingsPageView(PageView):

    def __init__(self):
        PageView.__init__(self)
        self.set_document_settings_page()
            
        self.header.set_text(_('Article settings'))
        self.headerbar_subtitle = _('Step') + ' 2: ' + _('Article settings')

        self.right_content.append(self.subheader_page_format)
        self.right_content.append(self.page_format_list)

        self.left_content.append(self.subheader_options)
        self.left_content.append(self.option_landscape)
        self.left_content.append(self.option_twocolumn)
        self.left_content.append(self.subheader_font_size)
        self.left_content.append(self.font_size_entry)
        self.left_content.append(self.subheader_margins)
        self.left_content.append(self.option_default_margins)
        self.left_content.append(self.margins_box)
        self.left_content.append(self.margins_description)

        self.content.append(self.left_content)

        self.append(self.header)
        self.append(self.right_content)
        self.append(self.content)



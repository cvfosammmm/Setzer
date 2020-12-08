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
from gi.repository import Pango
from gi.repository import Gtk

from setzer.helpers.observable import Observable


class FontManager(Observable):

    def __init__(self, main_window, settings):
        Observable.__init__(self)

        self.main_window = main_window
        self.settings = settings
        self.settings.register_observer(self)

        textview = Gtk.TextView()
        textview.set_monospace(True)
        self.system_font = textview.get_pango_context().get_font_description().to_string()
        self.font_string = None
        self.update_font_string()

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'settings_changed':
            section, item, value = parameter
            if (section, item) in [('preferences', 'font_string'), ('preferences', 'use_system_font')]:
                self.update_font_string()

    def update_font_string(self):
        self.set_font_string(self.get_normal_font_string())

    def get_system_font(self):
        return self.system_font

    def get_line_height(self, text_view):
        char_width, line_height = self.get_char_dimensions(text_view)
        return line_height

    def get_char_width(self, text_view, char='A'):
        char_width, line_height = self.get_char_dimensions(text_view, char)
        return char_width

    def get_char_dimensions(self, text_view, char='A'):
        context = text_view.get_pango_context()
        font_desc = Pango.FontDescription.from_string(self.font_string)
        layout = Pango.Layout.new(context)
        layout.set_text(char, -1)
        layout.set_font_description(font_desc)
        return layout.get_pixel_size()

    def get_zoom_level(self):
        return self.get_font_size() / self.get_normal_font_size()

    def set_font_string(self, font_string):
        font_desc = Pango.FontDescription.from_string(font_string)
        font_size = font_desc.get_size() / Pango.SCALE

        self.font_string = font_string
        self.propagate_font_setting()
        self.add_change_code('font_string_changed')

    def zoom_in(self):
        font_desc = Pango.FontDescription.from_string(self.font_string)
        font_desc.set_size(min(self.get_font_size() * 1.1, 24 * Pango.SCALE))
        self.set_font_string(font_desc.to_string())

    def zoom_out(self):
        font_desc = Pango.FontDescription.from_string(self.font_string)
        font_desc.set_size(max(self.get_font_size() / 1.1, 6 * Pango.SCALE))
        self.set_font_string(font_desc.to_string())

    def reset_zoom(self):
        font_desc = Pango.FontDescription.from_string(self.get_normal_font_string())
        self.set_font_string(font_desc.to_string())

    def propagate_font_setting(self):
        font_size = self.get_font_size() / Pango.SCALE
        font_family = self.get_font_family()
        self.main_window.css_provider_font_size.load_from_data(('''
textview { font-size: ''' + str(font_size) + '''pt; font-family: ''' + font_family + '''; }
box.autocomplete list row { font-size: ''' + str(font_size) + '''pt; }
box.autocomplete list row label { font-family: ''' + font_family + '''; }
''').encode('utf-8'))

    def get_font_desc(self):
        return Pango.FontDescription.from_string(self.font_string)

    def get_font_size(self):
        font_desc = Pango.FontDescription.from_string(self.font_string)
        return font_desc.get_size()

    def get_font_family(self):
        font_desc = Pango.FontDescription.from_string(self.font_string)
        return font_desc.get_family()

    def get_font_size_in_points(self):
        return self.get_font_size() / Pango.SCALE

    def get_normal_font_string(self):
        if self.settings.get_value('preferences', 'use_system_font'):
            return self.system_font
        else:
            return self.settings.get_value('preferences', 'font_string')

    def get_normal_font_size(self):
        font_desc = Pango.FontDescription.from_string(self.get_normal_font_string())
        return font_desc.get_size()

    def get_normal_font_size_in_points(self):
        return self.get_normal_font_size() / Pango.SCALE



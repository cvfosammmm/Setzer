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
gi.require_version('GtkSource', '4')
from gi.repository import Gdk
from gi.repository import GtkSource


class ColorManager(object):

    def __init__(self, main_window, settings, source_style_scheme_manager):
        self.main_window = main_window
        self.settings = settings

        self.style_context = main_window.get_style_context()
        self.source_style_scheme_manager = source_style_scheme_manager
        self.source_style_scheme = None
        self.syntax_scheme_name = None
        self.main_window.connect('style-updated', self.on_style_updated)

        self.string_cache = dict()
        self.rgba_cache = dict()
        self.mix_cache = dict()

    def on_style_updated(self, a, b=None):
        self.mix_cache = dict()

    def update_syntax_scheme(self):
        if self.settings.get_value('preferences', 'prefer_dark_mode'):
            name = self.settings.get_value('preferences', 'syntax_scheme_dark_mode')
        else:
            name = self.settings.get_value('preferences', 'syntax_scheme')
        if name == self.syntax_scheme_name: return

        self.syntax_scheme_name = name
        self.source_style_scheme = self.source_style_scheme_manager.get_scheme(name)

    def get_theme_color(self, name):
        return self.style_context.lookup_color(name)[1]

    def get_theme_color_mix(self, name1, name2, ratio):
        index = name1 + name2 + str(ratio)
        try:
            return self.mix_cache[index]
        except KeyError:
            color1 = self.get_theme_color(name1)
            color2 = self.get_theme_color(name2)
            mix_color = Gdk.RGBA(0, 0, 0, 0)
            mix_color.red = color1.red * ratio + color2.red * (1 - ratio)
            mix_color.green = color1.green * ratio + color2.green * (1 - ratio)
            mix_color.blue = color1.blue * ratio + color2.blue * (1 - ratio)
            mix_color.alpha = color1.alpha * ratio + color2.alpha * (1 - ratio)
            self.mix_cache[index] = mix_color
        return self.mix_cache[index]

    def get_syntax_scheme_color(self, style_id, property_name):
        self.update_syntax_scheme()
        style = self.source_style_scheme.get_style(style_id)

        if style == None: return None
        return style.get_property(property_name)

    def get_rgba(self, red, green, blue, alpha):
        index = int(red * 1000000000000) + int(green * 1000000000) + int(blue * 1000000) + int(alpha * 1000)
        try:
            return self.rgba_cache[index]
        except KeyError:
            self.rgba_cache[index] = Gdk.RGBA(red, green, blue, alpha)
        return self.rgba_cache[index]

    def get_rgba_from_string(self, color_string):
        if color_string not in self.string_cache:
            self.string_cache[color_string] = Gdk.RGBA(0, 0, 0, 0)
            self.string_cache[color_string].parse(color_string)
        return self.string_cache[color_string]



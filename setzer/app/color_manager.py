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
from gi.repository import Gdk


class ColorManager(object):

    def __init__(self, main_window):
        self.main_window = main_window
        self.style_context = main_window.get_style_context()
        self.main_window.connect('style-updated', self.on_style_updated)

        self.string_cache = dict()
        self.rgba_cache = dict()
        self.mix_cache = dict()

    def on_style_updated(self, a, b=None):
        self.mix_cache = dict()

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



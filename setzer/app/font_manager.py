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
from gi.repository import Pango
from gi.repository import Gtk


class FontManager(object):

    main_window = None
    text_view = None
    font_string = None

    def init(main_window):
        FontManager.main_window = main_window

        FontManager.text_view = Gtk.TextView()
        FontManager.text_view.set_monospace(True)
        FontManager.font_string = FontManager.text_view.get_pango_context().get_font_description().to_string()

    def get_line_height():
        char_width, line_height = FontManager.get_char_dimensions()
        return line_height

    def get_char_width(char='A'):
        char_width, line_height = FontManager.get_char_dimensions(char)
        return char_width

    def get_char_dimensions(char='A'):
        context = FontManager.text_view.get_pango_context()
        font_desc = Pango.FontDescription.from_string(FontManager.font_string)
        layout = Pango.Layout.new(context)
        layout.set_text(char, -1)
        layout.set_font_description(font_desc)
        return layout.get_pixel_size()

    def get_font_desc():
        return Pango.FontDescription.from_string(FontManager.font_string)



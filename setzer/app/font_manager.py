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
    default_font_string = None
    font_string = None

    def init(main_window):
        FontManager.main_window = main_window

        FontManager.default_font_string = 'monospace 11'
        FontManager.font_string = 'monospace 11'

    def propagate_font_setting():
        font_string = FontManager.font_string

        font_desc = Pango.FontDescription.from_string(font_string)
        font_size = font_desc.get_size() / Pango.SCALE
        font_family = font_desc.get_family()

        FontManager.main_window.css_provider_font_size.load_from_data(('textview { font-size: ' + str(font_size) + 'pt; font-family: ' + font_family + '; }\nbox.autocomplete list row { font-size: ' + str(font_size) + 'pt; }\nbox.autocomplete list row label { font-family: ' + font_family + '; }').encode('utf-8'))

    def get_char_width(text_view):
        context = text_view.get_pango_context()
        layout = Pango.Layout.new(context)
        layout.set_text('A', -1)
        char_width, line_height_1 = layout.get_pixel_size()
        return char_width

    def get_line_height(text_view):
        context = text_view.get_pango_context()
        layout = Pango.Layout.new(context)
        layout.set_text('A', -1)
        char_width, line_height_1 = layout.get_pixel_size()
        layout.set_text('A\nA', -1)
        char_width, line_height_2 = layout.get_pixel_size()
        return line_height_2 - line_height_1

    def get_font_desc():
        return Pango.FontDescription.from_string(FontManager.font_string)

    def get_system_font():
        return FontManager.default_font_string



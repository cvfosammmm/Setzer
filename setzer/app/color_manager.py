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


class ColorManager():

    main_window = None

    def init(main_window):
        ColorManager.main_window = main_window

    def get_ui_color(name):
        rgba = ColorManager.main_window.get_style_context().lookup_color(name)[1]
        return rgba

    def get_ui_color_string(name):
        color_rgba = ColorManager.get_ui_color(name)
        color_string = '#'
        color_string += format(int(color_rgba.red * 255), '02x')
        color_string += format(int(color_rgba.green * 255), '02x')
        color_string += format(int(color_rgba.blue * 255), '02x')
        return color_string

    def get_ui_color_string_with_alpha(name):
        color_rgba = ColorManager.get_ui_color(name)
        color_string = '#'
        color_string += format(int(color_rgba.red * 255), '02x')
        color_string += format(int(color_rgba.green * 255), '02x')
        color_string += format(int(color_rgba.blue * 255), '02x')
        color_string += format(int(color_rgba.alpha * 255), '02x')
        return color_string



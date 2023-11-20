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

from setzer.popovers.helpers.popover_menu_builder import MenuBuilder
from setzer.popovers.helpers.popover import Popover


class PreviewZoomLevelView(Popover):

    def __init__(self, popover_manager):
        Popover.__init__(self, popover_manager)

        self.set_width(180)

        self.levels = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 4.0]

        self.button_fit_to_width = MenuBuilder.create_button(_('Fit to Width'))
        self.button_fit_to_text_width = MenuBuilder.create_button(_('Fit to Text Width'))
        self.button_fit_to_height = MenuBuilder.create_button(_('Fit to Height'))
        self.zoom_level_buttons = dict()
        for level in self.levels:
            self.zoom_level_buttons[level] = MenuBuilder.create_button('{0:.0f}%'.format(level * 100))

        self.add_closing_button(self.button_fit_to_width)
        self.add_closing_button(self.button_fit_to_text_width)
        self.add_closing_button(self.button_fit_to_height)
        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
        for level in self.levels:
            self.add_closing_button(self.zoom_level_buttons[level])



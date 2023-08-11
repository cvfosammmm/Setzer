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

from setzer.helpers.observable import Observable


class PreviewZoomManager(Observable):

    def __init__(self, preview, view):
        Observable.__init__(self)
        self.preview = preview
        self.view = view

        self.zoom_level_fit_to_width = None
        self.zoom_level_fit_to_text_width = None
        self.zoom_level_fit_to_height = None
        self.zoom_level = None
        self.zoom_set = False

    def update_dynamic_zoom_levels(self):
        if self.preview.layout == None: return
        if self.view.get_allocated_width() < 300: return

        old_level = self.zoom_level_fit_to_width

        self.update_fit_to_width()
        self.update_fit_to_text_width()
        self.update_fit_to_height()

        if self.zoom_level == old_level and self.zoom_level_fit_to_width != old_level:
            self.set_zoom_fit_to_width_auto_offset()

        if not self.zoom_set:
            self.zoom_set = True
            self.set_zoom_fit_to_width()

    def update_fit_to_width(self):
        self.zoom_level_fit_to_width = self.view.get_allocated_width() / (self.preview.page_width * self.preview.layout.hidpi_factor)

    def update_fit_to_text_width(self):
        self.zoom_level_fit_to_text_width = self.zoom_level_fit_to_width * (self.preview.page_width / (self.preview.page_width - 2 * self.preview.vertical_margin))

    def update_fit_to_height(self):
        self.zoom_level_fit_to_height = (self.view.stack.get_allocated_height() + self.preview.layout.border_width) / (self.preview.page_height * self.preview.layout.hidpi_factor)

    def set_zoom_fit_to_height(self):
        self.set_zoom_level_auto_offset(self.zoom_level_fit_to_height)

    def set_zoom_fit_to_text_width(self):
        self.set_zoom_level_auto_offset(self.zoom_level_fit_to_text_width)

    def set_zoom_fit_to_width(self):
        if self.zoom_level_fit_to_width != None:
            self.set_zoom_level(self.zoom_level_fit_to_width)
        else:
            self.set_zoom_level(1.0)
            self.zoom_set = False

    def set_zoom_fit_to_width_auto_offset(self):
        if self.zoom_level_fit_to_width != None:
            zoom_level = self.zoom_level_fit_to_width
        else:
            zoom_level = 1.0
            self.zoom_set = False
        self.set_zoom_level_auto_offset(zoom_level)

    def zoom_in(self):
        try:
            zoom_level = min([level for level in self.get_list_of_zoom_levels() if level > self.zoom_level])
        except ValueError:
            zoom_level = max(self.get_list_of_zoom_levels())
        self.set_zoom_level_auto_offset(zoom_level)

    def zoom_out(self):
        try:
            zoom_level = max([level for level in self.get_list_of_zoom_levels() if level < self.zoom_level])
        except ValueError:
            zoom_level = min(self.zoom_levels)
        self.set_zoom_level_auto_offset(zoom_level)

    def get_list_of_zoom_levels(self):
        zoom_levels = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 4.0]
        if self.zoom_level_fit_to_width != None:
            zoom_levels.append(self.zoom_level_fit_to_width)
        if self.zoom_level_fit_to_text_width != None:
            zoom_levels.append(self.zoom_level_fit_to_text_width)
        if self.zoom_level_fit_to_height != None:
            zoom_levels.append(self.zoom_level_fit_to_height)
        return zoom_levels

    def set_zoom_level_auto_offset(self, zoom_level):
        layout = self.preview.layout
        factor = zoom_level / self.zoom_level

        x = factor * self.view.content.scrolling_offset_x + (factor - 1) * self.view.content.width / 2
        prev_pages = self.view.content.scrolling_offset_y // (layout.page_height + layout.page_gap)
        y = (1 - factor) * prev_pages * layout.page_gap + factor * self.view.content.scrolling_offset_y

        self.set_zoom_level(zoom_level)
        self.preview.scroll_to_position(x, y)

    def set_zoom_level(self, level):
        if level == None: return
        if level == self.zoom_level: return
        if level > 4.0: level = 4.0
        if level < 0.25: level = 0.25

        self.zoom_level = level

        self.preview.layout = self.preview.layouter.create_layout()
        self.preview.add_change_code('layout_changed')
        self.update_dynamic_zoom_levels()

        self.zoom_set = True
        self.add_change_code('zoom_level_changed')

    def get_zoom_level(self):
        return self.zoom_level



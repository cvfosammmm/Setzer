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

from setzer.helpers.observable import Observable


class PreviewLayouter(Observable):

    def __init__(self, preview, view):
        Observable.__init__(self)
        self.preview = preview
        self.view = view

        self.hidpi_factor = self.view.get_scale_factor()
        self.page_width = None
        self.page_height = None
        self.page_gap = None
        self.border_width = None
        self.canvas_width = None
        self.canvas_height = None
        self.scale_factor = None
        self.visible_synctex_rectangles = dict()
        self.has_layout = False

    def update_layout(self):
        if self.preview.zoom_manager.get_zoom_level() == None or not self.preview.poppler_document != None:
            self.has_layout = False
            self.page_width = None
            self.page_height = None
            self.page_gap = None
            self.border_width = None
            self.canvas_width = None
            self.canvas_height = None
            self.scale_factor = None
        else:
            self.scale_factor = self.preview.zoom_manager.get_zoom_level() * self.hidpi_factor
            self.page_width = int(round(self.scale_factor * self.preview.page_width))
            self.page_height = int(self.scale_factor * self.preview.page_height)
            self.page_gap = int(self.hidpi_factor * 10)
            self.border_width = 1
            self.canvas_width = self.page_width + 2 * self.get_horizontal_margin()
            self.canvas_height = self.preview.poppler_document.get_n_pages() * (self.page_height + self.page_gap) - self.page_gap
            self.has_layout = True
            self.update_synctex_rectangles()
        self.add_change_code('layout_changed')

    def update_synctex_rectangles(self):
        self.visible_synctex_rectangles = dict()
        for rectangle in self.preview.visible_synctex_rectangles:
            new_rectangle = dict()
            new_rectangle['page'] = rectangle['page']
            new_rectangle['x'] = rectangle['h'] * self.scale_factor
            new_rectangle['y'] = (rectangle['v'] - rectangle['height']) * self.scale_factor
            new_rectangle['width'] = rectangle['width'] * self.scale_factor
            new_rectangle['height'] = rectangle['height'] * self.scale_factor
            try:
                self.visible_synctex_rectangles[rectangle['page'] - 1].append(new_rectangle)
            except KeyError:
                self.visible_synctex_rectangles[rectangle['page'] - 1] = [new_rectangle]

    def get_horizontal_margin(self):
        return int(max((self.view.get_allocated_width() - self.page_width) / 2, 0))

    def get_page_number_and_offsets_by_document_offsets(self, x, y):
        if self.has_layout:
            if y % (self.page_height + self.page_gap) > self.page_height: return None
            if x < self.get_horizontal_margin() or x > (self.get_horizontal_margin() + self.page_width): return None

            page_number = int(y // (self.page_height + self.page_gap))
            y_offset = y % (self.page_height + self.page_gap) / self.scale_factor
            x_offset = (x - self.get_horizontal_margin()) / self.scale_factor

            return (page_number, x_offset, y_offset)
        return None

    def get_current_page(self):
        offset = self.view.scrolled_window.get_vadjustment().get_value()
        return int(1 + offset // (self.page_height + self.page_gap))



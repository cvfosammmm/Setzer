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


class PreviewLayouter(Observable):

    def __init__(self, preview, view):
        Observable.__init__(self)
        self.preview = preview
        self.view = view

    def create_layout(self):
        if self.preview.zoom_manager.get_zoom_level() != None and self.preview.poppler_document != None:
            window_width = self.view.get_allocated_width()

            layout = PreviewLayout(self.view.get_scale_factor())
            layout.scale_factor = self.preview.zoom_manager.get_zoom_level() * layout.hidpi_factor
            layout.page_width = layout.scale_factor * self.preview.page_width
            layout.page_height = layout.scale_factor * self.preview.page_height
            layout.page_gap = layout.hidpi_factor * 10
            layout.border_width = 1
            layout.canvas_width = layout.page_width + 2 * layout.get_horizontal_margin(window_width)
            layout.canvas_height = self.preview.poppler_document.get_n_pages() * (layout.page_height + layout.page_gap) - layout.page_gap
            self.update_synctex_rectangles(layout)
            return layout
        else:
            return None

    def update_synctex_rectangles(self, layout):
        layout.visible_synctex_rectangles = dict()
        for rectangle in self.preview.visible_synctex_rectangles:
            new_rectangle = dict()
            new_rectangle['page'] = rectangle['page']
            new_rectangle['x'] = rectangle['h'] * layout.scale_factor
            new_rectangle['y'] = (rectangle['v'] - rectangle['height']) * layout.scale_factor
            new_rectangle['width'] = rectangle['width'] * layout.scale_factor
            new_rectangle['height'] = rectangle['height'] * layout.scale_factor
            try:
                layout.visible_synctex_rectangles[rectangle['page'] - 1].append(new_rectangle)
            except KeyError:
                layout.visible_synctex_rectangles[rectangle['page'] - 1] = [new_rectangle]


class PreviewLayout(object):

    def __init__(self, hidpi_factor):
        self.hidpi_factor = hidpi_factor
        self.page_width = None
        self.page_height = None
        self.page_gap = None
        self.border_width = None
        self.canvas_width = None
        self.canvas_height = None
        self.scale_factor = None
        self.visible_synctex_rectangles = dict()

    def get_horizontal_margin(self, window_width):
        return int(max((window_width - self.page_width) / 2, 0))

    def get_page_number_and_offsets_by_document_offsets(self, x, y, window_width):
        if y % (self.page_height + self.page_gap) > self.page_height: return None
        if x < self.get_horizontal_margin(window_width) or x > (self.get_horizontal_margin(window_width) + self.page_width): return None

        page_number = int(y // (self.page_height + self.page_gap))
        y_offset = y % (self.page_height + self.page_gap) / self.scale_factor
        x_offset = (x - self.get_horizontal_margin(window_width)) / self.scale_factor

        return (page_number, x_offset, y_offset)

    def get_page_by_offset(self, offset):
        return int(1 + offset // (self.page_height + self.page_gap))



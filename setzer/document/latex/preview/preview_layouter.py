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

from setzer.helpers.observable import Observable


class PreviewLayouter(Observable):

    def __init__(self, preview, view):
        Observable.__init__(self)
        self.preview = preview
        self.view = view

        self.hidpi_factor = self.view.get_scale_factor()
        self.ppp = self.get_ppp() # pixels per point
        self.vertical_margin_points = 0
        self.horizontal_margin_points = 0
        self.vertical_margin = None
        self.horizontal_margin = None
        self.page_width = None
        self.page_height = None
        self.page_gap_points = 5
        self.page_gap = None
        self.border_width = None
        self.canvas_width = None
        self.canvas_height = None
        self.scale_factor = None
        self.current_page = None
        self.visible_synctex_rectangles = dict()
        self.has_layout = False

        self.preview.connect('pdf_changed', self.on_pdf_or_zoom_level_changed)
        self.preview.connect('zoom_level_changed', self.on_pdf_or_zoom_level_changed)
        self.preview.connect('position_changed', self.on_position_changed)

        if self.preview.pdf_filename != None:
            self.update_layout()

    def on_pdf_or_zoom_level_changed(self, preview):
        if self.preview.pdf_loaded:
            self.update_layout()
        else:
            self.has_layout = False
            self.vertical_margin = None
            self.horizontal_margin = None
            self.page_width = None
            self.page_height = None
            self.page_gap = None
            self.border_width = None
            self.canvas_width = None
            self.canvas_height = None
            self.scale_factor = None
            self.add_change_code('layout_changed')
        self.compute_current_page()

    def on_position_changed(self, preview):
        self.compute_current_page()

    def update_layout(self):
        if self.preview.zoom_level == None: return
        if not self.preview.pdf_loaded: return

        self.vertical_margin = int(self.ppp * self.vertical_margin_points)
        self.page_width = int(round(self.preview.zoom_level * self.ppp * self.preview.page_width))
        self.horizontal_margin = int(self.ppp * self.horizontal_margin_points)
        self.horizontal_margin = int(max((self.view.get_allocated_width() - self.page_width) / 2, self.horizontal_margin))
        self.page_height = int(self.preview.zoom_level * self.ppp * self.preview.page_height)
        self.page_gap = int(self.ppp * self.page_gap_points)
        self.border_width = 1
        self.scale_factor = self.preview.zoom_level * self.ppp
        self.canvas_width = self.page_width + 2 * self.horizontal_margin
        self.canvas_height = self.preview.number_of_pages * (self.page_height + self.page_gap) - self.page_gap + 2 * self.vertical_margin
        self.has_layout = True
        self.compute_current_page()
        self.update_zoom_levels()
        self.update_synctex_rectangles()
        self.add_change_code('layout_changed')

    def update_synctex_rectangles(self):
        if self.has_layout:
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

    def update_zoom_levels(self):
        if not self.has_layout: return

        self.horizontal_margin = int(self.ppp * self.horizontal_margin_points)
        self.horizontal_margin = int(max((self.view.get_allocated_width() - self.page_width) / 2, self.horizontal_margin))

        if self.view.get_allocated_width() < 300: return
        old_level = self.preview.zoom_level_fit_to_width

        self.preview.update_dynamic_zoom_levels()

        if old_level != None and self.preview.zoom_level == old_level:
            self.preview.set_zoom_fit_to_width()
        elif self.preview.zoom_level != None and self.preview.zoom_level_fit_to_text_width != None and self.preview.zoom_level_fit_to_text_width == self.preview.zoom_level:
            self.preview.set_zoom_fit_to_text_width()
        elif self.preview.zoom_level != None and self.preview.zoom_level_fit_to_height != None and self.preview.zoom_level_fit_to_height == self.preview.zoom_level:
            self.preview.set_zoom_fit_to_height()
        elif self.preview.first_show:
            self.preview.first_show = False

    def get_ppp(self):
        monitor = Gdk.Display.get_default().get_monitor_at_point(1, 1)
        width_inch = monitor.get_width_mm() / 25.4
        width_pixels = monitor.get_geometry().width
        if width_inch > 0 and width_pixels > 0:
            ppi = int(width_pixels / width_inch)
        else:
            ppi = 96

        return self.hidpi_factor * ppi / 72

    def compute_current_page(self):
        if self.has_layout and self.preview.presenter.scrolling_queue.empty():
            offset = self.view.scrolled_window.get_vadjustment().get_value()
            self.current_page = int(1 + offset // (self.page_height + self.page_gap))

    def get_page_number_and_offsets_by_document_offsets(self, x, y):
        if self.has_layout:
            if y % (self.page_height + self.page_gap) > self.page_height: return None
            if x < self.horizontal_margin or x > (self.horizontal_margin + self.page_width): return None

            page_number = int(y // (self.page_height + self.page_gap))
            y_offset = y % (self.page_height + self.page_gap) / self.scale_factor
            x_offset = (x - self.horizontal_margin) / self.scale_factor

            return (page_number, x_offset, y_offset)
        return None

    def get_current_page(self):
        return self.current_page



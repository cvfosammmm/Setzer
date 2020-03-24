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

        self.ppp = self.get_ppp() # pixels per point
        self.vertical_margin_points = 8
        self.horizontal_margin_points = 8
        self.vertical_margin = None
        self.horizontal_margin = None
        self.page_width = None
        self.page_height = None
        self.page_gap_points = 9
        self.page_gap = None
        self.border_width = None
        self.scale_factor = None
        self.visible_pages = list()
        self.current_page = None
        self.has_layout = False

        self.preview.register_observer(self)

        if self.preview.pdf_filename != None:
            self.update_layout()

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code in ['pdf_changed', 'zoom_level_changed']:
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
                self.scale_factor = None
                self.visible_pages = list()
                self.current_page = None
                self.pages = None
                self.add_change_code('layout_changed')
            self.compute_visible_pages()

        if change_code == 'position_changed':
            self.compute_visible_pages()

    def update_layout(self):
        if self.preview.zoom_level == None: return
        if not self.preview.pdf_loaded: return

        self.vertical_margin = int(self.ppp * self.vertical_margin_points)
        self.horizontal_margin = int(self.ppp * self.horizontal_margin_points)
        self.page_width = int(round(self.preview.zoom_level * self.ppp * self.preview.page_width))
        self.page_height = int(self.preview.zoom_level * self.ppp * self.preview.page_height)
        self.page_gap = int(self.ppp * self.page_gap_points)
        self.border_width = 1
        self.scale_factor = self.preview.zoom_level * self.ppp
        self.pages = list()
        for n in range(0, self.preview.number_of_pages):
            page = dict()
            page['x'] = self.horizontal_margin
            page['y'] = n * (self.page_height + self.page_gap) + self.vertical_margin
            page['width'] = self.page_width
            page['height'] = self.page_height
            self.pages.append(page)
        self.has_layout = True
        self.update_fit_to_width()
        self.add_change_code('layout_changed')

    def update_fit_to_width(self):
        if self.view.get_allocated_width() < 300: return
        old_level = self.preview.zoom_level_fit_to_width
        try:
            level = (self.view.get_allocated_width() - 2 * int(self.vertical_margin_points * self.ppp)) / (self.preview.page_width * self.ppp)
        except TypeError:
            pass
        else:
            self.preview.update_fit_to_width_zoom_level(level)
        if old_level != None and self.preview.zoom_level == old_level:
            self.preview.set_zoom_fit_to_width()
        elif self.preview.first_show:
            self.preview.first_show = False
            self.preview.set_zoom_fit_to_width()

    def get_ppp(self):        
        monitor = Gdk.Display.get_default().get_monitor_at_point(1, 1)
        width_inch = monitor.get_width_mm() / 25.4
        width_pixels = monitor.get_geometry().width
        if width_inch > 0 and width_pixels > 0:
            ppi = int(width_pixels / width_inch)
        else:
            ppi = 96
        hidpi_factor = self.view.get_scale_factor()

        return hidpi_factor * ppi / 72

    def compute_visible_pages(self):
        if self.has_layout:
            current_page = 0
            offset = self.view.scrolled_window.get_vadjustment().get_value()
            size_iter = self.vertical_margin
            while size_iter <= offset:
                size_iter += self.page_height + self.page_gap
                current_page += 1
            self.current_page = max(current_page, 1)

            screen_height = self.view.scrolled_window.get_allocated_height()
            yoffset = (self.preview.yoffset / self.preview.page_height) * (self.page_height + self.page_gap)
            first_page = max(int((yoffset - self.vertical_margin) / (self.page_height + self.page_gap)) - 1, 0)
            last_page = min(int(first_page + screen_height / self.page_height + 2), self.preview.number_of_pages - 1)
            self.visible_pages = list(range(first_page, last_page + 1))
            self.add_change_code('layout_changed')

    def get_visible_pages(self):
        return self.visible_pages



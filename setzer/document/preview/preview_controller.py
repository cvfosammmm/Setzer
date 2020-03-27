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


class PreviewController(object):

    def __init__(self, preview, layouter, view):
        self.preview = preview
        self.layouter = layouter
        self.view = view

        self.view.zoom_widget.zoom_in_button.connect('clicked', self.on_zoom_button_clicked, 'in')
        self.view.zoom_widget.zoom_out_button.connect('clicked', self.on_zoom_button_clicked, 'out')
        self.view.connect('size-allocate', self.on_size_allocate)
        self.view.scrolled_window.get_hadjustment().connect('value-changed', self.on_hadjustment_changed)
        self.view.scrolled_window.get_vadjustment().connect('value-changed', self.on_vadjustment_changed)

    def on_zoom_button_clicked(self, button, direction):
        if direction == 'in':
            self.preview.zoom_in()
        else:
            self.preview.zoom_out()

    def on_size_allocate(self, view=None, allocation=None):
        self.layouter.update_fit_to_width()

    def on_hadjustment_changed(self, adjustment):
        if self.layouter.has_layout:
            xoffset = max((adjustment.get_value() - self.layouter.horizontal_margin) / self.layouter.scale_factor, 0)
            self.preview.set_position_from_offsets(xoffset, None)
    
    def on_vadjustment_changed(self, adjustment):
        if self.layouter.has_layout:
            self.layouter.compute_visible_pages()
            yoffset = max(self.layouter.current_page - 1, 0) * self.preview.page_height
            yoffset += min(max(adjustment.get_value() - self.layouter.vertical_margin - max(self.layouter.current_page - 1, 0) * (self.layouter.page_height + self.layouter.page_gap), 0), self.layouter.page_height) / self.layouter.scale_factor
            self.preview.set_position_from_offsets(None, yoffset)
    


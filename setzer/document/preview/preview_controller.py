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


class PreviewController(object):

    def __init__(self, preview, layouter, view):
        self.preview = preview
        self.layouter = layouter
        self.view = view

        self.zoom_momentum = 0

        self.view.connect('size-allocate', self.on_size_allocate)
        self.view.scrolled_window.get_hadjustment().connect('value-changed', self.on_hadjustment_changed)
        self.view.scrolled_window.get_vadjustment().connect('value-changed', self.on_vadjustment_changed)
        self.view.scrolled_window.connect('scroll-event', self.on_scroll)
        self.view.drawing_area.connect('button-press-event', self.on_button_press)

        def zoom_in(menu_item): self.preview.zoom_in()
        self.view.menu_item_zoom_in.connect('activate', zoom_in)

        def zoom_out(menu_item): self.preview.zoom_out()
        self.view.menu_item_zoom_out.connect('activate', zoom_out)

        def zoom_fit_to_width(menu_item): self.preview.set_zoom_fit_to_width_auto_offset()
        self.view.menu_item_zoom_fit_to_width.connect('activate', zoom_fit_to_width)

        def zoom_fit_to_text_width(menu_item): self.preview.set_zoom_fit_to_text_width()
        self.view.menu_item_zoom_fit_to_text_width.connect('activate', zoom_fit_to_text_width)

        def zoom_fit_to_height(menu_item): self.preview.set_zoom_fit_to_height()
        self.view.menu_item_zoom_fit_to_height.connect('activate', zoom_fit_to_height)

    def on_scroll(self, widget, event):
        if event.state == Gdk.ModifierType.CONTROL_MASK:
            direction = False
            if event.delta_y - event.delta_x < 0:
                direction = 'in'
            elif event.delta_y - event.delta_x > 0:
                direction = 'out'
            if direction != False:
                self.zoom_momentum += event.delta_y - event.delta_x
                if(self.preview.presenter.scrolling_queue.empty()):
                    zoom_level = min(max(self.preview.zoom_level * (1 - 0.1 * self.zoom_momentum), 0.25), 4)
                    xoffset = (-event.x + event.x * zoom_level / self.preview.zoom_level) / (zoom_level * self.layouter.ppp)
                    yoffset = (-event.y + event.y * zoom_level / self.preview.zoom_level) / (zoom_level * self.layouter.ppp)
                    self.preview.set_zoom_level(zoom_level, xoffset, yoffset)
                    self.zoom_momentum = 0
            return True
        return False
    
    def on_size_allocate(self, view=None, allocation=None):
        self.layouter.update_zoom_levels()
        self.view.drawing_area.queue_draw()

    def on_hadjustment_changed(self, adjustment):
        if self.layouter.has_layout:
            xoffset = max((adjustment.get_value() - self.layouter.horizontal_margin) / self.layouter.scale_factor, 0)
            self.preview.set_position_from_offsets(xoffset, None)
    
    def on_vadjustment_changed(self, adjustment):
        if self.layouter.has_layout:
            self.layouter.compute_current_page()
            yoffset = max(self.layouter.current_page - 1, 0) * self.preview.page_height
            yoffset += min(max(adjustment.get_value() - self.layouter.vertical_margin - max(self.layouter.current_page - 1, 0) * (self.layouter.page_height + self.layouter.page_gap), 0), self.layouter.page_height) / self.layouter.scale_factor
            self.preview.set_position_from_offsets(None, yoffset)
    
    def on_button_press(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.view.context_menu.show_all()
            self.view.context_menu.popup_at_pointer()
    


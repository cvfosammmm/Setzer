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
gi.require_version('Poppler', '0.18')
from gi.repository import Poppler
from gi.repository import GObject
import cairo

import os.path
import math
import queue


class PreviewPresenter(object):

    def __init__(self, preview, layouter, page_renderer, view):
        self.preview = preview
        self.layouter = layouter
        self.page_renderer = page_renderer
        self.view = view

        self.view.drawing_area.connect('draw', self.draw)
        self.scrolling_queue = queue.Queue()
        self.view.drawing_area.connect('size-allocate', self.scrolling_loop)
        GObject.timeout_add(50, self.scrolling_loop)
        self.preview.register_observer(self)
        self.layouter.register_observer(self)
        self.page_renderer.register_observer(self)

        self.show_blank_slate()
        self.update_number_of_pages()
        self.update_current_page()

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'pdf_changed':
            if self.preview.pdf_loaded:
                self.show_pdf()
            else:
                self.show_blank_slate()
            self.update_number_of_pages()

        if change_code == 'layout_changed':
            self.set_canvas_size()
            if self.scrolling_queue.empty():
                self.update_current_page()
            self.update_zoom_level()

        if change_code == 'rendered_pages_changed':
            self.view.drawing_area.queue_draw()

        if change_code == 'position_changed':
            self.update_current_page()

    def show_blank_slate(self):
        self.view.stack.set_visible_child_name('blank_slate')
        self.view.blank_slate.show_all()
        self.view.zoom_widget.hide()

    def show_pdf(self):
        self.view.stack.set_visible_child_name('pdf')
        self.view.scrolled_window.show_all()
        self.view.zoom_widget.show_all()

    def update_number_of_pages(self):
        if self.preview.pdf_filename != None:
            self.view.paging_widget.label_number_of_pages.set_text(str(self.preview.number_of_pages))
        else:
            self.view.paging_widget.label_number_of_pages.set_text("0")

    def update_current_page(self):
        if self.layouter.has_layout:
            self.view.paging_widget.label_current_page.set_text(str(self.layouter.current_page))
        else:
            self.view.paging_widget.label_current_page.set_text("0")

    def update_zoom_level(self):
        if self.layouter.has_layout and self.preview.zoom_level != None:
            self.view.zoom_widget.label.set_text('{0:.1f}%'.format(self.preview.zoom_level * 100))
    
    def set_canvas_size(self):
        if self.layouter.has_layout:
            self.view.drawing_area.set_size_request(self.layouter.canvas_width, self.layouter.canvas_height)

    def scroll_to_position(self, position):
        if self.layouter.has_layout:
            self.scrolling_queue.put(position)

    def scrolling_loop(self, widget=None, allocation=None):
        if int(self.view.drawing_area.get_allocated_height()) == int(self.layouter.canvas_height):
            while self.scrolling_queue.empty() == False:
                try: todo = self.scrolling_queue.get(block=False)
                except queue.Empty: pass
                else:
                    if(self.scrolling_queue.empty()):
                        self.scroll_now(todo)
        return True

    def scroll_now(self, position):
        yoffset = max((self.layouter.page_gap + self.layouter.page_height) * (position['page'] - 1) + self.layouter.vertical_margin + position['y'] * self.layouter.scale_factor, 0)
        xoffset = self.layouter.vertical_margin + position['x'] * self.layouter.scale_factor
        self.view.scrolled_window.get_hadjustment().set_value(xoffset)
        self.view.scrolled_window.get_vadjustment().set_value(yoffset)

    #@helpers.timer
    def draw(self, drawing_area, cairo_context, data = None):
        if self.layouter.has_layout:
            ctx = cairo_context
            bg_color = self.view.get_style_context().lookup_color('theme_bg_color')[1]
            border_color = self.view.get_style_context().lookup_color('borders')[1]

            ctx.rectangle(0, 0, drawing_area.get_allocated_width(), drawing_area.get_allocated_height())
            ctx.set_source_rgba(bg_color.red, bg_color.green, bg_color.blue, bg_color.alpha)
            ctx.fill()

            ctx.transform(cairo.Matrix(1, 0, 0, 1, self.layouter.horizontal_margin, self.layouter.vertical_margin))
            for page_number in range(0, self.preview.number_of_pages):
                ctx.set_source_rgba(border_color.red, border_color.green, border_color.blue, border_color.alpha)
                ctx.rectangle(- self.layouter.border_width, - self.layouter.border_width, self.layouter.page_width + 2 * self.layouter.border_width, self.layouter.page_height + 2 * self.layouter.border_width)
                ctx.fill()
                ctx.set_source_rgba(1, 1, 1, 1)
                ctx.rectangle(0, 0, self.layouter.page_width, self.layouter.page_height)
                ctx.fill()

                if page_number in self.page_renderer.rendered_pages:
                    rendered_page_data = self.page_renderer.rendered_pages[page_number]
                    surface = rendered_page_data[0]
                    page_width = rendered_page_data[1]
                    if isinstance(surface, cairo.ImageSurface):
                        if page_width == self.layouter.page_width:
                            ctx.set_source_surface(surface, 0, 0)
                            ctx.paint()
                        else:
                            matrix = ctx.get_matrix()
                            factor = self.layouter.page_width / page_width
                            ctx.scale(factor, factor)
                            ctx.set_source_surface(surface, 0, 0)
                            ctx.paint()
                            ctx.set_matrix(matrix)
                ctx.transform(cairo.Matrix(1, 0, 0, 1, 0, self.layouter.page_height + self.layouter.page_gap))



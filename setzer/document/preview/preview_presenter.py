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
from gi.repository import GObject
import cairo

import os.path
import math
import time
import queue

from setzer.app.service_locator import ServiceLocator
from setzer.helpers.timer import timer


class PreviewPresenter(object):

    def __init__(self, preview, layouter, page_renderer, view):
        self.preview = preview
        self.layouter = layouter
        self.page_renderer = page_renderer
        self.view = view

        self.highlight_duration = 1.5

        self.color_manager = ServiceLocator.get_color_manager()

        self.view.drawing_area.connect('draw', self.draw)
        self.scrolling_queue = queue.Queue()
        self.view.drawing_area.connect('size-allocate', self.scrolling_loop)
        GObject.timeout_add(50, self.scrolling_loop)

        self.preview.connect('pdf_changed', self.on_pdf_changed)
        self.preview.connect('invert_pdf_changed', self.on_invert_pdf_changed)
        self.layouter.connect('layout_changed', self.on_layout_changed)
        self.page_renderer.connect('rendered_pages_changed', self.on_rendered_pages_changed)

        self.show_blank_slate()

    def on_pdf_changed(self, preview):
        if self.preview.pdf_loaded:
            self.show_pdf()
        else:
            self.show_blank_slate()

    def on_invert_pdf_changed(self, preview):
        self.view.drawing_area.queue_draw()

    def on_layout_changed(self, layouter):
        self.set_canvas_size()

    def on_rendered_pages_changed(self, page_renderer):
        self.view.drawing_area.queue_draw()

    def show_blank_slate(self):
        self.view.stack.set_visible_child_name('blank_slate')
        self.view.blank_slate.show_all()
        self.view.external_viewer_button.set_sensitive(False)
        self.view.external_viewer_button_revealer.set_reveal_child(False)

    def show_pdf(self):
        self.view.stack.set_visible_child_name('pdf')
        self.view.scrolled_window.show_all()
        self.view.external_viewer_button.set_sensitive(True)
        self.view.external_viewer_button_revealer.set_reveal_child(True)

    def set_canvas_size(self):
        if self.layouter.has_layout:
            self.view.drawing_area.set_size_request(self.layouter.canvas_width, self.layouter.canvas_height)

    def start_fade_loop(self):
        def draw():
            timer = (self.highlight_duration + 0.25 - time.time() + self.preview.visible_synctex_rectangles_time)
            if timer <= 0.4:
                self.view.drawing_area.queue_draw()
            return timer >= 0
        self.view.drawing_area.queue_draw()
        GObject.timeout_add(15, draw)

    def scroll_to_position(self, position):
        if self.layouter.has_layout:
            self.scrolling_queue.put(position)

    def scrolling_loop(self, widget=None, allocation=None):
        allocated_height = int(self.view.drawing_area.get_allocated_height())
        if self.layouter.has_layout and allocated_height == max(int(self.layouter.canvas_height), allocated_height):
            while self.scrolling_queue.empty() == False:
                todo = self.scrolling_queue.get(block=False)
                if self.scrolling_queue.empty():
                    self.scroll_now(todo)
                    self.preview.add_change_code('position_changed')
        return True

    def scroll_now(self, position):
        yoffset = max((self.layouter.page_gap + self.layouter.page_height) * (position['page'] - 1) + self.layouter.vertical_margin + position['y'] * self.layouter.scale_factor, 0)
        xoffset = self.layouter.horizontal_margin + position['x'] * self.layouter.scale_factor
        self.view.scrolled_window.get_hadjustment().set_value(xoffset)
        self.view.scrolled_window.get_vadjustment().set_value(yoffset)

    #@timer
    def draw(self, drawing_area, ctx, data = None):
        if self.layouter.has_layout:
            bg_color = self.color_manager.get_theme_color('theme_bg_color')
            border_color = self.color_manager.get_theme_color('borders')
            self.draw_background(ctx, drawing_area, bg_color)

            ctx.transform(cairo.Matrix(1, 0, 0, 1, self.layouter.horizontal_margin, self.layouter.vertical_margin))

            offset = self.view.scrolled_window.get_vadjustment().get_value()
            view_width = self.view.scrolled_window.get_allocated_width()
            view_height = self.view.scrolled_window.get_allocated_height()
            additional_height = ctx.get_target().get_height() - view_height
            additional_pages = additional_height // self.layouter.page_height + 2

            first_page = max(int(offset // self.layouter.page_height) - additional_pages, 0)
            last_page = min(int((offset + view_height) // self.layouter.page_height) + additional_pages, self.preview.number_of_pages)
            ctx.transform(cairo.Matrix(1, 0, 0, 1, 0, first_page * (self.layouter.page_height + self.layouter.page_gap)))

            for page_number in range(first_page, last_page):
                self.draw_page_background_and_outline(ctx, border_color)
                self.draw_rendered_page(ctx, page_number)
                self.draw_synctex_rectangles(ctx, page_number)

                ctx.transform(cairo.Matrix(1, 0, 0, 1, 0, self.layouter.page_height + self.layouter.page_gap))

    def draw_background(self, ctx, drawing_area, bg_color):
        ctx.rectangle(0, 0, drawing_area.get_allocated_width(), drawing_area.get_allocated_height())
        ctx.set_source_rgba(bg_color.red, bg_color.green, bg_color.blue, bg_color.alpha)
        ctx.fill()

    #@timer
    def draw_page_background_and_outline(self, ctx, border_color):
        ctx.set_source_rgba(border_color.red, border_color.green, border_color.blue, border_color.alpha)
        ctx.rectangle(- self.layouter.border_width, - self.layouter.border_width, self.layouter.page_width + 2 * self.layouter.border_width, self.layouter.page_height + 2 * self.layouter.border_width)
        ctx.fill()
        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.rectangle(0, 0, self.layouter.page_width, self.layouter.page_height)
        ctx.fill()

    def draw_rendered_page(self, ctx, page_number):
        if page_number in self.page_renderer.rendered_pages:
            rendered_page_data = self.page_renderer.rendered_pages[page_number]
            surface = rendered_page_data[0]
            page_width = rendered_page_data[1] * self.layouter.hidpi_factor
            if isinstance(surface, cairo.ImageSurface):
                if page_width == self.layouter.page_width:
                    ctx.set_source_surface(surface, 0, 0)
                    ctx.rectangle(0, 0, self.layouter.page_width, self.layouter.page_height)
                    ctx.fill()
                else:
                    matrix = ctx.get_matrix()
                    factor = self.layouter.page_width / page_width
                    ctx.scale(factor, factor)
                    ctx.set_source_surface(surface, 0, 0)
                    ctx.rectangle(0, 0, self.layouter.page_width, self.layouter.page_height)
                    ctx.fill()
                    ctx.set_matrix(matrix)
                if self.preview.invert_pdf:
                    ctx.set_operator(cairo.Operator.DIFFERENCE)
                    ctx.set_source_rgb(1, 1, 1)
                    ctx.rectangle(0, 0, self.layouter.page_width, self.layouter.page_height)
                    ctx.fill()
                    ctx.set_operator(cairo.Operator.OVER)

    def draw_synctex_rectangles(self, ctx, page_number):
        try:
            rectangles = self.layouter.visible_synctex_rectangles[page_number]
        except KeyError: pass
        else:
            time_factor = self.ease(min(self.highlight_duration + 0.25 - (time.time() - self.preview.visible_synctex_rectangles_time), 0.25) * 4)
            if time_factor < 0:
                self.preview.set_synctex_rectangles(list())
            else:
                ctx.set_source_rgba(0.976, 0.941, 0.420, 0.6 * time_factor)
                ctx.set_operator(cairo.Operator.MULTIPLY)
                for rectangle in rectangles:
                    ctx.rectangle(rectangle['x'], rectangle['y'], rectangle['width'], rectangle['height'])
                ctx.fill()
                ctx.set_operator(cairo.Operator.OVER)

    def ease(self, factor): return (factor - 1)**3 + 1



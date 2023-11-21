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
from gi.repository import GObject, Gdk
import cairo

import os.path
import math
import time

from setzer.app.color_manager import ColorManager
from setzer.helpers.timer import timer


class PreviewPresenter(object):

    def __init__(self, preview, page_renderer, view):
        self.preview = preview
        self.page_renderer = page_renderer
        self.view = view

        self.highlight_duration = 1.5
        self.count = 1

        self.view.drawing_area.set_draw_func(self.draw)

        self.preview.connect('pdf_changed', self.on_pdf_changed)
        self.preview.connect('layout_changed', self.on_layout_changed)
        self.page_renderer.connect('rendered_pages_changed', self.on_rendered_pages_changed)

        self.show_blank_slate()

    def on_pdf_changed(self, preview):
        if self.preview.poppler_document != None:
            self.show_pdf()
        else:
            self.show_blank_slate()

    def on_layout_changed(self, preview):
        if self.preview.layout != None:
            self.view.content.adjustment_x.set_upper(self.preview.layout.canvas_width)
            self.view.content.adjustment_y.set_upper(self.preview.layout.canvas_height)
            self.view.content.queue_draw()

    def on_rendered_pages_changed(self, page_renderer):
        self.view.drawing_area.queue_draw()

    def show_blank_slate(self):
        self.view.stack.set_visible_child_name('blank_slate')

    def show_pdf(self):
        self.view.stack.set_visible_child_name('pdf')
        self.view.drawing_area.queue_draw()

    def start_fade_loop(self):
        def draw():
            timer = (self.highlight_duration + 0.25 - time.time() + self.preview.visible_synctex_rectangles_time)
            if timer <= 0.4:
                self.view.drawing_area.queue_draw()
            return timer >= 0
        self.view.drawing_area.queue_draw()
        GObject.timeout_add(15, draw)

    #@timer
    def draw(self, drawing_area, ctx, width, height):
        if self.preview.layout == None:
            self.preview.setup_layout_and_zoom_levels()
            return

        self.draw_background(ctx, drawing_area)

        page_height = self.preview.layout.page_height
        page_gap = self.preview.layout.page_gap
        margin = self.preview.layout.get_horizontal_margin(width)
        scrolling_offset_x = self.view.content.scrolling_offset_x
        scrolling_offset_y = self.view.content.scrolling_offset_y
        first_page = int(scrolling_offset_y // (page_height + page_gap))
        last_page = min(int((scrolling_offset_y + height + 1) // (page_height + page_gap)), self.preview.poppler_document.get_n_pages() - 1)
        ctx.transform(cairo.Matrix(1, 0, 0, 1, margin - scrolling_offset_x, first_page * (page_height + page_gap) - scrolling_offset_y))

        for page_number in range(first_page, last_page + 1):
            self.draw_page_background_and_outline(ctx)
            self.draw_rendered_page(ctx, page_number)
            self.draw_synctex_rectangles(ctx, page_number)

            ctx.transform(cairo.Matrix(1, 0, 0, 1, 0, page_height + self.preview.layout.page_gap))

    def draw_background(self, ctx, drawing_area):
        ctx.rectangle(0, 0, drawing_area.get_allocated_width(), drawing_area.get_allocated_height())
        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('window_bg_color'))
        ctx.fill()

    #@timer
    def draw_page_background_and_outline(self, ctx):
        Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('borders'))
        ctx.rectangle(- self.preview.layout.border_width, - self.preview.layout.border_width, self.preview.layout.page_width + 2 * self.preview.layout.border_width, self.preview.layout.page_height + 2 * self.preview.layout.border_width)
        ctx.fill()

        if self.preview.recolor_pdf:
            Gdk.cairo_set_source_rgba(ctx, ColorManager.get_ui_color('view_bg_color'))
        else:
            ctx.set_source_rgba(1, 1, 1, 1)
        ctx.rectangle(0, 0, self.preview.layout.page_width, self.preview.layout.page_height)
        ctx.fill()

    def draw_rendered_page(self, ctx, page_number):
        if not page_number in self.page_renderer.rendered_pages: return

        rendered_page_data = self.page_renderer.rendered_pages[page_number]
        surface = rendered_page_data[0]
        page_width = rendered_page_data[1] * self.preview.layout.hidpi_factor

        if not isinstance(surface, cairo.ImageSurface): return

        matrix = ctx.get_matrix()
        factor = self.preview.layout.page_width / page_width
        ctx.scale(factor, factor)

        ctx.set_source_surface(surface, 0, 0)
        ctx.rectangle(0, 0, self.preview.layout.page_width / factor, self.preview.layout.page_height / factor)
        ctx.fill()

        ctx.set_matrix(matrix)

    def draw_synctex_rectangles(self, ctx, page_number):
        try:
            rectangles = self.preview.layout.visible_synctex_rectangles[page_number]
        except KeyError: pass
        else:
            time_factor = self.ease(min(self.highlight_duration + 0.25 - (time.time() - self.preview.visible_synctex_rectangles_time), 0.25) * 4)
            if time_factor < 0:
                self.preview.set_synctex_rectangles(list())
            else:
                color = ColorManager.get_ui_color('highlight_tag_preview')
                color.alpha *= time_factor
                Gdk.cairo_set_source_rgba(ctx, color)
                ctx.set_operator(cairo.Operator.MULTIPLY)
                for rectangle in rectangles:
                    ctx.rectangle(rectangle['x'], rectangle['y'], rectangle['width'], rectangle['height'])
                ctx.fill()
                ctx.set_operator(cairo.Operator.OVER)

    def ease(self, factor): return (factor - 1)**3 + 1



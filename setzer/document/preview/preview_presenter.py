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
gi.require_version('Gtk', '4.0')
from gi.repository import GObject
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
        self.preview.connect('invert_pdf_changed', self.on_invert_pdf_changed)
        self.preview.connect('layout_changed', self.on_layout_changed)
        self.page_renderer.connect('rendered_pages_changed', self.on_rendered_pages_changed)

        self.show_blank_slate()

    def on_pdf_changed(self, preview):
        if self.preview.poppler_document != None:
            self.show_pdf()
        else:
            self.show_blank_slate()

    def on_invert_pdf_changed(self, preview):
        self.view.drawing_area.queue_draw()

    def on_layout_changed(self, preview):
        if self.preview.layout != None:
            self.view.content.adjustment_x.set_upper(self.preview.layout.canvas_width)
            self.view.content.adjustment_y.set_upper(self.preview.layout.canvas_height)
            self.view.content.queue_draw()

    def on_rendered_pages_changed(self, page_renderer):
        self.view.drawing_area.queue_draw()

    def show_blank_slate(self):
        self.view.stack.set_visible_child_name('blank_slate')
        self.view.external_viewer_button.set_sensitive(False)
        self.view.external_viewer_button_revealer.set_reveal_child(False)

    def show_pdf(self):
        self.view.stack.set_visible_child_name('pdf')
        self.view.external_viewer_button.set_sensitive(True)
        self.view.external_viewer_button_revealer.set_reveal_child(True)

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
        if self.preview.layout == None: return

        bg_color = ColorManager.get_ui_color('theme_bg_color')
        border_color = ColorManager.get_ui_color('borders')
        self.draw_background(ctx, drawing_area, bg_color)

        page_height = self.preview.layout.page_height
        page_gap = self.preview.layout.page_gap
        margin = self.preview.layout.get_horizontal_margin(width)
        scrolling_offset_x = self.view.content.scrolling_offset_x
        scrolling_offset_y = self.view.content.scrolling_offset_y
        first_page = int(scrolling_offset_y // (page_height + page_gap))
        last_page = int((scrolling_offset_y + height + 1) // (page_height + page_gap))
        ctx.transform(cairo.Matrix(1, 0, 0, 1, margin - scrolling_offset_x, first_page * (page_height + page_gap) - scrolling_offset_y))

        for page_number in range(first_page, last_page + 1):
            self.draw_page_background_and_outline(ctx, border_color)
            self.draw_rendered_page(ctx, page_number)

            ctx.transform(cairo.Matrix(1, 0, 0, 1, 0, page_height + self.preview.layout.page_gap))

    def draw_background(self, ctx, drawing_area, bg_color):
        ctx.rectangle(0, 0, drawing_area.get_allocated_width(), drawing_area.get_allocated_height())
        ctx.set_source_rgba(bg_color.red, bg_color.green, bg_color.blue, bg_color.alpha)
        ctx.fill()

    #@timer
    def draw_page_background_and_outline(self, ctx, border_color):
        ctx.set_source_rgba(border_color.red, border_color.green, border_color.blue, border_color.alpha)
        ctx.rectangle(- self.preview.layout.border_width, - self.preview.layout.border_width, self.preview.layout.page_width + 2 * self.preview.layout.border_width, self.preview.layout.page_height + 2 * self.preview.layout.border_width)
        ctx.fill()
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
        if self.preview.invert_pdf:
            ctx.set_operator(cairo.Operator.DIFFERENCE)
            ctx.set_source_rgb(1, 1, 1)
            ctx.rectangle(0, 0, self.preview.layout.page_width / factor, self.preview.layout.page_height / factor)
            ctx.fill()
            ctx.set_operator(cairo.Operator.OVER)
        ctx.set_matrix(matrix)



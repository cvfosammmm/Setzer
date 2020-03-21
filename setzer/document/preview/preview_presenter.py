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
gi.require_version('Poppler', '0.18')
from gi.repository import Poppler
import cairo

import os.path
import math


class PreviewPresenter(object):

    def __init__(self, preview, layouter, page_renderer, view):
        self.preview = preview
        self.layouter = layouter
        self.page_renderer = page_renderer
        self.view = view

        self.view.drawing_area.connect('draw', self.draw)
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
            self.update_current_page()
            self.update_zoom_level()
            pass

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
            canvas_width = self.layouter.page_width + 2 * self.layouter.horizontal_margin
            canvas_height = self.preview.number_of_pages * (self.layouter.page_height + self.layouter.page_gap) - self.layouter.page_gap + 2 * self.layouter.horizontal_margin
            self.view.drawing_area.set_size_request(canvas_width, canvas_height)

    def scroll_to_position(self, position):
        if self.layouter.has_layout:
            yoffset = max((self.layouter.page_gap + self.layouter.page_height) * (position['page'] - 1) + self.layouter.vertical_margin + (position['y'] + position['height'] / 2) * self.layouter.scale_factor - self.view.scrolled_window.get_allocated_height() / 2, 0)
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

            for page in self.layouter.pages:
                ctx.set_source_rgba(border_color.red, border_color.green, border_color.blue, border_color.alpha)
                ctx.rectangle(page['x'] - self.layouter.border_width, page['y'] - self.layouter.border_width, page['width'] + 2 * self.layouter.border_width, page['height'] + 2 * self.layouter.border_width)
                ctx.fill()
                ctx.set_source_rgba(1, 1, 1, 1)
                ctx.rectangle(page['x'], page['y'], page['width'], page['height'])
                ctx.fill()

            for page_number, rendered_page_data in self.page_renderer.rendered_pages.items():
                surface = rendered_page_data[0]
                if isinstance(surface, cairo.ImageSurface):
                    page = self.layouter.pages[page_number]
                    ctx.set_source_surface(surface, page['x'], page['y'])
                    ctx.paint()
                    #ctx.transform(cairo.Matrix(1, 0, 0, 1, 0, size_y + 12 * self.hidpi_factor))
                    #self.rendered_pages[page_number].remove_previous_size_surface()

        '''if self.do_draw == True:

            if len(self.rendered_pages) > 0:
                
                ctx.transform(cairo.Matrix(1 / self.hidpi_factor, 0, 0, 1 / self.hidpi_factor, 11, 11))
                for page_number in range(self.number_of_pages):
                    size_x, size_y = self.rendered_pages[page_number].get_current_size()
                    ctx.set_source_rgba(border_color.red, border_color.green, border_color.blue, border_color.alpha)
                    ctx.rectangle(-1 * self.hidpi_factor, -1 * self.hidpi_factor, 2 * self.hidpi_factor + size_x, 2 * self.hidpi_factor + size_y)
                    ctx.fill()
                    ctx.set_source_rgba(1, 1, 1, 1)
                    ctx.rectangle(0, 0, size_x, size_y)
                    ctx.fill()

                    # draw .pdf
                    surface = self.rendered_pages[page_number].get_current_size_surface()
                    if isinstance(surface, cairo.ImageSurface):
                        ctx.set_source_surface(surface, 0, 0)
                        ctx.paint()
                        ctx.transform(cairo.Matrix(1, 0, 0, 1, 0, size_y + 12 * self.hidpi_factor))
                        self.rendered_pages[page_number].remove_previous_size_surface()
                    else:
                        surface = self.rendered_pages[page_number].get_previous_size_surface()
                        if isinstance(surface, cairo.ImageSurface):
                            matrix = ctx.get_matrix()
                            ctx.scale(*self.rendered_pages[page_number].get_scale_for_previous_size())
                            ctx.set_source_surface(surface, 0, 0)
                            ctx.paint()
                            ctx.set_matrix(matrix)
                            ctx.transform(cairo.Matrix(1, 0, 0, 1, 0, size_y + 12 * self.hidpi_factor))
                        else:
                            ctx.transform(cairo.Matrix(1, 0, 0, 1, 0, size_y + 12 * self.hidpi_factor))
            else:
                ctx.rectangle(0, 0, drawing_area.get_allocated_width(), drawing_area.get_allocated_height())
                ctx.set_source_rgba(bg_color.red, bg_color.green, bg_color.blue, bg_color.alpha)
                ctx.fill()
            return True
        return True'''



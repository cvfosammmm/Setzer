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
from gi.repository import Gtk


class PreviewView(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)
        self.get_style_context().add_class('preview')

        self.layout_data = None

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.connect('draw', self.draw)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.add(self.drawing_area)

    def set_layout_data(self, layout_data):
        self.layout_data = layout_data

    #@helpers.timer
    def draw(self, drawing_area, cairo_context, data = None):
        if self.layout_data != None:
            ctx = cairo_context
            bg_color = self.view.notebook.get_style_context().lookup_color('theme_bg_color')[1]
            border_color = self.view.notebook.get_style_context().lookup_color('borders')[1]

        '''if self.do_draw == True:

            if len(self.rendered_pages) > 0:
                ctx.rectangle(0, 0, drawing_area.get_allocated_width(), drawing_area.get_allocated_height())
                ctx.set_source_rgba(bg_color.red, bg_color.green, bg_color.blue, bg_color.alpha)
                ctx.fill()
                
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



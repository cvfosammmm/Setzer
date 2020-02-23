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
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Poppler
import cairo

import math
import os.path
import time
import _thread as thread, queue

import helpers.helpers as helpers
from app.service_locator import ServiceLocator


class Preview(object):
    ''' Init and controll preview widget '''
    
    def __init__(self):

        self.settings = ServiceLocator.get_settings()
        self.main_window = ServiceLocator.get_main_window()
        self.view = self.main_window.preview

        self.active_document = None

        self.ppi = self.get_ppi()
        self.zoom_factors_button = list()
        self.zoom_factors_scroll = list()
        self.zoom_factor_fit_width = None
        self.zoom_factor = 1.25
        self.real_zoom_factor = 1.0
        self.do_draw = True #lock
        self.zoom_momentum = 0.0
        self.hidpi_factor = self.view.get_scale_factor()
        
        self.view.zoom_widget.zoom_in_button.connect('clicked', self.on_zoom_button_clicked, 'in')
        self.view.zoom_widget.zoom_out_button.connect('clicked', self.on_zoom_button_clicked, 'out')
        self.view.drawing_area.connect('draw', self.draw)
        self.view.scrolled_window.connect('scroll-event', self.on_scroll)
        self.view.notebook.connect('size-allocate', self.on_size_allocate_view)
        self.view.drawing_area.connect('size-allocate', self.on_size_allocate_drawing_area)
        self.view.scrolled_window.get_vadjustment().connect('value-changed', self.on_adjustment_value_changed)

        # document attributes
        self.filename = None
        self.pdf_date = None
        self.pdf_position = None
        self.document = None
        self.number_of_pages = 0
        self.document_width_points = 0
        self.document_height_points = 0
        self.page_sizes_points = list()
        self.rendered_pages = dict()
        self.render_queue = queue.Queue()
        self.rendered_pages_queue = queue.Queue()
        self.page_render_count = dict()
        self.page_render_count_lock = thread.allocate_lock()
        self.current_page = 0
        self.current_page_lock = thread.allocate_lock()
        self.canvas_height = 0
        self.canvas_width = 0
        self.scroll_to_page_queue = queue.Queue()

        self.view.action_bar.show_all()
        GObject.timeout_add(50, self.check_filename_loop)
        GObject.timeout_add(50, self.check_rendered_pages_loop)
        thread.start_new_thread(self.render_page_loop, ())
        self.update_paging_widget()

    def set_active_document(self, document):
        self.active_document = document

    def check_filename_loop(self):
        if not self.view.notebook.get_allocated_width() > 100:
            return True

        if self.active_document != None:
            filename = self.active_document.get_pdf_filename()
            date = self.active_document.get_pdf_date()
            position = self.active_document.get_pdf_position()
            if self.filename != filename or self.pdf_date != date or self.pdf_position != position:
                self.filename = filename
                self.pdf_date = date
                self.pdf_position = position
                self.load_pdf(self.filename)
                self.render_pdf()
                if position != None:
                    x = (position['x'] * self.real_zoom_factor * self.ppi * self.hidpi_factor / 72) - self.view.notebook.get_allocated_width() / 2
                    y = (position['y'] * self.real_zoom_factor * self.ppi * self.hidpi_factor / 72) - self.view.notebook.get_allocated_height() / 2
                    if position['page'] == 1 and y < 50: y = -10.0
                    self.scroll_to_page_queue.put((position['page'], 0, y))
        if self.number_of_pages > 0:
            self.view.zoom_widget.show_all()
        else:
            self.view.zoom_widget.hide()
        return True
        
    #@helpers.timer
    def check_rendered_pages_loop(self):
        while self.rendered_pages_queue.empty() == False:
            try:
                todo = self.rendered_pages_queue.get(block=False)
            except queue.Empty:
                pass
            else:
                with self.page_render_count_lock:
                    try: render_count = self.page_render_count[todo['page_number']]
                    except KeyError: render_count = 0
                if todo['render_count'] == render_count:
                    self.rendered_pages[todo['page_number']].set_current_size_surface(todo['surface'])
                    self.view.drawing_area.queue_draw()
        return True

    '''
    *** zoom
    '''
    
    def setup_zoom_factors(self):
        if self.document_width_points != 0:
            self.zoom_factor_fit_width = ((self.view.notebook.get_allocated_width() - 22) / (self.ppi * self.hidpi_factor)) / (self.document_width_points / 72)

            self.zoom_factors_button = list()
            factors_button = [0.25*2**i for i in range(5)]
            index = 0
            while index < len(factors_button) and self.zoom_factor_fit_width > factors_button[index]:
                self.zoom_factors_button.append(factors_button[index])
                index += 1
            self.zoom_factors_button.append(self.zoom_factor_fit_width)
            while index < len(factors_button):
                self.zoom_factors_button.append(factors_button[index])
                index += 1

    def set_zoom_fit_to_width(self):
        old_real_zoom_factor = self.real_zoom_factor
        with self.current_page_lock:
            old_yoffset = self.view.scrolled_window.get_vadjustment().get_value() - self.get_page_offset(self.current_page)
        
        self.zoom_factor = self.zoom_factor_fit_width
        self.real_zoom_factor = self.zoom_factor_fit_width

        if old_real_zoom_factor != self.real_zoom_factor:
            self.render_pdf()
            self.view.drawing_area.queue_draw()
            
            if old_yoffset < 0: yoffset = -10.0
            else: yoffset = old_yoffset * self.real_zoom_factor / old_real_zoom_factor

            with self.current_page_lock:
                self.scroll_to_page_queue.put((self.current_page, 0, yoffset))

            self.update_paging_widget()
            self.view.zoom_widget.label.set_text('{:.1%}'.format(self.real_zoom_factor))
    
    def set_zoom(self, direction='in', type='button', factor=0, x=0, y=0):
        lower_bound = self.zoom_factor_fit_width * 0.8
        upper_bound = self.zoom_factor_fit_width * 1.25
        old_real_zoom_factor = self.real_zoom_factor
        with self.current_page_lock:
            old_yoffset = self.view.scrolled_window.get_vadjustment().get_value() - self.get_page_offset(self.current_page) + y
            old_xoffset = self.view.scrolled_window.get_hadjustment().get_value() + x
            old_page = self.current_page

        if type == 'button':
            zoom_factors = self.zoom_factors_button
            if direction == 'out':
                zoom_factors = zoom_factors[::-1]
                for factor in zoom_factors:
                    if factor < self.real_zoom_factor:
                        self.real_zoom_factor = factor
                        break
            else:
                for factor in zoom_factors:
                    if factor > self.real_zoom_factor:
                        self.real_zoom_factor = factor
                        break
            if self.real_zoom_factor < self.zoom_factor_fit_width:
                self.zoom_factor = 0.8 * self.real_zoom_factor
            elif self.real_zoom_factor == self.zoom_factor_fit_width:
                self.zoom_factor = self.real_zoom_factor
            else:
                self.zoom_factor = 1.25 * self.real_zoom_factor
        elif type == 'scroll':
            if direction == 'out':
                self.zoom_factor = max(self.zoom_factor * (1 - 0.1 * factor), 0.2)
            elif direction == 'in':
                self.zoom_factor = min(self.zoom_factor * (1 - 0.1 * factor), 5)
            if self.zoom_factor < lower_bound:
                self.real_zoom_factor = 1.25 * self.zoom_factor
            elif self.zoom_factor < upper_bound:
                self.real_zoom_factor = self.zoom_factor_fit_width
            else:
                self.real_zoom_factor = 0.8 * self.zoom_factor
        
        if old_real_zoom_factor != self.real_zoom_factor:
            self.render_pdf()

            self.view.drawing_area.queue_draw()

            if type == 'scroll':
                if self.zoom_factor >= 0.2 and self.zoom_factor <= 5:
                    if direction == 'out':
                        yoffset = -y + old_yoffset * self.real_zoom_factor / old_real_zoom_factor
                        xoffset = -x + old_xoffset * self.real_zoom_factor / old_real_zoom_factor
                        self.scroll_to_page_queue.put((old_page, xoffset, yoffset))
                    elif direction == 'in':
                        yoffset = -y + old_yoffset * self.real_zoom_factor / old_real_zoom_factor
                        xoffset = -x + old_xoffset * self.real_zoom_factor / old_real_zoom_factor
                        self.scroll_to_page_queue.put((old_page, xoffset, yoffset))
            elif type == 'button':
                if self.zoom_factor >= 0.2 and self.zoom_factor <= 5:
                    if direction == 'out':
                        yoffset = -y + old_yoffset * self.real_zoom_factor / old_real_zoom_factor
                        xoffset = -x + old_xoffset * self.real_zoom_factor / old_real_zoom_factor
                        self.scroll_to_page_queue.put((old_page, xoffset, yoffset))
                    elif direction == 'in':
                        yoffset = -y + old_yoffset * self.real_zoom_factor / old_real_zoom_factor
                        xoffset = -x + old_xoffset * self.real_zoom_factor / old_real_zoom_factor
                        self.scroll_to_page_queue.put((old_page, xoffset, yoffset))
            
            self.update_paging_widget()
            self.view.zoom_widget.label.set_text('{:.1%}'.format(self.real_zoom_factor))
    
    '''
    *** scrolling
    '''
    
    def get_page_offset(self, page_number):
        newy = 10
        for page_number in range(page_number - 1):
            if self.rendered_pages[page_number].current_size_y == None:
                return 0
            newy += self.rendered_pages[page_number].current_size_y + 12
        return newy
    
    def scroll_to_page(self, page_number, xoffset=0, yoffset=0):
        newy = self.get_page_offset(page_number) + yoffset
        self.view.scrolled_window.get_vadjustment().set_value(newy)
        self.view.scrolled_window.get_hadjustment().set_value(xoffset)
    
    '''
    *** actions
    '''
    
    def update_paging_widget(self):
        with self.current_page_lock:
            self.current_page = 0
        offset = self.view.scrolled_window.get_vadjustment().get_value()
        size_iter = 10
        total = self.number_of_pages
        with self.current_page_lock:
            while size_iter <= offset:
                try:
                    size_iter += self.rendered_pages[self.current_page].current_size_y / self.hidpi_factor + 12
                except KeyError:
                    break
                else:
                    self.current_page += 1

        if total > 0:
            with self.current_page_lock:
                self.view.paging_widget.label.set_text('Page ' + str(max(self.current_page, 1)) + ' of ' + str(total))
        else:
            self.view.paging_widget.label.set_text('Page 0 of 0')
    
    def load_pdf(self, filename):
        self.do_draw = False
        if isinstance(filename, str) and os.path.exists(filename):
            with self.page_render_count_lock:
                self.page_render_count = dict()
            try:
                self.document = Poppler.Document.new_from_file('file:' + filename)
            except gi.repository.GLib.Error:
                self.document = None
                self.number_of_pages = 0
                self.update_paging_widget()
                self.view.notebook.set_current_page(0)
            else:
                self.number_of_pages = self.document.get_n_pages()
                self.update_paging_widget()

                self.document_width_points = 0
                self.document_height_points = 0
                self.page_sizes_points = list()
                self.rendered_pages = dict()

                for page_number in range(self.document.get_n_pages()):
                    page_size = self.document.get_page(page_number).get_size()
                    with self.page_render_count_lock:
                        self.page_render_count[page_number] = 0
                    self.page_sizes_points.append([page_size.width, page_size.height])
                    self.rendered_pages[page_number] = RenderedPage()
                    self.document_height_points += page_size.height
                    if page_size.width > self.document_width_points:
                        self.document_width_points = page_size.width

                self.setup_zoom_factors()
                self.set_zoom_fit_to_width()
                self.view.notebook.set_current_page(1)
        else:
            self.document = None
            self.number_of_pages = 0
            self.update_paging_widget()
            self.view.notebook.set_current_page(0)
        self.do_draw = True

    def set_canvas_size(self, document_height_pixels):
        self.canvas_width = int(self.real_zoom_factor * self.ppi * self.hidpi_factor * self.document_width_points / 72) + 22
        old_height = self.canvas_height
        self.canvas_height = (int(document_height_pixels / self.hidpi_factor) + self.document.get_n_pages() * 12 + 12)
        if old_height == self.canvas_height: self.canvas_height += 1

    #@helpers.timer
    def render_pdf(self):
        self.do_draw = False
        if isinstance(self.document, Poppler.Document):
            number_of_pages = self.document.get_n_pages()
            document_height_pixels = 0
            for page_number in range(number_of_pages):
                self.rendered_pages[page_number].remove_current_size_surface()
                page_size = self.page_sizes_points[page_number]
                width_pixels = int(self.real_zoom_factor * self.ppi * self.hidpi_factor * self.hidpi_factor * page_size[0] / 72)
                height_pixels = int(self.real_zoom_factor * self.ppi * self.hidpi_factor * self.hidpi_factor * page_size[1] / 72)
                document_height_pixels += height_pixels
                with self.page_render_count_lock:
                    self.page_render_count[page_number] += 1
                    self.render_queue.put({'page_number': page_number, 'render_count': self.page_render_count[page_number], 'real_zoom_factor': self.real_zoom_factor, 'ppi': self.ppi})
                self.rendered_pages[page_number].set_current_size(width_pixels, height_pixels)

            self.set_canvas_size(document_height_pixels)
            self.view.drawing_area.set_size_request(self.canvas_width - 1, self.canvas_height)
        else:
            self.view.drawing_area.set_size_request(-1, -1)

        self.do_draw = True
        self.view.drawing_area.queue_draw()
    
    #@helpers.timer
    def render_page_loop(self):
        while True:
            try: todo = self.render_queue.get(block=False)
            except queue.Empty: time.sleep(0.1)
            else:
                with self.page_render_count_lock:
                    try: render_count = self.page_render_count[todo['page_number']]
                    except: KeyError: render_count = 0
                if todo['render_count'] == render_count:
                    page = self.document.get_page(todo['page_number'])
                    page_size_points = page.get_size()
                    real_zoom_factor = todo['real_zoom_factor']
                    ppi = todo['ppi']
                    width_pixels = int(real_zoom_factor * ppi * self.hidpi_factor * self.hidpi_factor * page_size_points.width / 72)
                    height_pixels = int(real_zoom_factor * ppi * self.hidpi_factor * self.hidpi_factor * page_size_points.height / 72)
                    scale_factor = width_pixels / page_size_points[0]
                    surface = cairo.ImageSurface(cairo.Format.ARGB32, width_pixels, height_pixels)
                    ctx = cairo.Context(surface)
                    ctx.scale(scale_factor, scale_factor)
                    page.render(ctx)
                    self.rendered_pages_queue.put({'page_number': todo['page_number'], 'render_count': todo['render_count'], 'surface': surface})
        
    def get_ppi(self):
        ''' pixels per inch '''
        
        monitor = Gdk.Display.get_default().get_monitor_at_point(1, 1)
        width_inch = monitor.get_width_mm() / 25.4
        width_pixels = monitor.get_geometry().width
        
        if width_inch > 0 and width_pixels > 0:
            return int(width_pixels / width_inch)
        else:
            return 96
            
    #@helpers.timer
    def draw(self, drawing_area, cairo_context, data = None):
        if self.do_draw == True:
            ctx = cairo_context
            bg_color = self.view.notebook.get_style_context().lookup_color('theme_bg_color')[1]
            border_color = self.view.notebook.get_style_context().lookup_color('borders')[1]

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
        return True

    '''
    *** signal handlers
    '''
    
    def on_zoom_button_clicked(self, button, direction):
        self.set_zoom(direction, 'button')
        
    def on_adjustment_value_changed(self, adjustment):
        self.update_paging_widget()
    
    def on_scroll(self, widget, event):
        if event.state == Gdk.ModifierType.CONTROL_MASK:
            direction = False
            if event.delta_y - event.delta_x < 0:
                direction = 'in'
            elif event.delta_y - event.delta_x > 0:
                direction = 'out'
            if direction != False:
                self.zoom_momentum += event.delta_y - event.delta_x
                if(self.scroll_to_page_queue.empty()):
                    self.set_zoom(direction, 'scroll', self.zoom_momentum, event.x, event.y)
                    self.zoom_momentum = 0.0
            return True
        return False
    
    def on_size_allocate_view(self, view=None, allocation=None):
        if self.real_zoom_factor == self.zoom_factor_fit_width:
            self.setup_zoom_factors()
            self.set_zoom_fit_to_width()
        else:
            self.setup_zoom_factors()

    def on_size_allocate_drawing_area(self, view=None, allocation=None):
        if int(self.view.drawing_area.get_allocated_height()) == int(self.canvas_height):
            while self.scroll_to_page_queue.empty() == False:
                try:
                    todo = self.scroll_to_page_queue.get(block=False)
                except queue.Empty:
                    pass
                else:
                    if(self.scroll_to_page_queue.empty()):
                        self.scroll_to_page(*todo)


class RenderedPage(object):

    def __init__(self):
        self.current_size_surface = None
        self.current_size_x = None
        self.current_size_y = None
        self.previous_size_surface = None
        self.previous_size_x = None
        self.previous_size_y = None
    
    def set_current_size_surface(self, surface):
        self.current_size_surface = surface

    def set_current_size(self, x, y):
        self.current_size_x = x
        self.current_size_y = y

    def remove_current_size_surface(self):
        if self.has_current_size_surface():
            self.flip_current_to_previous()
            self.current_size_x = None
            self.current_size_y = None
            self.current_size_surface = None

    def remove_previous_size_surface(self):
        self.previous_size_x = None
        self.previous_size_y = None
        self.previous_size_surface = None

    def flip_current_to_previous(self):
        self.previous_size_x = self.current_size_x
        self.previous_size_y = self.current_size_y
        self.previous_size_surface = self.current_size_surface
    
    def has_current_size_surface(self):
        return isinstance(self.current_size_surface, cairo.ImageSurface)

    def get_current_size_surface(self):
        return self.current_size_surface

    def get_current_size(self):
        return self.current_size_x, self.current_size_y

    def get_previous_size_surface(self):
        return self.previous_size_surface

    def get_scale_for_previous_size(self):
        scale_x = self.current_size_x / self.previous_size_x
        scale_y = self.current_size_y / self.previous_size_y
        return (scale_x, scale_y)





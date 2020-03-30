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

import os.path
import math
import _thread as thread

import setzer.document.preview.preview_viewgtk as preview_view
import setzer.document.preview.preview_layouter as preview_layouter
import setzer.document.preview.preview_presenter as preview_presenter
import setzer.document.preview.preview_controller as preview_controller
import setzer.document.preview.preview_page_renderer as preview_page_renderer
import setzer.document.preview.zoom_widget.zoom_widget as zoom_widget
from setzer.helpers.observable import Observable


class Preview(Observable):

    def __init__(self, document):
        Observable.__init__(self)
        self.document = document

        self.pdf_filename = None
        self.pdf_date = None

        self.poppler_document_lock = thread.allocate_lock()
        self.poppler_document = None
        self.number_of_pages = 0
        self.page_width = None
        self.page_height = None
        self.xoffset = 0
        self.yoffset = 0
        self.zoom_levels = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 4.0]
        self.zoom_level_fit_to_width = None
        self.zoom_level = None
        self.pdf_loaded = False

        self.first_show = True

        self.view = preview_view.PreviewView()
        self.layouter = preview_layouter.PreviewLayouter(self, self.view)
        self.controller = preview_controller.PreviewController(self, self.layouter, self.view)
        self.page_renderer = preview_page_renderer.PreviewPageRenderer(self, self.layouter)
        self.presenter = preview_presenter.PreviewPresenter(self, self.layouter, self.page_renderer, self.view)
        self.zoom_widget = zoom_widget.ZoomWidget(self)

        self.document.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'build_system_visibility_change':
            is_visible = parameter
            if is_visible:
                self.page_renderer.activate()
            else:
                self.page_renderer.deactivate()

    def get_pdf_filename(self):
        return self.pdf_filename
        
    def set_pdf_filename_from_tex_filename(self, tex_filename):
        if tex_filename != None:
            pdf_filename = os.path.splitext(self.document.filename)[0] + '.pdf'
            if os.path.exists(pdf_filename):
                self.set_pdf_filename(pdf_filename)

    def set_pdf_filename(self, pdf_filename):
        if pdf_filename != self.pdf_filename:
            self.pdf_filename = pdf_filename
        self.set_pdf_date()
        self.load_pdf()

    def reset_pdf_data(self):
        self.pdf_loaded = False
        self.pdf_filename = None
        self.pdf_date = None
        with self.poppler_document_lock:
            self.poppler_document = None
        self.number_of_pages = 0
        self.page_width = None
        self.page_height = None
        self.xoffset = 0
        self.yoffset = 0
        self.zoom_level = None
        self.add_change_code('pdf_changed')

    def set_position_from_offsets(self, xoffset=None, yoffset=None):
        value_changed = False
        if xoffset != None and xoffset != self.xoffset:
            self.xoffset = xoffset
            value_changed = True
        if yoffset != None and yoffset != self.yoffset:
            self.yoffset = yoffset
            value_changed = True
        if value_changed:
            self.add_change_code('position_changed')

    def get_position(self):
        if self.xoffset != None and self.yoffset != None:
            page = math.floor(self.yoffset / self.page_height) + 1
            return {'page': page, 'x': self.xoffset, 'y': self.yoffset - (page - 1) * self.page_height}

    def get_position_by_screen_offset(self, xoffset, yoffset):
        if self.xoffset != None and self.yoffset != None:
            page = math.floor(self.yoffset / self.page_height) + 1
            return {'page': page, 'x': self.xoffset + xoffset, 'y': self.yoffset - (page - 1) * self.page_height + yoffset}

    def scroll_to_position_from_offsets(self, xoffset=0, yoffset=0):
        if self.layouter.has_layout:
            page = math.floor(yoffset / self.page_height) + 1
            self.presenter.scroll_to_position({'page': page, 'x': xoffset, 'y': yoffset - (page - 1) * self.page_height})

    def scroll_to_synctex_position(self, position):
        if self.layouter.has_layout:
            self.presenter.scroll_to_position({'page': position['page'], 'x': max((self.layouter.page_width / 2 + self.layouter.horizontal_margin - self.view.scrolled_window.get_allocated_width() / 2) / self.layouter.scale_factor, 0), 'y': max(((position['y'] + position['height'] / 2) * self.layouter.scale_factor - self.view.scrolled_window.get_allocated_height() / 2) / self.layouter.scale_factor, 0)})

    def set_pdf_date(self):
        if self.pdf_filename != None:
            self.pdf_date = os.path.getmtime(self.pdf_filename)

    def get_pdf_date(self):
        return self.pdf_date

    def load_pdf(self):
        try:
            with self.poppler_document_lock:
                self.poppler_document = Poppler.Document.new_from_file('file:' + self.pdf_filename)
        except TypeError:
            self.reset_pdf_data()
        except gi.repository.GLib.Error:
            self.reset_pdf_data()
        else:
            with self.poppler_document_lock:
                self.number_of_pages = self.poppler_document.get_n_pages()
                page_size = self.poppler_document.get_page(0).get_size()
                self.page_width = page_size.width
                self.page_height = page_size.height
            self.pdf_loaded = True
            self.add_change_code('pdf_changed')
            self.set_zoom_fit_to_width()

    def update_fit_to_width_zoom_level(self, level):
        if level != self.zoom_level_fit_to_width:
            self.zoom_level_fit_to_width = level
            if level != None:
                self.zoom_levels = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 4.0, level]
            else:
                self.zoom_levels = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 4.0]

    def set_zoom_fit_to_width(self):
        if self.zoom_level_fit_to_width != None:
            self.set_zoom_level(self.zoom_level_fit_to_width)
        else:
            self.set_zoom_level(1.0)
    
    def set_zoom_fit_to_width_auto_offset(self):
        if self.zoom_level_fit_to_width != None:
            zoom_level = self.zoom_level_fit_to_width
        else:
            zoom_level = 1.0
        x = self.view.get_allocated_width() / 2
        y = self.view.get_allocated_height() / 2
        xoffset = (-x + x * zoom_level / self.zoom_level) / (zoom_level * self.layouter.ppp)
        yoffset = (-y + y * zoom_level / self.zoom_level) / (zoom_level * self.layouter.ppp)
        self.set_zoom_level(zoom_level, xoffset, yoffset)

    def zoom_in(self):
        try:
            zoom_level = min([level for level in self.zoom_levels if level > self.zoom_level])
        except ValueError:
            zoom_level = max(self.zoom_levels)
        x = self.view.get_allocated_width() / 2
        y = self.view.get_allocated_height() / 2
        xoffset = (-x + x * zoom_level / self.zoom_level) / (zoom_level * self.layouter.ppp)
        yoffset = (-y + y * zoom_level / self.zoom_level) / (zoom_level * self.layouter.ppp)
        self.set_zoom_level(zoom_level, xoffset, yoffset)

    def zoom_out(self):
        try:
            zoom_level = max([level for level in self.zoom_levels if level < self.zoom_level])
        except ValueError:
            zoom_level = min(self.zoom_levels)
        x = self.view.get_allocated_width() / 2
        y = self.view.get_allocated_height() / 2
        xoffset = (-x + x * zoom_level / self.zoom_level) / (zoom_level * self.layouter.ppp)
        yoffset = (-y + y * zoom_level / self.zoom_level) / (zoom_level * self.layouter.ppp)
        self.set_zoom_level(zoom_level, xoffset, yoffset)

    def set_zoom_level_auto_offset(self, zoom_level):
        x = self.view.get_allocated_width() / 2
        y = self.view.get_allocated_height() / 2
        xoffset = (-x + x * zoom_level / self.zoom_level) / (zoom_level * self.layouter.ppp)
        yoffset = (-y + y * zoom_level / self.zoom_level) / (zoom_level * self.layouter.ppp)
        self.set_zoom_level(zoom_level, xoffset, yoffset)

    def set_zoom_level(self, level, xoffset=0, yoffset=0):
        if level != self.zoom_level:
            self.zoom_level = level
            position = self.get_position_by_screen_offset(xoffset, yoffset)
            self.presenter.scroll_to_position(position)
            self.add_change_code('zoom_level_changed')



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
        self.zoom_levels = [0.25, 0.5, 1.0, 2.0, 4.0]
        self.zoom_level_fit_to_width = None
        self.zoom_level = None
        self.pdf_loaded = False

        self.first_show = True

        self.view = preview_view.PreviewView()
        self.layouter = preview_layouter.PreviewLayouter(self, self.view)
        self.controller = preview_controller.PreviewController(self, self.layouter, self.view)
        self.page_renderer = preview_page_renderer.PreviewPageRenderer(self, self.layouter)
        self.presenter = preview_presenter.PreviewPresenter(self, self.layouter, self.page_renderer, self.view)

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

    def set_pdf_position(self, position, scroll=False):
        if position == None: return
        if scroll:
            self.presenter.scroll_to_position(position)
        else:
            if position != None:
                self.xoffset = self.page_height * (position['page'] - 1) + position['x']
                self.yoffset = position['y']
            self.add_change_code('position_changed')

    def set_pdf_position_from_offsets(self, xoffset=None, yoffset=None, scroll=False):
        if scroll:
            self.view.scrolled_window.get_vadjustment().set_value(1000)
        else:
            value_changed = False
            if xoffset != None and xoffset != self.xoffset:
                self.xoffset = xoffset
                value_changed = True
            if yoffset != None and yoffset != self.yoffset:
                self.yoffset = yoffset
                value_changed = True
            if value_changed:
                self.add_change_code('position_changed')

    def get_pdf_position(self):
        if self.xoffset != None and self.yoffset != None:
            page = math.floor(self.xoffset / self.page_height) + 1
            return {'page': page, 'x': self.xoffset - (page - 1) * self.page_height, 'y': self.yoffset}

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
                self.zoom_levels = [0.25, 0.5, 1.0, 2.0, 4.0, level]
            else:
                self.zoom_levels = [0.25, 0.5, 1.0, 2.0, 4.0]

    def set_zoom_fit_to_width(self):
        if self.zoom_level_fit_to_width != None:
            self.set_zoom_level(self.zoom_level_fit_to_width)
        else:
            self.set_zoom_level(1.0)
    
    def zoom_in(self):
        try:
            self.set_zoom_level(min([level for level in self.zoom_levels if level > self.zoom_level]))
        except ValueError:
            self.set_zoom_level(max(self.zoom_levels))

    def zoom_out(self):
        try:
            self.set_zoom_level(max([level for level in self.zoom_levels if level < self.zoom_level]))
        except ValueError:
            self.set_zoom_level(min(self.zoom_levels))

    def set_zoom_level(self, level):
        if level != self.zoom_level:
            self.zoom_level = level
            self.add_change_code('zoom_level_changed')



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

import document.preview.preview_viewgtk as preview_view
import document.preview.preview_presenter as preview_presenter
from helpers.observable import Observable


class Preview(Observable):

    def __init__(self, document):
        Observable.__init__(self)
        self.document = document

        self.pdf_filename = None
        self.pdf_date = None

        self.poppler_document = None
        self.number_of_pages = None
        self.page_width = None
        self.page_height = None
        self.xoffset = None
        self.yoffset = None
        self.zoom_level = None

        self.view = preview_view.PreviewView()
        self.presenter = preview_presenter.PreviewPresenter(self, self.view)

    def get_pdf_filename(self):
        return self.pdf_filename
        
    def set_pdf_filename_from_tex_filename(self, tex_filename):
        if tex_filename != None:
            pdf_filename = os.path.splitext(self.document.filename)[0] + '.pdf'
            if os.path.exists(pdf_filename):
                self.set_pdf_filename(pdf_filename)

    def set_pdf_filename(self, pdf_filename):
        self.pdf_filename = pdf_filename
        self.set_pdf_date()
        self.load_pdf()

    def reset_pdf_data(self):
        self.pdf_filename = None
        self.pdf_date = None
        self.poppler_document = None
        self.number_of_pages = None
        self.page_width = None
        self.page_height = None
        self.xoffset = None
        self.yoffset = None
        self.zoom_level = None
        self.add_change_code('pdf_changed')

    def set_pdf_position(self, position):
        if position != None:
            self.xoffset = self.page_height * (position['page'] - 1) + position['x']
            self.yoffset = position['y']
        self.add_change_code('position_changed')

    def set_pdf_position_from_offsets(self, xoffset, yoffset):
        self.xoffset = xoffset
        self.yoffset = yoffset
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
            self.poppler_document = Poppler.Document.new_from_file('file:' + self.pdf_filename)
        except TypeError:
            self.reset_pdf_data()
        except gi.repository.GLib.Error:
            self.reset_pdf_data()
        else:
            self.number_of_pages = self.poppler_document.get_n_pages()
            page_size = self.poppler_document.get_page(0).get_size()
            self.page_width = page_size.width
            self.page_height = page_size.height
            self.xoffset = 0
            self.yoffset = 0
            self.zoom_level = 1.0
            self.add_change_code('pdf_changed')



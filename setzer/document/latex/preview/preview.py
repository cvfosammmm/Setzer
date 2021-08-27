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
from pdfminer.pdfpage import PDFPage
from pdfminer.pdftypes import PDFObjRef

import os.path
import math
import time
import subprocess
import _thread as thread

import setzer.document.latex.preview.preview_viewgtk as preview_view
import setzer.document.latex.preview.preview_layouter as preview_layouter
import setzer.document.latex.preview.preview_presenter as preview_presenter
import setzer.document.latex.preview.preview_controller as preview_controller
import setzer.document.latex.preview.preview_page_renderer as preview_page_renderer
import setzer.document.latex.preview.zoom_widget.zoom_widget as zoom_widget
import setzer.document.latex.preview.paging_widget.paging_widget as paging_widget
from setzer.helpers.observable import Observable
from setzer.helpers.timer import timer


class Preview(Observable):

    def __init__(self, document):
        Observable.__init__(self)
        self.document = document

        self.pdf_filename = None
        self.pdf_date = None
        self.invert_pdf = False

        self.poppler_document_lock = thread.allocate_lock()
        self.poppler_document = None
        self.links_lock = thread.allocate_lock()
        self.links_parsed = True
        with self.links_lock:
            self.links = dict()
        self.links_parser_lock = thread.allocate_lock()
        self.number_of_pages = 0
        self.page_width = None
        self.page_height = None
        self.xoffset = 0
        self.yoffset = 0
        self.zoom_levels = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 4.0]
        self.zoom_level_fit_to_width = None
        self.zoom_level_fit_to_text_width = None
        self.zoom_level_fit_to_height = None
        self.zoom_level = None
        self.visible_synctex_rectangles = list()
        self.visible_synctex_rectangles_time = None
        self.pdf_loaded = False

        self.is_visible = False
        self.first_show = True

        self.view = preview_view.PreviewView()
        self.layouter = preview_layouter.PreviewLayouter(self, self.view)
        self.controller = preview_controller.PreviewController(self, self.layouter, self.view)
        self.page_renderer = preview_page_renderer.PreviewPageRenderer(self, self.layouter)
        self.presenter = preview_presenter.PreviewPresenter(self, self.layouter, self.page_renderer, self.view)
        self.paging_widget = paging_widget.PagingWidget(self, self.layouter)
        self.zoom_widget = zoom_widget.ZoomWidget(self)

        self.document.connect('build_system_visibility_change', self.on_build_system_visibility_change)
        self.document.connect('filename_change', self.on_filename_change)
        self.document.connect('pdf_updated', self.on_pdf_updated)

    def on_build_system_visibility_change(self, document, is_visible):
        self.is_visible = is_visible
        if self.is_visible:
            self.page_renderer.activate()
        else:
            self.page_renderer.deactivate()
        thread.start_new_thread(self.update_links, ())

    def on_filename_change(self, document, filename):
        self.set_pdf_filename_from_tex_filename(filename)
        self.set_pdf_date()
        self.load_pdf()

    def on_pdf_updated(self, document):
        self.set_pdf_date()
        self.load_pdf()

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

    def set_invert_pdf(self, invert_pdf):
        self.invert_pdf = invert_pdf
        self.add_change_code('invert_pdf_changed')

    def reset_pdf_data(self):
        self.pdf_loaded = False
        self.pdf_filename = None
        self.pdf_date = None
        with self.poppler_document_lock:
            self.poppler_document = None
        self.number_of_pages = 0
        self.page_width = None
        self.page_height = None
        self.links_parsed = True
        self.links = dict()
        self.xoffset = 0
        self.yoffset = 0
        self.zoom_level = None
        self.add_change_code('pdf_changed')
        self.document.update_can_sync()

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

    def scroll_dest_on_screen(self, dest):
        page_number = dest.page_num
        if self.xoffset > dest.left:
            x = dest.left
        else:
            x = self.xoffset
        self.presenter.scroll_to_position({'page': page_number, 'x': x, 'y': self.page_height - dest.top})

    def set_synctex_rectangles(self, rectangles):
        if self.layouter.has_layout:
            self.visible_synctex_rectangles = rectangles
            self.layouter.update_synctex_rectangles()
            self.visible_synctex_rectangles_time = time.time()
            if len(rectangles) > 0:
                position = rectangles[0]
                self.presenter.scroll_to_position({'page': position['page'], 'x': max((self.layouter.page_width / 2 + self.layouter.horizontal_margin - self.view.stack.get_allocated_width() / 2) / self.layouter.scale_factor, 0), 'y': max(((position['v'] - position['height'] / 2) * self.layouter.scale_factor - self.view.stack.get_allocated_height() / 2) / self.layouter.scale_factor, 0)})
                self.presenter.start_fade_loop()

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
                current_min = self.page_width
                for page_number in range(0, min(self.number_of_pages, 3)):
                    page = self.poppler_document.get_page(page_number)
                    layout = page.get_text_layout()
                    for rect in layout[1]:
                        if rect.x1 < current_min:
                            current_min = rect.x1
                current_min -= 20
                self.vertical_margin = current_min
            self.pdf_loaded = True
            self.document.update_can_sync()
            self.add_change_code('pdf_changed')
            with self.links_lock:
                self.links = dict()
            self.links_parsed = False
            thread.start_new_thread(self.update_links, ())
            self.set_zoom_fit_to_width()
            self.document.update_can_sync()

    def get_page_number_and_offsets_by_document_offsets(self, x, y):
        return self.layouter.get_page_number_and_offsets_by_document_offsets(x, y)

    def get_links_for_page(self, page_number):
        with self.links_lock:
            try:
                return self.links[page_number]
            except KeyError:
                return list()

    def update_links(self):
        with self.links_parser_lock:
            if self.links_parsed: return
            if not self.is_visible: return

            links = dict()

            with open(self.pdf_filename, 'rb') as file:
                for page_num, page in enumerate(PDFPage.get_pages(file)):
                    links[page_num] = list()
                    annots_final = self.resolve_annots(page.annots)
                    for annot in annots_final:
                        try:
                            rect = annot['Rect']
                        except KeyError:
                            pass
                        else:
                            try:
                                data = annot['A']
                            except KeyError:
                                pass
                            else:
                                try:
                                    named_dest = data['D']
                                except KeyError:
                                    pass
                                else:
                                    dest = self.poppler_document.find_dest(named_dest.decode('utf-8'))
                                    links[page_num].append([rect, dest, 'goto'])
                                try:
                                    uri = data['URI']
                                except KeyError:
                                    pass
                                else:
                                    links[page_num].append([rect, uri.decode('utf-8'), 'uri'])
            with self.links_lock:
                self.links = links
                self.links_parsed = True

    def resolve_annots(self, annots):
        if annots == None: return []

        if type(annots) is PDFObjRef:
            annots = annots.resolve()

        if type(annots) is dict:
            return [annots]
        else:
            return_value = list()
            for annot in annots:
                if type(annots) is dict:
                    return_value.append(annot)
                else:
                    return_value += self.resolve_annots(annot)
            return return_value

    def update_fit_to_width_zoom_level(self, level):
        if level != self.zoom_level_fit_to_width:
            self.zoom_level_fit_to_width = level
            if level != None:
                self.zoom_levels = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 4.0, level]
            else:
                self.zoom_levels = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 4.0]

    def set_zoom_fit_to_height(self):
        zoom_level = (self.view.stack.get_allocated_height() + self.layouter.border_width) / (self.page_height * self.layouter.ppp)
        if zoom_level == self.zoom_level: return

        xoffset = ((self.page_width * zoom_level * self.layouter.ppp - self.view.get_allocated_width()) / 2) / (zoom_level * self.layouter.ppp) - self.xoffset
        y = self.view.get_allocated_height() / 2
        yoffset = (-y + y * zoom_level / self.zoom_level) / (zoom_level * self.layouter.ppp)
        self.zoom_level_fit_to_height = zoom_level
        self.set_zoom_level(zoom_level, xoffset, yoffset)

    def set_zoom_fit_to_text_width(self):
        zoom_level = self.zoom_level_fit_to_width * (self.page_width / (self.page_width - 2 * self.vertical_margin))
        if zoom_level == self.zoom_level: return

        xoffset = ((self.page_width * zoom_level * self.layouter.ppp - self.view.get_allocated_width()) / 2) / (zoom_level * self.layouter.ppp) - self.xoffset
        y = self.view.get_allocated_height() / 2
        yoffset = (-y + y * zoom_level / self.zoom_level) / (zoom_level * self.layouter.ppp)
        self.zoom_level_fit_to_text_width = zoom_level
        self.set_zoom_level(zoom_level, xoffset, yoffset)

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

    def open_external_viewer(self):
        if self.pdf_filename != None:
            subprocess.call(["xdg-open", self.pdf_filename])



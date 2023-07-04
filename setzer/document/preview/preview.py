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
gi.require_version('Gtk', '4.0')
from gi.repository import Poppler
from gi.repository import GLib
from gi.repository import Gio

import os.path
import time
import math

import setzer.document.preview.preview_viewgtk as preview_view
import setzer.document.preview.preview_layouter as preview_layouter
import setzer.document.preview.preview_presenter as preview_presenter
import setzer.document.preview.preview_controller as preview_controller
import setzer.document.preview.preview_page_renderer as preview_page_renderer
import setzer.document.preview.preview_links_parser as preview_links_parser
import setzer.document.preview.preview_zoom_manager as preview_zoom_manager
import setzer.document.preview.zoom_widget.zoom_widget as zoom_widget
import setzer.document.preview.paging_widget.paging_widget as paging_widget
from setzer.helpers.observable import Observable
from setzer.helpers.timer import timer


class Preview(Observable):

    def __init__(self, document):
        Observable.__init__(self)
        self.document = document

        self.pdf_filename = None
        self.invert_pdf = False

        self.poppler_document = None
        self.page_width = None
        self.page_height = None
        self.layout = None

        self.visible_synctex_rectangles = list()
        self.visible_synctex_rectangles_time = None

        self.view = preview_view.PreviewView()
        self.layouter = preview_layouter.PreviewLayouter(self, self.view)
        self.zoom_manager = preview_zoom_manager.PreviewZoomManager(self, self.view)
        self.controller = preview_controller.PreviewController(self, self.view)
        self.page_renderer = preview_page_renderer.PreviewPageRenderer(self)
        self.links_parser = preview_links_parser.PreviewLinksParser(self)
        self.presenter = preview_presenter.PreviewPresenter(self, self.page_renderer, self.view)
        self.paging_widget = paging_widget.PagingWidget(self)
        self.zoom_widget = zoom_widget.ZoomWidget(self)

        self.document.connect('filename_change', self.on_filename_change)
        self.document.connect('pdf_updated', self.on_pdf_updated)

    def on_filename_change(self, document, filename=None):
        if filename != None:
            pdf_filename = os.path.splitext(filename)[0] + '.pdf'
            if os.path.exists(pdf_filename):
                self.set_pdf_filename(pdf_filename)
        self.load_pdf()

    def on_pdf_updated(self, document):
        self.load_pdf()

    def set_pdf_filename(self, pdf_filename):
        if pdf_filename != self.pdf_filename:
            self.pdf_filename = pdf_filename

    def set_invert_pdf(self, invert_pdf):
        self.invert_pdf = invert_pdf
        self.add_change_code('invert_pdf_changed')

    def get_pdf_date(self):
        if self.pdf_filename != None:
            return os.path.getmtime(self.pdf_filename)
        else:
            return None

    def load_pdf(self):
        try:
            self.poppler_document = Poppler.Document.new_from_file('file:' + self.pdf_filename)
        except TypeError:
            self.reset_pdf_data()
        except gi.repository.GLib.Error:
            self.reset_pdf_data()
        else:
            page_size = self.poppler_document.get_page(0).get_size()
            self.page_width = page_size.width
            self.page_height = page_size.height
            self.update_vertical_margin()
            self.zoom_manager.update_dynamic_zoom_levels()
            self.layout = self.layouter.create_layout()
            self.add_change_code('layout_changed')
            self.add_change_code('pdf_changed')
            if self.zoom_manager.get_zoom_level() == None:
                self.zoom_manager.set_zoom_fit_to_width()

    def reset_pdf_data(self):
        self.pdf_filename = None
        self.poppler_document = None
        self.page_width = None
        self.page_height = None
        self.layout = None
        self.zoom_manager.update_dynamic_zoom_levels()
        self.add_change_code('pdf_changed')

    def update_vertical_margin(self):
        current_min = self.page_width
        for page_number in range(0, min(self.poppler_document.get_n_pages(), 3)):
            page = self.poppler_document.get_page(page_number)
            layout = page.get_text_layout()
            for rect in layout[1]:
                if rect.x1 < current_min:
                    current_min = rect.x1
        current_min -= 20
        self.vertical_margin = current_min

    def open_external_viewer(self):
        if self.pdf_filename != None:
            Gio.AppInfo.launch_default_for_uri('file:' + self.pdf_filename)

    def scroll_to_position(self, x, y):
        if self.layout == None: return

        self.view.content.scroll_to_position([x, y])

    def scroll_dest_on_screen(self, dest):
        if self.layout == None: return

        page_number = dest.page_num
        content = self.view.content
        left = dest.left * self.layout.scale_factor
        top = dest.top * self.layout.scale_factor
        x = max(min(left, content.scrolling_offset_x), content.scrolling_offset_x + content.width)
        y = (self.layout.page_height + self.layout.page_gap) * (page_number) - top - self.layout.page_gap

        self.view.content.scroll_to_position([x, y])

    def update_position(self):
        if self.layout == None: return

        self.add_change_code('position_changed')

    def set_synctex_rectangles(self, rectangles):
        if self.layout == None: return

        self.visible_synctex_rectangles = rectangles
        self.layouter.update_synctex_rectangles(self.layout)
        self.visible_synctex_rectangles_time = time.time()

        if len(rectangles) > 0:
            content = self.view.content
            position = rectangles[0]
            window_width = self.view.get_allocated_width()
            page_number = position['page']
            left = position['h'] * self.layout.scale_factor
            top = position['v'] * self.layout.scale_factor
            width = position['width'] * self.layout.scale_factor
            height = position['height'] * self.layout.scale_factor

            x = max(min(left - 18, content.scrolling_offset_x), left + width - content.width + 18)
            y = (self.layout.page_height + self.layout.page_gap) * (page_number - 1) + max(0, top - height / 2 - content.height * 0.3)

            content.scroll_to_position([x, y])
            self.presenter.start_fade_loop()



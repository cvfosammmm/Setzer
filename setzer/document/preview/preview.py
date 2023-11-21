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
import setzer.document.preview.context_menu.context_menu as context_menu
from setzer.helpers.observable import Observable
from setzer.helpers.timer import timer


class Preview(Observable):

    def __init__(self, document):
        Observable.__init__(self)
        self.document = document

        self.pdf_filename = None
        self.recolor_pdf = self.document.settings.get_value('preferences', 'recolor_pdf')

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
        self.context_menu = context_menu.ContextMenu(self, self.view)

        self.document.connect('filename_change', self.on_filename_change)
        self.document.connect('pdf_updated', self.on_pdf_updated)

        self.document.settings.connect('settings_changed', self.on_settings_changed)

    def on_settings_changed(self, settings, parameter):
        section, item, value = parameter

        if item == 'recolor_pdf':
            self.recolor_pdf = value
            self.add_change_code('recolor_pdf_changed')
            self.view.drawing_area.queue_draw()

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

    def get_pdf_date(self):
        if self.pdf_filename != None:
            return os.path.getmtime(self.pdf_filename)
        else:
            return None

    def load_pdf(self):
        try:
            self.poppler_document = Poppler.Document.new_from_file(GLib.filename_to_uri(self.pdf_filename))
        except Exception:
            self.reset_pdf_data()
            return

        page_size = self.poppler_document.get_page(0).get_size()
        self.page_width = page_size.width
        self.page_height = page_size.height
        self.update_vertical_margin()
        self.layout = None
        self.add_change_code('pdf_changed')
        self.add_change_code('layout_changed')

    def reset_pdf_data(self):
        self.pdf_filename = None
        self.poppler_document = None
        self.page_width = None
        self.page_height = None
        self.layout = None
        self.add_change_code('pdf_changed')
        self.add_change_code('layout_changed')

    def setup_layout_and_zoom_levels(self):
        self.zoom_manager.update_dynamic_zoom_levels()
        if self.zoom_manager.get_zoom_level() == None:
            self.zoom_manager.set_zoom_fit_to_width()

        self.layout = self.layouter.create_layout()
        self.add_change_code('layout_changed')

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

    def init_backward_sync(self, x_offset, y_offset):
        if self.layout == None: return False

        window_width = self.view.get_allocated_width()
        y_total_pixels = min(max(y_offset, 0), (self.layout.page_height + self.layout.page_gap) * self.poppler_document.get_n_pages() - self.layout.page_gap)
        x_pixels = min(max(x_offset - self.layout.get_horizontal_margin(window_width), 0), self.layout.page_width)
        page = math.floor(y_total_pixels / (self.layout.page_height + self.layout.page_gap))
        y_pixels = min(max(y_total_pixels - page * (self.layout.page_height + self.layout.page_gap), 0), self.layout.page_height)
        x = x_pixels / self.layout.scale_factor
        y = y_pixels / self.layout.scale_factor
        page += 1

        poppler_page = self.poppler_document.get_page(page - 1)
        rect = Poppler.Rectangle()
        rect.x1 = max(min(x, self.page_width), 0)
        rect.y1 = max(min(y, self.page_height), 0)
        rect.x2 = max(min(x, self.page_width), 0)
        rect.y2 = max(min(y, self.page_height), 0)
        word = poppler_page.get_selected_text(Poppler.SelectionStyle.WORD, rect)
        context = poppler_page.get_selected_text(Poppler.SelectionStyle.LINE, rect)
        self.document.build_system.backward_sync(page, x, y, word, context)



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
from gi.repository import Gdk
from gi.repository import GObject
import cairo

import _thread as thread, queue
import time
import copy

from setzer.helpers.observable import Observable


class PreviewPageRenderer(Observable):

    def __init__(self, preview, layouter):
        Observable.__init__(self)
        self.preview = preview
        self.layouter = layouter

        self.visible_pages_lock = thread.allocate_lock()
        self.visible_pages = list()
        self.page_width = None
        self.pdf_date = None
        self.rendered_pages = dict()

        self.preview.register_observer(self)
        self.layouter.register_observer(self)

        self.page_render_count = dict()
        self.page_render_count_lock = thread.allocate_lock()
        self.render_queue = queue.Queue()
        self.rendered_pages_queue = queue.Queue()
        thread.start_new_thread(self.render_page_loop, ())
        GObject.timeout_add(50, self.rendered_pages_loop)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code in ['layout_changed', 'position_changed']:
            if self.layouter.has_layout:
                self.update_rendered_pages()
            else:
                self.rendered_pages = dict()

    def render_page_loop(self):
        while True:
            try: todo = self.render_queue.get(block=False)
            except queue.Empty: time.sleep(0.05)
            else:
                with self.visible_pages_lock:
                    visible_pages = self.visible_pages.copy()
                with self.page_render_count_lock:
                    render_count = self.page_render_count[todo['page_number']]
                if todo['render_count'] == render_count and todo['page_number'] in visible_pages:
                    with self.preview.poppler_document_lock:
                        page = self.preview.poppler_document.get_page(todo['page_number'])
                        page.render(todo['ctx'])
                    self.rendered_pages_queue.put({'page_number': todo['page_number'], 'item': [todo['surface'], todo['page_width'], todo['pdf_date']]})

    def rendered_pages_loop(self):
        while self.rendered_pages_queue.empty() == False:
            try: todo = self.rendered_pages_queue.get(block=False)
            except queue.Empty: pass
            else:
                self.rendered_pages[todo['page_number']] = todo['item']
                self.add_change_code('rendered_pages_changed')
        return True

    def update_rendered_pages(self):
        visible_pages = self.layouter.get_visible_pages()
        page_width = self.layouter.page_width
        pdf_date = self.preview.pdf_date
        if pdf_date == self.pdf_date and visible_pages == self.visible_pages and page_width == self.page_width: return
        with self.visible_pages_lock:
            self.visible_pages = visible_pages
        self.page_width = page_width
        self.pdf_date = pdf_date

        changed = False
        '''for page_number in list(self.rendered_pages):
            if page_number not in visible_pages:
                del(self.rendered_pages[page_number])
                changed = True
            elif self.rendered_pages[page_number][2] != pdf_date:
                del(self.rendered_pages[page_number])
                changed = True
        if changed:
            self.add_change_code('rendered_pages_changed')'''

        for page_number in visible_pages:
            if page_number not in self.rendered_pages or self.rendered_pages[page_number][1] != page_width or self.rendered_pages[page_number][2] != pdf_date:
                width_pixels = self.layouter.page_width
                height_pixels = self.layouter.page_height
                scale_factor = self.layouter.scale_factor
                surface = cairo.ImageSurface(cairo.Format.ARGB32, width_pixels, height_pixels)
                ctx = cairo.Context(surface)
                ctx.scale(scale_factor, scale_factor)

                with self.page_render_count_lock:
                    try:
                        self.page_render_count[page_number] += 1
                    except KeyError:
                        self.page_render_count[page_number] = 1
                    self.render_queue.put({'page_number': page_number, 'render_count': self.page_render_count[page_number], 'surface': surface, 'ctx': ctx, 'page_width': page_width, 'pdf_date': pdf_date})



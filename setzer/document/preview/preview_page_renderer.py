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
from gi.repository import GObject
import cairo

import _thread as thread, queue
import time
import math

from setzer.helpers.observable import Observable


class PreviewPageRenderer(Observable):

    def __init__(self, preview, layouter):
        Observable.__init__(self)
        self.preview = preview
        self.layouter = layouter
        self.maximum_rendered_pixels = 20000000

        self.visible_pages_lock = thread.allocate_lock()
        self.visible_pages = list()
        self.page_width = None
        self.pdf_date = None
        self.rendered_pages = dict()
        self.is_active_lock = thread.allocate_lock()
        self.is_active = False

        self.preview.connect('position_changed', self.on_layout_or_position_changed)
        self.layouter.connect('layout_changed', self.on_layout_or_position_changed)

        self.page_render_count_lock = thread.allocate_lock()
        self.page_render_count = dict()
        self.render_queue = queue.Queue()
        self.render_queue_low_priority = queue.Queue()
        self.rendered_pages_queue = queue.Queue()
        thread.start_new_thread(self.render_page_loop, ())
        GObject.timeout_add(50, self.rendered_pages_loop)

    def on_layout_or_position_changed(self, notifying_object):
        if self.layouter.has_layout:
            self.update_rendered_pages()
        else:
            self.rendered_pages = dict()

    def activate(self):
        with self.is_active_lock:
            self.is_active = True
        self.update_rendered_pages()

    def deactivate(self):
        with self.is_active_lock:
            self.is_active = False
        self.rendered_pages = dict()
        with self.visible_pages_lock:
            self.visible_pages = list()
        self.page_width = None
        self.pdf_date = None

    def render_page_loop(self):
        while True:
            with self.is_active_lock:
                is_active = self.is_active
            if is_active:
                try: todo = self.render_queue.get(block=False)
                except queue.Empty:
                    try: todo = self.render_queue_low_priority.get(block=False)
                    except queue.Empty:
                        todo = None
                        time.sleep(0.05)
                if todo != None:
                    with self.page_render_count_lock:
                        render_count = self.page_render_count[todo['page_number']]
                    with self.visible_pages_lock:
                        is_visible = (todo['page_number'] >= self.visible_pages_additional[0] and todo['page_number'] <= self.visible_pages_additional[1])
                    if todo['render_count'] == render_count and is_visible:
                        surface = cairo.ImageSurface(cairo.Format.ARGB32, todo['page_width'] * todo['hidpi_factor'], todo['page_height'] * 2)
                        ctx = cairo.Context(surface)
                        ctx.scale(todo['scale_factor'] * todo['hidpi_factor'], todo['scale_factor'] * todo['hidpi_factor'])
                        page = self.preview.poppler_document.get_page(todo['page_number'])
                        page.render(ctx)
                        self.rendered_pages_queue.put({'page_number': todo['page_number'], 'item': [surface, todo['page_width'], todo['pdf_date']]})
            else:
                time.sleep(0.05)

    def rendered_pages_loop(self):
        with self.is_active_lock:
            is_active = self.is_active
        if not is_active: return True

        changed = False
        while self.rendered_pages_queue.empty() == False:
            try: todo = self.rendered_pages_queue.get(block=False)
            except queue.Empty: pass
            else:
                try:
                    del(self.rendered_pages[todo['page_number']])
                except KeyError: pass
                self.rendered_pages[todo['page_number']] = todo['item']
                changed = True
        if changed:
            self.add_change_code('rendered_pages_changed')
        return True

    def update_rendered_pages(self):
        with self.is_active_lock:
            is_active = self.is_active
        if not is_active: return
        if not self.layouter.has_layout: return

        hidpi_factor = self.layouter.hidpi_factor
        page_width = self.layouter.page_width
        page_height = self.layouter.page_height

        current_page = self.layouter.get_current_page() - 1

        visible_pages = [current_page, min(current_page + math.floor(self.preview.view.get_allocated_height() / page_height) + 1, self.preview.number_of_pages - 1)]

        max_additional_pages = max(math.floor(self.maximum_rendered_pixels / (page_width * page_height * hidpi_factor * hidpi_factor) - visible_pages[1] + visible_pages[0]), 0)
        visible_pages_additional = [max(int(visible_pages[0] - max_additional_pages / 2), 0), min(int(visible_pages[1] + max_additional_pages / 2), self.preview.number_of_pages - 1)]

        pdf_date = self.preview.pdf_date
        with self.visible_pages_lock:
            if pdf_date == self.pdf_date and visible_pages == self.visible_pages and visible_pages_additional == self.visible_pages_additional and page_width == self.page_width:
                do_return = True
            else:
                do_return = False
        if do_return: return
        with self.visible_pages_lock:
            self.visible_pages = visible_pages
            self.visible_pages_additional = visible_pages_additional
        self.page_width = page_width
        self.pdf_date = pdf_date

        changed = False
        for page_number in list(self.rendered_pages):
            if self.rendered_pages[page_number][2] != pdf_date or page_number < visible_pages_additional[0] or page_number > visible_pages_additional[1]:
                del(self.rendered_pages[page_number])
                changed = True
        if changed:
            self.add_change_code('rendered_pages_changed')

        scale_factor = self.layouter.scale_factor

        for page_number in range(0, self.preview.number_of_pages):
            if page_number not in self.rendered_pages or self.rendered_pages[page_number][1] != page_width or self.rendered_pages[page_number][2] != pdf_date:
                with self.page_render_count_lock:
                    try:
                        self.page_render_count[page_number] += 1
                    except KeyError:
                        self.page_render_count[page_number] = 1
                    if visible_pages != None and page_number >= visible_pages[0] and page_number <= visible_pages[1]:
                        self.render_queue.put({'page_number': page_number, 'render_count': self.page_render_count[page_number], 'scale_factor': scale_factor, 'hidpi_factor': hidpi_factor, 'page_width': page_width, 'page_height': page_height, 'pdf_date': pdf_date})
                    elif page_number >= visible_pages_additional[0] and page_number <= visible_pages_additional[1]:
                        self.render_queue_low_priority.put({'page_number': page_number, 'render_count': self.page_render_count[page_number], 'scale_factor': scale_factor, 'hidpi_factor': hidpi_factor, 'page_width': page_width, 'page_height': page_height, 'pdf_date': pdf_date})



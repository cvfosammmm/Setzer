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
gi.require_version('Gtk', '4.0')
from gi.repository import GObject, Gdk
import cairo

import _thread as thread, queue
import time
import math
import numpy as np
from PIL import Image, ImageFilter

from setzer.app.color_manager import ColorManager
from setzer.helpers.observable import Observable


class PreviewPageRenderer(Observable):

    def __init__(self, preview):
        Observable.__init__(self)
        self.preview = preview
        self.maximum_rendered_pixels = 20000000

        self.visible_pages_lock = thread.allocate_lock()
        self.visible_pages = list()
        self.page_width = None
        self.pdf_date = None
        self.rendered_pages = dict()
        self.is_active_lock = thread.allocate_lock()
        self.is_active = False

        self.preview.connect('position_changed', self.on_layout_or_position_changed)
        self.preview.connect('layout_changed', self.on_layout_or_position_changed)
        self.preview.connect('recolor_pdf_changed', self.on_recolor_pdf_changed)
        self.preview.document.settings.connect('settings_changed', self.on_settings_changed)

        self.page_render_count_lock = thread.allocate_lock()
        self.page_render_count = dict()
        self.render_queue = queue.Queue()
        self.render_queue_low_priority = queue.Queue()
        self.rendered_pages_queue = queue.Queue()
        thread.start_new_thread(self.render_page_loop, ())
        GObject.timeout_add(50, self.rendered_pages_loop)

    def on_layout_or_position_changed(self, notifying_object):
        if self.preview.layout != None:
            self.update_rendered_pages()
        else:
            self.rendered_pages = dict()

    def on_recolor_pdf_changed(self, preview):
        self.update_rendered_pages()

    def on_settings_changed(self, settings, parameter):
        section, item, value = parameter

        if item == 'color_scheme':
            self.update_rendered_pages()

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
            todo = None
            if is_active:
                try: todo = self.render_queue.get(block=False)
                except queue.Empty:
                    try: todo = self.render_queue_low_priority.get(block=False)
                    except queue.Empty:
                        todo = None
            if todo != None:
                with self.page_render_count_lock:
                    render_count = self.page_render_count[todo['page_number']]
                with self.visible_pages_lock:
                    is_visible = (todo['page_number'] >= self.visible_pages_additional[0] and todo['page_number'] <= self.visible_pages_additional[1])
                if todo['render_count'] == render_count and is_visible:
                    colors = todo['matching_theme_colors']
                    width = todo['page_width'] * todo['hidpi_factor']
                    height = todo['page_height'] * 2
                    surface = cairo.ImageSurface(cairo.Format.ARGB32, width, height)
                    ctx = cairo.Context(surface)

                    ctx.set_source_rgba(1, 1, 1, 1)
                    ctx.rectangle(0, 0, width, height)
                    ctx.fill()

                    ctx.scale(todo['scale_factor'] * todo['hidpi_factor'], todo['scale_factor'] * todo['hidpi_factor'])
                    page = self.preview.poppler_document.get_page(todo['page_number'])
                    page.render(ctx)

                    if colors != None:
                        pil_img = Image.frombuffer("RGBA", (width, height), surface.get_data(), "raw", "RGBA", 0, 1)

                        img_data = np.array(pil_img, dtype=np.ubyte)
                        alpha = 255 - 0.3 * img_data[..., 0] - 0.6 * img_data[..., 1] - 0.1 * img_data[..., 2]
                        img_data[:,:,-1] = alpha
                        pil_img = Image.fromarray(np.ubyte(img_data))

                        im_bytes = bytearray(pil_img.tobytes('raw', 'BGRa'))
                        surface = cairo.ImageSurface.create_for_data(im_bytes, cairo.FORMAT_ARGB32, width, height)
                        temp_ctx = cairo.Context(surface)

                        Gdk.cairo_set_source_rgba(temp_ctx, colors[0])
                        temp_ctx.set_operator(cairo.Operator.IN)
                        temp_ctx.rectangle(0, 0, width, height)
                        temp_ctx.fill()

                    self.rendered_pages_queue.put({'page_number': todo['page_number'], 'item': [surface, todo['page_width'], todo['pdf_date'], colors]})
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
        if self.preview.layout == None: return

        hidpi_factor = self.preview.layout.hidpi_factor
        page_width = int(self.preview.layout.page_width)
        page_height = int(self.preview.layout.page_height)

        offset = self.preview.view.content.scrolling_offset_y
        current_page = self.preview.layout.get_page_by_offset(offset) - 1

        visible_pages = [current_page, min(current_page + math.floor(self.preview.view.get_allocated_height() / page_height) + 1, self.preview.poppler_document.get_n_pages() - 1)]

        max_additional_pages = max(math.floor(self.maximum_rendered_pixels / (page_width * page_height * hidpi_factor * hidpi_factor) - visible_pages[1] + visible_pages[0]), 0)
        visible_pages_additional = [max(int(visible_pages[0] - max_additional_pages / 2), 0), min(int(visible_pages[1] + max_additional_pages / 2), self.preview.poppler_document.get_n_pages() - 1)]

        pdf_date = self.preview.get_pdf_date()
        with self.visible_pages_lock:
            self.visible_pages = visible_pages
            self.visible_pages_additional = visible_pages_additional
        self.page_width = page_width
        self.pdf_date = pdf_date

        if self.preview.recolor_pdf:
            colors = (ColorManager.get_ui_color('view_fg_color'), ColorManager.get_ui_color('view_bg_color'))
        else:
            colors = None

        changed = False
        for page_number in list(self.rendered_pages):
            if self.rendered_pages[page_number][3] == None and colors == None:
                colors_changed = False
            elif self.rendered_pages[page_number][3] == None and colors != None:
                colors_changed = True
            elif self.rendered_pages[page_number][3] != None and colors == None:
                colors_changed = True
            elif not self.rendered_pages[page_number][3][0].equal(colors[0]):
                colors_changed = True
            elif not self.rendered_pages[page_number][3][1].equal(colors[1]):
                colors_changed = True
            else:
                colors_changed = False

            if self.rendered_pages[page_number][2] != pdf_date or colors_changed or page_number < visible_pages_additional[0] or page_number > visible_pages_additional[1]:
                del(self.rendered_pages[page_number])
                changed = True
        if changed:
            self.add_change_code('rendered_pages_changed')

        scale_factor = self.preview.layout.scale_factor

        for page_number in range(0, self.preview.poppler_document.get_n_pages()):
            if page_number not in self.rendered_pages or self.rendered_pages[page_number][1] != page_width or self.rendered_pages[page_number][2] != pdf_date:
                with self.page_render_count_lock:
                    try:
                        self.page_render_count[page_number] += 1
                    except KeyError:
                        self.page_render_count[page_number] = 1

                    render_task = dict()
                    render_task['page_number'] = page_number
                    render_task['render_count'] = self.page_render_count[page_number]
                    render_task['scale_factor'] = scale_factor
                    render_task['hidpi_factor'] = hidpi_factor
                    render_task['page_width'] = page_width
                    render_task['page_height'] = page_height
                    render_task['pdf_date'] = pdf_date
                    render_task['matching_theme_colors'] = colors

                    if visible_pages != None and page_number >= visible_pages[0] and page_number <= visible_pages[1]:
                        self.render_queue.put(render_task)
                    elif page_number >= visible_pages_additional[0] and page_number <= visible_pages_additional[1]:
                        self.render_queue_low_priority.put(render_task)



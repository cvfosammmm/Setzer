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
from gi.repository import Gdk

import webbrowser
import _thread as thread

from setzer.app.service_locator import ServiceLocator


class PreviewController(object):

    def __init__(self, preview, view):
        self.preview = preview
        self.view = view

        self.zoom_buffer = 1
        self.label_height = 0

        self.cursor_default = Gdk.Cursor.new_from_name('default')
        self.cursor_pointer = Gdk.Cursor.new_from_name('pointer')

        self.view.content.connect('size_changed', self.on_size_change)
        self.view.content.connect('scrolling_offset_changed', self.on_scrolling_offset_change)
        self.view.content.connect('hover_state_changed', self.on_hover_state_change)
        self.view.content.connect('primary_button_press', self.on_primary_button_press)
        self.view.content.connect('zoom_request', self.on_zoom_request)

    def on_size_change(self, *arguments):
        self.preview.zoom_manager.update_dynamic_zoom_levels()
        self.update_cursor()

    def on_scrolling_offset_change(self, *arguments):
        self.preview.update_position()
        self.update_cursor()

    def on_zoom_request(self, content, amount):
        self.preview.update_position()

        layout = self.preview.layout
        manager = self.preview.zoom_manager

        gap = 1.25
        stopping_points = []
        if manager.zoom_level_fit_to_width != None:
            stopping_points.append(manager.zoom_level_fit_to_width)
        if manager.zoom_level_fit_to_text_width != None:
            stopping_points.append(manager.zoom_level_fit_to_text_width)
        if manager.zoom_level_fit_to_height != None:
            stopping_points.append(manager.zoom_level_fit_to_height)

        prev_zoom_level = manager.get_zoom_level()
        if prev_zoom_level in stopping_points:
            if amount <= 0:
                self.zoom_buffer *= (1 - amount)
                amount = max(1, self.zoom_buffer / gap)
                zoom_level = min(max(prev_zoom_level * amount, 0.25), 4)
            elif amount > 0:
                self.zoom_buffer *= (1 - amount)
                amount = min(1, self.zoom_buffer * gap)
                zoom_level = min(max(prev_zoom_level * amount, 0.25), 4)
        else:
            zoom_level = min(max(prev_zoom_level * (1 - amount), 0.25), 4)
            if amount <= 0:
                for level in stopping_points:
                    if prev_zoom_level < level and zoom_level >= level:
                        zoom_level = level
                        self.zoom_buffer = 1 / gap
            if amount > 0:
                for level in stopping_points:
                    if prev_zoom_level > level and zoom_level <= level:
                        zoom_level = level
                        self.zoom_buffer = 1 * gap

        factor = zoom_level / manager.zoom_level
        x = factor * self.view.content.scrolling_offset_x + (factor - 1) * self.view.content.cursor_x
        prev_pages = self.view.content.scrolling_offset_y // (layout.page_height + layout.page_gap)
        y = (1 - factor) * prev_pages * layout.page_gap + factor * self.view.content.scrolling_offset_y + (factor - 1) * self.view.content.cursor_y
        manager.set_zoom_level(zoom_level)
        self.preview.scroll_to_position(x, y)

    def on_hover_state_change(self, *arguments):
        self.update_cursor()

    def update_cursor(self):
        if self.preview.layout == None: return True

        content = self.view.content
        x_offset = content.scrolling_offset_x + (content.cursor_x if content.cursor_x != None else 0)
        y_offset = content.scrolling_offset_y + (content.cursor_y if content.cursor_y != None else 0)

        window_width = content.width
        data = self.preview.layout.get_page_number_and_offsets_by_document_offsets(x_offset, y_offset, window_width)
        if data == None: return True

        page_number, x_offset, y_offset = data
        cursor = self.cursor_default
        link_target = ''
        links = self.preview.links_parser.get_links_for_page(page_number)
        y_offset = (self.preview.page_height - y_offset)
        for link in links:
            if x_offset > link[0].x1 and x_offset < link[0].x2 and y_offset > link[0].y1 and y_offset < link[0].y2:
                cursor = self.cursor_pointer
                self.label_height = max(self.view.target_label.get_allocated_height(), self.label_height)
                if self.view.overlay.get_allocated_height() - content.cursor_y <= self.label_height:
                    link_target = ''
                elif link[2] == 'uri':
                    link_target = link[1]
                elif link[2] == 'goto':
                    link_target = _('Go to page ') + str(link[1].page_num)
                break

        self.view.set_cursor(cursor)
        self.view.set_link_target_string(link_target)

    def on_primary_button_press(self, content, data):
        if self.preview.layout == None: return True

        x_offset, y_offset, state = data

        if state == Gdk.ModifierType.CONTROL_MASK:
            self.preview.init_backward_sync(x_offset, y_offset)
            return True

        if state == 0:
            window_width = content.width
            data = self.preview.layout.get_page_number_and_offsets_by_document_offsets(x_offset, y_offset, window_width)
            if data == None: return True

            page_number, x_offset, y_offset = data
            links = self.preview.links_parser.get_links_for_page(page_number)
            y_offset = self.preview.page_height - y_offset
            for link in links:
                if x_offset > link[0].x1 and x_offset < link[0].x2 and y_offset > link[0].y1 and y_offset < link[0].y2:
                    if link[2] == 'goto':
                        self.preview.scroll_dest_on_screen(link[1])
                        return True
                    elif link[2] == 'uri':
                        thread.start_new_thread(webbrowser.open_new_tab, (link[1],))
                        return True
            return True



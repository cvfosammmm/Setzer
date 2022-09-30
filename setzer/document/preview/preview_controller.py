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
gi.require_version('Gtk', '3.0')
from gi.repository import Poppler
from gi.repository import Gdk
from gi.repository import Gtk

import math
import webbrowser
import _thread as thread


class PreviewController(object):

    def __init__(self, preview, view):
        self.preview = preview
        self.view = view

        self.zoom_momentum = 0
        self.context_menu_popup_button_event = None

        display = self.view.scrolled_window.get_display()
        self.cursor_default = Gdk.Cursor.new_from_name(display, 'default')
        self.cursor_pointer = Gdk.Cursor.new_from_name(display, 'pointer')

        self.view.connect('size-allocate', self.on_size_allocate)
        self.view.scrolled_window.get_hadjustment().connect('value-changed', self.on_hadjustment_changed)
        self.view.scrolled_window.get_vadjustment().connect('value-changed', self.on_vadjustment_changed)
        self.view.scrolled_window.connect('scroll-event', self.on_scroll)
        self.view.drawing_area.connect('button-press-event', self.on_button_press)
        self.view.scrolled_window.connect('enter-notify-event', self.on_enter)
        self.view.scrolled_window.connect('motion-notify-event', self.on_hover)
        self.view.scrolled_window.connect('leave-notify-event', self.on_leave)
        self.view.external_viewer_button.connect('clicked', self.on_external_viewer_button_clicked)

        def zoom_in(menu_item): self.preview.zoom_manager.zoom_in()
        self.view.menu_item_zoom_in.connect('activate', zoom_in)

        def zoom_out(menu_item): self.preview.zoom_manager.zoom_out()
        self.view.menu_item_zoom_out.connect('activate', zoom_out)

        def zoom_fit_to_width(menu_item): self.preview.zoom_manager.set_zoom_fit_to_width_auto_offset()
        self.view.menu_item_zoom_fit_to_width.connect('activate', zoom_fit_to_width)

        def zoom_fit_to_text_width(menu_item): self.preview.zoom_manager.set_zoom_fit_to_text_width()
        self.view.menu_item_zoom_fit_to_text_width.connect('activate', zoom_fit_to_text_width)

        def zoom_fit_to_height(menu_item): self.preview.zoom_manager.set_zoom_fit_to_height()
        self.view.menu_item_zoom_fit_to_height.connect('activate', zoom_fit_to_height)

        def backward_sync(menu_item):
            event = self.context_menu_popup_button_event
            if event != None:
                self.init_backward_sync(event)
        self.view.menu_item_backward_sync.connect('activate', backward_sync)

    def on_scroll(self, widget, event):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if event.state & modifiers == Gdk.ModifierType.CONTROL_MASK:
            if event.delta_y != event.delta_x:
                self.zoom_momentum += event.delta_y - event.delta_x
                if(self.preview.presenter.scrolling_queue.empty()):
                    zoom_level = min(max(self.preview.zoom_manager.get_zoom_level() * (1 - 0.1 * self.zoom_momentum), 0.25), 4)
                    xoffset = (-event.x + event.x * zoom_level / self.preview.zoom_manager.get_zoom_level()) / (zoom_level * self.preview.layout.hidpi_factor)
                    yoffset = (-event.y + event.y * zoom_level / self.preview.zoom_manager.get_zoom_level()) / (zoom_level * self.preview.layout.hidpi_factor)
                    self.preview.zoom_manager.set_zoom_level(zoom_level)
                    self.preview.scroll_by_offsets(xoffset, yoffset)
                    self.zoom_momentum = 0
            return True
        return False

    def on_enter(self, widget, event):
        self.update_cursor(event)

    def on_hover(self, widget, event):
        self.update_cursor(event)

    def on_leave(self, widget, event):
        self.update_cursor(event)

    def update_cursor(self, event):
        if self.preview.layout == None: return True

        x_offset = event.x + self.view.scrolled_window.get_hadjustment().get_value()
        y_offset = event.y + self.view.scrolled_window.get_vadjustment().get_value()

        window_width = self.view.get_allocated_width()
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
                if link[2] == 'uri':
                    link_target = link[1]
                elif link[2] == 'goto':
                    link_target = _('Go to page ') + str(link[1].page_num)
                break

        window = self.view.scrolled_window.get_window()
        window.set_cursor(cursor)
        self.view.set_link_target_string(link_target)

    def on_size_allocate(self, view=None, allocation=None):
        self.preview.zoom_manager.update_dynamic_zoom_levels()

    def on_hadjustment_changed(self, adjustment):
        self.preview.update_position()

    def on_vadjustment_changed(self, adjustment):
        self.preview.update_position()

    def on_button_press(self, widget, event):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.view.context_menu.show_all()
            self.view.context_menu.popup_at_pointer(event)
            self.context_menu_popup_button_event = event
            return True
        elif event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1 and event.state & modifiers == Gdk.ModifierType.CONTROL_MASK:
            self.init_backward_sync(event)
            return True
        elif event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1 and event.state & modifiers == 0:
            x_offset = event.x
            y_offset = event.y
            window_width = self.view.get_allocated_width()
            data = self.preview.layout.get_page_number_and_offsets_by_document_offsets(x_offset, y_offset, window_width)
            if data == None: return True

            page_number, x_offset, y_offset = data
            links = self.preview.links_parser.get_links_for_page(page_number)
            y_offset = (self.preview.page_height - y_offset)
            for link in links:
                if x_offset > link[0].x1 and x_offset < link[0].x2 and y_offset > link[0].y1 and y_offset < link[0].y2:
                    if link[2] == 'goto':
                        self.preview.scroll_dest_on_screen(link[1])
                        return True
                    elif link[2] == 'uri':
                        thread.start_new_thread(webbrowser.open_new_tab, (link[1],))

            return True

    def on_external_viewer_button_clicked(self, button):
        self.preview.open_external_viewer()

    def init_backward_sync(self, event):
        if self.preview.layout == None: return False

        window_width = self.view.get_allocated_width()
        y_total_pixels = min(max(event.y, 0), (self.preview.layout.page_height + self.preview.layout.page_gap) * self.preview.poppler_document.get_n_pages() - self.preview.layout.page_gap)
        x_pixels = min(max(event.x - self.preview.layout.get_horizontal_margin(window_width), 0), self.preview.layout.page_width)
        page = math.floor(y_total_pixels / (self.preview.layout.page_height + self.preview.layout.page_gap))
        y_pixels = min(max(y_total_pixels - page * (self.preview.layout.page_height + self.preview.layout.page_gap), 0), self.preview.layout.page_height)
        x = x_pixels / self.preview.layout.scale_factor
        y = y_pixels / self.preview.layout.scale_factor
        page += 1

        poppler_page = self.preview.poppler_document.get_page(page - 1)
        rect = Poppler.Rectangle()
        rect.x1 = max(min(x, self.preview.page_width), 0)
        rect.y1 = max(min(y, self.preview.page_height), 0)
        rect.x2 = max(min(x, self.preview.page_width), 0)
        rect.y2 = max(min(y, self.preview.page_height), 0)
        word = poppler_page.get_selected_text(Poppler.SelectionStyle.WORD, rect)
        context = poppler_page.get_selected_text(Poppler.SelectionStyle.LINE, rect)
        self.preview.document.build_system.backward_sync(page, x, y, word, context)



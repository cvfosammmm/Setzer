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
from gi.repository import Gtk, Gdk, Gio, GLib, GObject

import setzer.workspace.sidebar.symbols_page.symbols_page_viewgtk as symbols_page_view
from setzer.app.service_locator import ServiceLocator
import setzer.helpers.timer as timer

import math
import time
import xml.etree.ElementTree as ET
import os


class SymbolsPage(object):

    def __init__(self, workspace):
        self.view = symbols_page_view.SymbolsPageView()
        self.workspace = workspace

        self.scroll_to = None

        self.recent = ServiceLocator.get_settings().get_value('app_recent_symbols', 'symbols')
        self.recent_details = list()
        self.recent_view_size = None
        self.update_recent_widget()

        for symbols_list_view in self.view.symbols_views:
            event_controller = Gtk.GestureClick()
            event_controller.set_button(1)
            event_controller.connect('pressed', self.on_flowbox_clicked, symbols_list_view)
            symbols_list_view.add_controller(event_controller)

        self.view.scrolled_window.get_hadjustment().connect('changed', self.on_symbols_view_size_allocate)
        self.view.scrolled_window.get_vadjustment().connect('changed', self.on_scroll_or_resize)
        self.view.scrolled_window.get_vadjustment().connect('value-changed', self.on_scroll_or_resize)
        self.view.next_button.connect('clicked', self.on_next_button_clicked)
        self.view.prev_button.connect('clicked', self.on_prev_button_clicked)
        self.view.search_button.connect('toggled', self.on_search_button_toggled)
        self.view.search_close_button.connect('clicked', self.on_search_close_button_clicked)
        self.view.search_entry.connect('stop_search', self.on_search_stopped)
        self.view.search_entry.connect('changed', self.on_search_changed)

    def update_recent_widget(self):
        for item in [item for item in self.recent]:
            self.add_recent_symbol_to_flowbox(item)
        event_controller = Gtk.GestureClick()
        event_controller.set_button(1)
        event_controller.connect('pressed', self.on_recent_widget_clicked)
        self.view.symbols_view_recent.add_controller(event_controller)

    def on_recent_widget_clicked(self, event_controller, n_press, x, y):
        flowbox = event_controller.get_widget()
        child = flowbox.get_child_at_pos(x, y)
        if child != None and self.workspace.active_document != None:
            text = self.recent_details[- child.get_index() - 1][1]
            self.workspace.actions.insert_symbol(None, [text])
            self.add_recent_symbol(self.recent[- child.get_index() - 1])

        return True

    def remove_recent_symbol(self, item):
        self.recent.remove(item)
        for symbol in [symbol for symbol in self.recent_details]:
            if item[1] == symbol[1]:
                self.view.symbols_view_recent.remove(symbol[5])
                self.recent_details.remove(symbol)

    def add_recent_symbol(self, new_item):
        for item in [item for item in self.recent]:
            if item[1] == new_item[1]:
                self.remove_recent_symbol(item)
        if len(self.recent) >= 20:
            self.remove_recent_symbol(self.recent[0])

        self.recent.append(new_item)
        self.add_recent_symbol_to_flowbox(new_item)

    def add_recent_symbol_to_flowbox(self, item):
        (category, command) = item
        xml_tree = ET.parse(os.path.join(ServiceLocator.get_resources_path(), 'symbols', category + '.xml'))
        xml_root = xml_tree.getroot()
        elements = xml_root.findall('./symbol[@command=\'' + command + '\']')
        if len(elements) == 0:
            self.remove_recent_symbol(item)
        else:
            attrib = elements[0].attrib
            symbol = [attrib['file'].rsplit('.')[0], attrib['command'], attrib.get('package', None), int(attrib.get('original_width', 10)), int(attrib.get('original_height', 10))]
            size = max(symbol[3], symbol[4])

            image = Gtk.Image.new_from_icon_name('sidebar-' + symbol[0] + '-symbolic')
            image.set_pixel_size(int(size * 1.5))
            tooltip_text = symbol[1]
            if symbol[2] != None: 
                tooltip_text += ' (' + _('Package') + ': ' + symbol[2] + ')'
            image.set_tooltip_text(tooltip_text)
            symbol.append(image)
            self.recent_details.append(symbol)

            self.view.symbols_view_recent.insert(image, 0)
            self.view.queue_draw()

    def on_flowbox_clicked(self, event_controller, n_press, x, y, symbols_view):
        flowbox = event_controller.get_widget()
        child = flowbox.get_child_at_pos(x, y)
        if child != None and self.workspace.active_document != None:
            text = symbols_view.visible_symbols[child.get_index()][1]
            self.workspace.actions.insert_symbol(None, [text])
            self.add_recent_symbol((flowbox.symbol_folder, symbols_view.visible_symbols[child.get_index()][1]))

        return True

    def on_scroll_or_resize(self, *args):
        scrolling_offset = self.view.scrolled_window.get_vadjustment().get_value()
        if scrolling_offset == 0:
            self.view.prev_button.set_sensitive(False)
        else:
            self.view.prev_button.set_sensitive(True)

        final_label_offset = self.view.vbox.get_allocated_height() - self.view.symbols_views[-1].get_allocated_height()
        if scrolling_offset >= final_label_offset:
            self.view.next_button.set_sensitive(False)
        elif scrolling_offset >= self.view.vbox.get_allocated_height() - self.view.scrolled_window.get_allocated_height():
            self.view.next_button.set_sensitive(False)
        else:
            self.view.next_button.set_sensitive(True)

        self.update_labels()

    def update_labels(self):
        offset = self.view.symbols_view_recent.get_allocated_height() + self.view.tabs.get_allocated_height() + 1
        scrolling_offset = self.view.scrolled_window.get_vadjustment().get_value()
        self.view.tabs_box.get_style_context().remove_class('no-border')
        for key, symbols_view in enumerate(self.view.symbols_views):
            label = self.view.labels[key]
            placeholder = self.view.placeholders[len(self.view.symbols_views) - key - 1]
            margin_top = max(0, offset - int(scrolling_offset))
            label.set_margin_top(margin_top)
            if margin_top > 1 and margin_top <= label.get_allocated_height():
                self.view.tabs_box.get_style_context().add_class('no-border')
            if len(symbols_view.visible_symbols) > 0:
                offset += symbols_view.get_allocated_height() + self.view.tabs.get_allocated_height()

    def on_next_button_clicked(self, button):
        offset = self.view.symbols_view_recent.get_allocated_height() + self.view.tabs.get_allocated_height() + 1
        scrolling_offset = self.view.scrolled_window.get_vadjustment().get_value()
        if scrolling_offset < offset:
            self.scroll_view(offset)
            return

        for key, symbols_view in enumerate(self.view.symbols_views):
            label = self.view.labels[len(self.view.symbols_views) - key - 1]

            if len(symbols_view.visible_symbols) > 0:
                view_height = (symbols_view.get_allocated_height() + self.view.tabs.get_allocated_height())
            else:
                view_height = 0

            if offset > scrolling_offset - view_height:
                new_offset = offset + (symbols_view.get_allocated_height() + self.view.tabs.get_allocated_height())
                if key < len(self.view.symbols_views) - 1:
                    self.scroll_view(new_offset)
                break
            offset += view_height

    def on_prev_button_clicked(self, button):
        offset = self.view.symbols_view_recent.get_allocated_height() + self.view.tabs.get_allocated_height() + 1
        old_offset = offset
        scrolling_offset = self.view.scrolled_window.get_vadjustment().get_value()

        if scrolling_offset <= offset:
            self.scroll_view(0)
            return

        for key, symbols_view in enumerate(self.view.symbols_views):
            label = self.view.labels[len(self.view.symbols_views) - key - 1]

            if len(symbols_view.visible_symbols) > 0:
                view_height = (symbols_view.get_allocated_height() + self.view.tabs.get_allocated_height())
            else:
                view_height = 0

            if offset > scrolling_offset - view_height:
                if offset == int(scrolling_offset):
                    new_offset = old_offset
                else:
                    new_offset = offset
                self.scroll_view(new_offset)
                break
            old_offset = offset
            offset += view_height

    def on_search_button_toggled(self, button):
        if button.get_active():
            self.view.search_entry.set_text('')
            self.view.search_revealer.set_reveal_child(True)
            self.view.search_entry.grab_focus()
        else:
            self.view.search_entry.set_text('')
            self.view.search_revealer.set_reveal_child(False)
            document = self.workspace.get_active_document()
            if document != None:
                document.source_view.grab_focus()

    def on_search_close_button_clicked(self, button):
        self.view.search_button.set_active(False)

    def on_search_stopped(self, entry):
        self.view.search_button.set_active(False)

    def on_search_changed(self, entry):
        self.update_symbols()

    def update_symbols(self):
        any_symbols_found = False

        search_words = self.view.search_entry.get_text().split()
        for i, symbols_view in enumerate(self.view.symbols_views):
            for symbol in symbols_view.visible_symbols:
                symbols_view.remove(symbol[5])
            symbols_view.visible_symbols = []

            for symbol in symbols_view.symbols:
                image = symbol[5]
                symbol_found = True
                for word in search_words:
                    if symbol[0].find(word) == -1:
                        symbol_found = False
                if symbol_found:
                    symbols_view.visible_symbols.append(symbol)
                    symbols_view.insert(image, -1)

            adjustment = self.view.scrolled_window.get_vadjustment()
            symbols_found = (len(symbols_view.visible_symbols) > 0)
            any_symbols_found |= symbols_found
            symbols_view.set_visible(symbols_found)
            self.view.labels[i].set_visible(symbols_found and (adjustment.get_upper() <= self.view.scrolled_window.get_allocated_height()))
            self.view.placeholders[i].set_visible(symbols_found)
            self.update_borders(symbols_view, symbols_view.get_allocated_width())

        if any_symbols_found:
            self.view.search_entry.get_style_context().remove_class('error')
        else:
            self.view.search_entry.get_style_context().add_class('error')

    def on_symbols_view_size_allocate(self, *arguments):
        for symbols_view in self.view.symbols_views:
            allocation = symbols_view.get_allocation()
            if symbols_view.size != (allocation.width, allocation.height):
                symbols_view.size = (allocation.width, allocation.height)
                self.update_borders(symbols_view, allocation.width)

        view = self.view.symbols_view_recent
        allocation = view.get_allocation()
        if self.recent_view_size != (allocation.width, allocation.height):
            self.recent_view_size = (allocation.width, allocation.height)

            for number, recent_symbol in enumerate(self.recent_details):
                image = recent_symbol[5]
                image.get_style_context().remove_class('no_right_border')

            for offset in range(max(0, allocation.height) // 20 + 1):
                widget = view.get_child_at_pos(allocation.width - 1, offset * 20)
                if widget != None:
                    widget.get_child().get_style_context().add_class('no_right_border')

    def update_borders(self, symbols_view, width_available):
        width_with_border = symbols_view.symbol_width + 11
        symbols_per_line = int((width_available) / width_with_border)

        if symbols_per_line == 0 or len(symbols_view.visible_symbols) == 0:
            return

        for number, image in enumerate(symbols_view.visible_symbols):
            if (number % symbols_per_line) == symbols_per_line - 1:
                image[5].get_style_context().add_class('no_right_border')
            else:
                image[5].get_style_context().remove_class('no_right_border')

    def scroll_view(self, position, duration=0.2):
        adjustment = self.view.scrolled_window.get_vadjustment()
        self.scroll_to = {'position_start': adjustment.get_value(), 'position_end': position, 'time_start': time.time(), 'duration': duration}
        self.view.scrolled_window.set_kinetic_scrolling(False)
        GObject.timeout_add(15, self.do_scroll)

    def do_scroll(self):
        if self.scroll_to != None:
            adjustment = self.view.scrolled_window.get_vadjustment()
            time_elapsed = time.time() - self.scroll_to['time_start']
            if self.scroll_to['duration'] == 0:
                time_elapsed_percent = 1
            else:
                time_elapsed_percent = time_elapsed / self.scroll_to['duration']
            if time_elapsed_percent >= 1:
                adjustment.set_value(self.scroll_to['position_end'])
                self.scroll_to = None
                self.view.scrolled_window.set_kinetic_scrolling(True)
                return False
            else:
                adjustment.set_value(self.scroll_to['position_start'] * (1 - self.ease(time_elapsed_percent)) + self.scroll_to['position_end'] * self.ease(time_elapsed_percent))
                return True
        return False

    def ease(self, time): return (time - 1)**3 + 1



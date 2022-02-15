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
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import GObject

import setzer.workspace.sidebar.sidebar_viewgtk as sidebar_view
from setzer.app.service_locator import ServiceLocator

import math
import time
import xml.etree.ElementTree as ET
import os


class Sidebar(object):
    ''' Init and controll sidebar '''
    
    def __init__(self, workspace):
        self.view = ServiceLocator.get_main_window().sidebar
        self.workspace = workspace

        self.scroll_to = None

        # tabbed pages: name, icon name, tooltip, widget
        self.pages = list()
        self.pages.append(['greek_letters', 'own-symbols-greek-letters-symbolic', _('Greek Letters'), 
                           'sidebar_view.SidebarPageSymbolsList("greek_letters", 25)'])
        self.pages.append(['arrows', 'own-symbols-arrows-symbolic', _('Arrows'), 
                           'sidebar_view.SidebarPageSymbolsList("arrows", 48)'])
        self.pages.append(['relations', 'own-symbols-relations-symbolic', _('Relations'), 
                           'sidebar_view.SidebarPageSymbolsList("relations", 39)'])
        self.pages.append(['operators', 'own-symbols-operators-symbolic', _('Operators'), 
                           'sidebar_view.SidebarPageSymbolsList("operators", 47)'])
        self.pages.append(['misc_math', 'own-symbols-misc-math-symbolic', _('Misc. Math'), 
                           'sidebar_view.SidebarPageSymbolsList("misc_math", 42)'])
        self.pages.append(['misc_text', 'own-symbols-misc-text-symbolic', _('Misc. Symbols'), 
                           'sidebar_view.SidebarPageSymbolsList("misc_text", 38)'])
        self.init_pages()

        self.recent = ServiceLocator.get_settings().get_value('app_recent_symbols', 'symbols')
        self.recent_details = list()
        self.recent_page_size = None
        self.update_recent_widget()

        self.view.show_all()

        self.view.vbox.connect('size-allocate', self.on_scroll_or_resize)
        self.view.scrolled_window.get_vadjustment().connect('value-changed', self.on_scroll_or_resize)
        self.view.next_button.connect('clicked', self.on_next_button_clicked)
        self.view.prev_button.connect('clicked', self.on_prev_button_clicked)

    def init_pages(self):
        for page in reversed(self.pages):
            page_view = eval(page[3])
            label = Gtk.Label(page[2])
            label.set_xalign(0)
            label.set_halign(Gtk.Align.START)
            label.set_valign(Gtk.Align.START)
            label.set_size_request(108, -1)
            label.get_style_context().add_class('overlay')
            self.view.add_overlay(label)
            self.view.reorder_overlay(label, 1)
            self.view.set_overlay_pass_through(label, True)
            self.view.labels.append(label)
            self.view.page_views.append(page_view)
            self.view.vbox.pack_end(page_view, False, False, 0)
            placeholder = Gtk.Label(page[2])
            placeholder.set_xalign(0)
            self.view.vbox.pack_end(placeholder, False, False, 0)
            page_view.connect('size-allocate', self.on_page_size_allocate)
            page_view.connect('button-press-event', self.on_flowbox_clicked, page_view.symbols)
            self.init_symbols_page(page_view)

    def update_recent_widget(self):
        for item in [item for item in self.recent]:
            self.add_recent_symbol_to_flowbox(item)
        self.view.page_view_recent.connect('button-press-event', self.on_recent_widget_clicked)
        self.view.page_view_recent.connect('size-allocate', self.on_recent_page_size_allocate)

    def on_recent_widget_clicked(self, flowbox, event):
        if event.button != 1: return

        child = flowbox.get_child_at_pos(event.x, event.y)

        if child != None and self.workspace.active_document != None:
            self.workspace.get_active_document().content.insert_text_at_cursor(self.recent_details[- child.get_index() - 1][1])
            self.workspace.get_active_document().content.scroll_cursor_onscreen()
            self.add_recent_symbol(self.recent[- child.get_index() - 1])

        return True

    def remove_recent_symbol(self, item):
        self.recent.remove(item)
        for symbol in [symbol for symbol in self.recent_details]:
            if item[1] == symbol[1]:
                self.view.page_view_recent.remove(symbol[5])
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

            image = Gtk.Image.new_from_icon_name('sidebar-' + symbol[0] + '-symbolic', 0)
            image.set_pixel_size(int(size * 1.5))
            tooltip_text = symbol[1]
            if symbol[2] != None: 
                tooltip_text += ' (' + _('Package') + ': ' + symbol[2] + ')'
            image.set_tooltip_text(tooltip_text)
            image.show_all()
            symbol.append(image)
            self.recent_details.append(symbol)

            self.view.page_view_recent.insert(image, 0)
            self.view.queue_draw()

    def init_symbols_page(self, page_view):
        for symbol in page_view.symbols:
            image = symbol[5]
            image.set_size_request(page_view.symbol_width + 11, -1)

    def on_scroll_or_resize(self, *args):
        scrolling_offset = self.view.scrolled_window.get_vadjustment().get_value()
        if scrolling_offset == 0:
            self.view.prev_button.set_sensitive(False)
        else:
            self.view.prev_button.set_sensitive(True)
        final_label_offset = self.view.vbox.get_allocated_height() - self.view.page_views[0].get_allocated_height()
        if scrolling_offset >= final_label_offset:
            self.view.next_button.set_sensitive(False)
        else:
            self.view.next_button.set_sensitive(True)
        self.update_labels()

    def update_labels(self):
        offset = self.view.page_view_recent.get_allocated_height() + self.view.label_recent.get_allocated_height() + 1
        scrolling_offset = self.view.scrolled_window.get_vadjustment().get_value()
        self.view.tabs_box.get_style_context().remove_class('no-border')
        for key, page in enumerate(reversed(self.view.page_views)):
            label = self.view.labels[len(self.view.page_views) - key - 1]
            margin_top = max(0, offset - int(scrolling_offset))
            label.set_margin_top(margin_top)
            if margin_top > 0 and margin_top <= label.get_allocated_height():
                self.view.tabs_box.get_style_context().add_class('no-border')
            offset += page.get_allocated_height() + label.get_allocated_height() + 1

    def on_next_button_clicked(self, button):
        offset = self.view.page_view_recent.get_allocated_height() + self.view.label_recent.get_allocated_height() + 1
        scrolling_offset = self.view.scrolled_window.get_vadjustment().get_value()
        if scrolling_offset < offset:
            self.scroll_view(offset)
            return

        for key, page in enumerate(reversed(self.view.page_views)):
            label = self.view.labels[len(self.view.page_views) - key - 1]
            if offset >= scrolling_offset - (page.get_allocated_height() + label.get_allocated_height()):
                new_offset = offset + (page.get_allocated_height() + label.get_allocated_height()) + 1
                if key < len(self.view.page_views) - 1:
                    self.scroll_view(new_offset)
                break
            offset += page.get_allocated_height() + label.get_allocated_height() + 1

    def on_prev_button_clicked(self, button):
        offset = self.view.page_view_recent.get_allocated_height() + self.view.label_recent.get_allocated_height() + 1
        old_offset = offset
        scrolling_offset = self.view.scrolled_window.get_vadjustment().get_value()

        if scrolling_offset <= offset:
            self.scroll_view(0)
            return

        for key, page in enumerate(reversed(self.view.page_views)):
            label = self.view.labels[len(self.view.page_views) - key - 1]
            if offset >= scrolling_offset - (page.get_allocated_height() + label.get_allocated_height()):
                if offset == int(scrolling_offset):
                    new_offset = old_offset
                else:
                    new_offset = offset
                self.scroll_view(new_offset)
                break
            old_offset = offset
            offset += page.get_allocated_height() + label.get_allocated_height() + 1

    def on_flowbox_clicked(self, flowbox, event, symbols_list):
        if event.button != 1: return

        child = flowbox.get_child_at_pos(event.x, event.y)

        if child != None and self.workspace.active_document != None:
            self.workspace.get_active_document().content.insert_text_at_cursor(symbols_list[child.get_index()][1])
            self.workspace.get_active_document().content.scroll_cursor_onscreen()
            self.add_recent_symbol((flowbox.symbol_folder, symbols_list[child.get_index()][1]))

        return True

    '''
    *** manage borders of images
    '''

    def on_page_size_allocate(self, symbol_page, allocation, data=None):
        if symbol_page.size != (allocation.width, allocation.height):
            symbol_page.size = (allocation.width, allocation.height)

            width_with_border = symbol_page.symbol_width + 11
            width_avail = allocation.width
            symbols_per_line = int((width_avail) / width_with_border)

            for number, image in enumerate(symbol_page.symbols):
                if (number % symbols_per_line) == symbols_per_line - 1:
                    image[5].get_style_context().add_class('no_right_border')
                else:
                    image[5].get_style_context().remove_class('no_right_border')

    def on_recent_page_size_allocate(self, page, allocation, data=None):
        if self.recent_page_size != (allocation.width, allocation.height):
            self.recent_page_size = (allocation.width, allocation.height)

            for number, recent_symbol in enumerate(self.recent_details):
                image = recent_symbol[5]
                image.get_style_context().remove_class('no_right_border')

            for offset in range(max(0, allocation.height) // 20 + 1):
                widget = page.get_child_at_pos(allocation.width - 1, offset * 20)
                if widget != None:
                    widget.get_child().get_style_context().add_class('no_right_border')

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



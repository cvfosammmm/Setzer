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
from gi.repository import Gdk, Gtk

import xml.etree.ElementTree as ET
import os

from setzer.widgets.search_entry.search_entry import SearchEntry
from setzer.app.service_locator import ServiceLocator


class SymbolsPageView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_size_request(252, -1)

        self.get_style_context().add_class('sidebar-symbols')

        self.overlay = Gtk.Overlay()
        self.overlay.set_vexpand(True)
        self.overlay.set_can_focus(False)
        self.vbox_top = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_vexpand(True)
        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.scrolled_window.set_child(self.vbox)

        self.tabs_box = Gtk.CenterBox()
        self.tabs_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.tabs_box.set_valign(Gtk.Align.START)
        self.tabs_box.set_halign(Gtk.Align.FILL)
        self.tabs_box.get_style_context().add_class('tabs-box')

        self.tabs = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)

        self.prev_button = Gtk.Button.new_from_icon_name('go-up-symbolic')
        self.prev_button.set_can_focus(False)
        self.prev_button.get_style_context().add_class('flat')
        self.prev_button.set_tooltip_text(_('Back'))
        self.tabs.append(self.prev_button)

        self.next_button = Gtk.Button.new_from_icon_name('go-down-symbolic')
        self.next_button.set_can_focus(False)
        self.next_button.get_style_context().add_class('flat')
        self.next_button.set_tooltip_text(_('Forward'))
        self.tabs.append(self.next_button)

        self.search_button = Gtk.ToggleButton()
        self.search_button.set_icon_name('edit-find-symbolic')
        self.search_button.set_can_focus(False)
        self.search_button.get_style_context().add_class('flat')
        self.search_button.set_tooltip_text(_('Find'))
        self.tabs.append(self.search_button)

        self.search_revealer = Gtk.Revealer()
        self.search_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.search_box.get_style_context().add_class('search_bar')

        self.search_entry = SearchEntry()
        self.search_entry.set_hexpand(True)
        self.search_box.append(self.search_entry)

        self.search_close_button = Gtk.Button.new_from_icon_name('window-close-symbolic')
        self.search_close_button.get_style_context().add_class('flat')
        self.search_close_button.set_can_focus(False)
        self.search_box.append(self.search_close_button)

        self.search_revealer.set_child(self.search_box)

        self.tabs_box.set_end_widget(self.tabs)
        self.vbox_top.append(self.tabs_box)
        self.vbox_top.append(self.scrolled_window)
        self.overlay.set_child(self.vbox_top)
        self.append(self.overlay)
        self.append(self.search_revealer)

        self.labels = list()
        self.symbols_views = list()
        self.placeholders = list()

        self.label_recent = Gtk.Label.new(_('Recent'))
        self.label_recent.set_xalign(0)
        self.label_recent.set_halign(Gtk.Align.START)
        self.label_recent.set_valign(Gtk.Align.START)
        self.label_recent.set_size_request(108, -1)
        self.label_recent.get_style_context().add_class('overlay')
        self.label_recent.set_can_target(False)
        self.overlay.add_overlay(self.label_recent)

        self.symbols_view_recent = Gtk.FlowBox()
        self.symbols_view_recent.set_homogeneous(False)
        self.symbols_view_recent.set_valign(Gtk.Align.START)
        self.symbols_view_recent.set_max_children_per_line(20)
        self.vbox.append(self.symbols_view_recent)

        self.symbols_lists = list()
        self.symbols_lists.append(['greek_letters', 'own-symbols-greek-letters-symbolic', _('Greek Letters'), 
                           'SidebarSymbolsList("greek_letters", 25)'])
        self.symbols_lists.append(['arrows', 'own-symbols-arrows-symbolic', _('Arrows'), 
                           'SidebarSymbolsList("arrows", 48)'])
        self.symbols_lists.append(['relations', 'own-symbols-relations-symbolic', _('Relations'), 
                           'SidebarSymbolsList("relations", 39)'])
        self.symbols_lists.append(['operators', 'own-symbols-operators-symbolic', _('Operators'), 
                           'SidebarSymbolsList("operators", 47)'])
        self.symbols_lists.append(['misc_math', 'own-symbols-misc-math-symbolic', _('Misc. Math'), 
                           'SidebarSymbolsList("misc_math", 42)'])
        self.symbols_lists.append(['misc_text', 'own-symbols-misc-text-symbolic', _('Misc. Symbols'), 
                           'SidebarSymbolsList("misc_text", 38)'])

        self.init_symbols_lists()

    def init_symbols_lists(self):
        for symbols_list in self.symbols_lists:
            symbols_list_view = eval(symbols_list[3])
            label = Gtk.Label.new(symbols_list[2])
            label.set_xalign(0)
            label.set_halign(Gtk.Align.START)
            label.set_valign(Gtk.Align.START)
            label.set_size_request(108, -1)
            label.get_style_context().add_class('overlay')
            label.set_can_target(False)
            self.overlay.add_overlay(label)
            self.labels.append(label)
            placeholder = Gtk.Label.new(symbols_list[2])
            placeholder.set_xalign(0)
            placeholder.get_style_context().add_class('placeholder')
            self.placeholders.append(placeholder)
            self.vbox.append(placeholder)
            self.symbols_views.append(symbols_list_view)
            self.vbox.append(symbols_list_view)


class SidebarSymbolsList(Gtk.FlowBox):

    def __init__(self, symbol_folder, symbol_width):
        Gtk.FlowBox.__init__(self)

        self.symbol_folder = symbol_folder
        self.symbol_width = symbol_width
        
        self.size = None
        
        # symbols: icon name, latex code
        self.symbols = list()
        self.visible_symbols = list()
        
        self.set_homogeneous(False)
        self.set_valign(Gtk.Align.START)
        self.set_max_children_per_line(20)
        
        xml_tree = ET.parse(os.path.join(ServiceLocator.get_resources_path(), 'symbols', symbol_folder + '.xml'))
        xml_root = xml_tree.getroot()
        for symbol_tag in xml_root:
            self.symbols.append([symbol_tag.attrib['file'].rsplit('.')[0], symbol_tag.attrib['command'], symbol_tag.attrib.get('package', None), int(symbol_tag.attrib.get('original_width', 10)), int(symbol_tag.attrib.get('original_height', 10))])

        self.init_symbols_list()

    def init_symbols_list(self):
        for symbol in self.symbols:
            size = max(symbol[3], symbol[4])

            image = Gtk.Image.new_from_icon_name('sidebar-' + symbol[0] + '-symbolic')
            image.set_pixel_size(int(size * 1.5))
            tooltip_text = symbol[1]
            if symbol[2] != None: 
                tooltip_text += ' (' + _('Package') + ': ' + symbol[2] + ')'
            image.set_tooltip_text(tooltip_text)
            image.set_size_request(self.symbol_width + 11, -1)
            symbol.append(image)
            self.visible_symbols.append(symbol)
            self.insert(image, -1)



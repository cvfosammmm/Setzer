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
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk
from gi.repository import Gtk

from setzer.app.service_locator import ServiceLocator

import xml.etree.ElementTree as ET
import os


class SymbolsPageView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self, orientation = Gtk.Orientation.VERTICAL)

        self.get_style_context().add_class('sidebar-symbols')

        self.overlay = Gtk.Overlay()
        self.vbox_top = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.scrolled_window = Gtk.ScrolledWindow()
        self.vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.scrolled_window.add(self.vbox)

        self.tabs_box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.tabs_box.set_valign(Gtk.Align.START)
        self.tabs_box.set_halign(Gtk.Align.FILL)
        self.tabs_box.get_style_context().add_class('tabs-box')

        self.tabs = Gtk.Toolbar()
        self.tabs.set_style(Gtk.ToolbarStyle.ICONS)
        self.tabs.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.tabs.set_icon_size(Gtk.IconSize.SMALL_TOOLBAR)

        self.prev_button = Gtk.ToolButton()
        self.prev_button.set_icon_name('go-up-symbolic')
        self.prev_button.set_focus_on_click(False)
        self.prev_button.set_tooltip_text(_('Back'))
        self.tabs.insert(self.prev_button, -1)

        self.next_button = Gtk.ToolButton()
        self.next_button.set_icon_name('go-down-symbolic')
        self.next_button.set_focus_on_click(False)
        self.next_button.set_tooltip_text(_('Forward'))
        self.tabs.insert(self.next_button, -1)

        self.search_button = Gtk.ToggleToolButton()
        self.search_button.set_icon_name('edit-find-symbolic')
        self.search_button.set_focus_on_click(False)
        self.search_button.set_tooltip_text(_('Find'))
        self.tabs.insert(self.search_button, -1)

        self.search_revealer = Gtk.Revealer()
        self.search_box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.search_box.get_style_context().add_class('search_bar')

        self.search_entry = Gtk.SearchEntry()
        self.search_box.pack_start(self.search_entry, True, True, 0)

        self.search_close_button = Gtk.Button.new_from_icon_name('window-close-symbolic', Gtk.IconSize.MENU)
        self.search_close_button.get_style_context().add_class('flat')
        self.search_close_button.set_can_focus(False)
        self.search_box.pack_start(self.search_close_button, False, False, 0)

        self.search_revealer.add(self.search_box)

        self.tabs_box.pack_end(self.tabs, False, False, 0)
        self.vbox_top.pack_start(self.tabs_box, False, False, 0)
        self.vbox_top.pack_start(self.scrolled_window, True, True, 0)
        self.overlay.add(self.vbox_top)
        self.pack_start(self.overlay, True, True, 0)
        self.pack_start(self.search_revealer, False, False, 0)

        self.labels = list()
        self.symbols_views = list()
        self.placeholders = list()

        self.label_recent = Gtk.Label(_('Recent'))
        self.label_recent.set_xalign(0)
        self.label_recent.set_halign(Gtk.Align.START)
        self.label_recent.set_valign(Gtk.Align.START)
        self.label_recent.set_size_request(108, -1)
        self.label_recent.get_style_context().add_class('overlay')
        self.overlay.add_overlay(self.label_recent)
        self.overlay.reorder_overlay(self.label_recent, 0)
        self.overlay.set_overlay_pass_through(self.label_recent, True)

        self.symbols_view_recent = Gtk.FlowBox()
        self.symbols_view_recent.set_homogeneous(False)
        self.symbols_view_recent.set_valign(Gtk.Align.START)
        self.symbols_view_recent.set_max_children_per_line(20)
        self.vbox.pack_start(self.symbols_view_recent, False, False, 0)

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
            label = Gtk.Label(symbols_list[2])
            label.set_xalign(0)
            label.set_halign(Gtk.Align.START)
            label.set_valign(Gtk.Align.START)
            label.set_size_request(108, -1)
            label.get_style_context().add_class('overlay')
            self.overlay.add_overlay(label)
            self.overlay.set_overlay_pass_through(label, True)
            self.labels.append(label)
            placeholder = Gtk.Label(symbols_list[2])
            placeholder.set_xalign(0)
            self.placeholders.append(placeholder)
            self.vbox.pack_start(placeholder, False, False, 0)
            self.symbols_views.append(symbols_list_view)
            self.vbox.pack_start(symbols_list_view, False, False, 0)

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE

    def do_get_preferred_width(self):
        return 252, 300


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

            image = Gtk.Image.new_from_icon_name('sidebar-' + symbol[0] + '-symbolic', 0)
            image.set_pixel_size(int(size * 1.5))
            tooltip_text = symbol[1]
            if symbol[2] != None: 
                tooltip_text += ' (' + _('Package') + ': ' + symbol[2] + ')'
            image.set_tooltip_text(tooltip_text)
            image.set_size_request(self.symbol_width + 11, -1)
            symbol.append(image)
            self.visible_symbols.append(symbol)
            self.insert(image, -1)



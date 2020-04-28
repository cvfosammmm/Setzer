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
from gi.repository import Gtk

from setzer.app.service_locator import ServiceLocator

import xml.etree.ElementTree as ET
import os


class Sidebar(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)
        
        self.get_style_context().add_class('sidebar')

        self.vbox = Gtk.VBox()

        # icons on top
        self.tabs = Gtk.Toolbar()
        self.tabs.set_style(Gtk.ToolbarStyle.ICONS)
        self.tabs.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.tabs.set_icon_size(Gtk.IconSize.SMALL_TOOLBAR)
        
        # pages view
        self.stack = Gtk.Stack()
        
        self.vbox.pack_start(self.tabs, False, False, 0)
        self.vbox.pack_start(self.stack, True, True, 0)
        self.pack_start(self.vbox, True, True, 0)
        
    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE
                     
    def do_get_preferred_width(self):
        return 216, 300


class SidebarPage(Gtk.ScrolledWindow):

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)


class SidebarPageSymbolsList(SidebarPage):

    def __init__(self, symbol_folder, symbol_width, is_dark_mode):
        SidebarPage.__init__(self)
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        self.symbol_folder = symbol_folder
        self.symbol_width = symbol_width
        
        self.size = None
        
        # symbols: icon name, latex code
        self.symbols = list()
        self.images = list()
        
        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_homogeneous(False)
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_max_children_per_line(20)
        
        self.parent_folder = 'dark' if is_dark_mode else 'light'

        xml_tree = ET.parse(os.path.join(ServiceLocator.get_resources_path(), 'symbols', symbol_folder + '.xml'))
        xml_root = xml_tree.getroot()
        for symbol_tag in xml_root:
            self.symbols.append([symbol_tag.attrib['file'].rsplit('.')[0], symbol_tag.attrib['command'], symbol_tag.attrib.get('package', None), int(symbol_tag.attrib.get('original_width', 10)), int(symbol_tag.attrib.get('original_height', 10))])
        
        self.init_symbols_list()

        self.add(self.flowbox)
        
    def init_symbols_list(self):
        for symbol in self.symbols:
            size = max(symbol[3], symbol[4])

            image = Gtk.Image.new_from_icon_name('sidebar-' + symbol[0] + '-symbolic', 0)
            image.set_pixel_size(int(size * 1.5))
            self.images.append([image, symbol])
            button = Gtk.Button()
            button.set_image(image)
            tooltip_text = symbol[1]
            if symbol[2] != None: 
                tooltip_text += ' (' + _('Package') + ': ' + symbol[2] + ')'
            button.set_tooltip_text(tooltip_text)
            symbol.append(button)
            self.flowbox.insert(button, -1)



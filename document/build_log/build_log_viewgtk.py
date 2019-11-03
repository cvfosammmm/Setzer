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


class BuildLogView(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)
        self.get_style_context().add_class('buildlog')

        self.position = 200
        
        self.scrolled_window = Gtk.ScrolledWindow()
        self.list = Gtk.ListBox()
        self.list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.list.set_sort_func(self.sort_function)
        self.scrolled_window.add(self.list)

        self.header = Gtk.HBox()
        self.close_button = Gtk.Button.new_from_icon_name('window-close-symbolic', Gtk.IconSize.MENU)
        self.close_button.get_style_context().add_class('flat')
        self.close_button.set_can_focus(False)
        self.header_label = Gtk.Label()
        self.header_label.set_markup('<b>Building failed with 1 error</b> (4 warnings and badboxes):')
        self.header_label.set_markup('<b>Building successful</b> (4 Warnings and BadBoxes):')
        self.header_label.set_size_request(300, -1)
        self.header_label.set_xalign(0)
        self.header_label.set_margin_left(0)
        self.header.pack_start(self.header_label, True, True, 0)
        self.header.pack_start(self.close_button, False, False, 0)

        self.pack_start(self.header, False, False, 0)
        self.pack_start(self.scrolled_window, True, True, 0)
        self.set_size_request(200, 200)

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE
                     
    def sort_function(self, row1, row2, user_data=None):
        line_number1 = row1.get_child().line_number
        line_number2 = row2.get_child().line_number
        message_type1 = row1.get_child().label_message_type.get_text()
        message_type2 = row2.get_child().label_message_type.get_text()
        
        if message_type1 != 'Error' and message_type2 == 'Error':
            return 1
        elif message_type1 == 'Error' and message_type2 != 'Error':
            return 0
        if line_number1 > line_number2:
            return 1
        elif line_number1 == line_number2:
            return 0
        else:
            return -1
        

class BuildLogRowView(Gtk.HBox):

    def __init__(self, icon_name, message_type, line_number, message):
        Gtk.HBox.__init__(self)
        
        try:
            self.line_number = int(line_number[5:].strip())
        except ValueError:
            self.line_number = 0
            line_number = ''

        self.icon_box = Gtk.VBox()
        self.icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
        self.icon.set_margin_left(10)
        self.icon.set_margin_right(12)
        self.icon.set_margin_top(1)
        self.icon.set_valign(0)
        self.icon_box.pack_start(self.icon, False, False, 0)
        self.label_message_type = Gtk.Label(message_type)
        self.label_message_type.set_size_request(80, -1)
        self.label_message_type.set_xalign(0)
        self.label_message_type.set_yalign(0)
        self.label_line_number = Gtk.Label(line_number)
        self.label_line_number.set_size_request(80, -1)
        self.label_line_number.set_xalign(0)
        self.label_line_number.set_yalign(0)
        self.label_message = Gtk.Label()
        self.label_message.set_text(message)
        self.label_message.set_size_request(100, -1)
        self.label_message.set_xalign(0)
        self.label_message.set_yalign(0)
        self.label_message.set_line_wrap(False)
        self.pack_start(self.icon_box, False, False, 0)
        self.pack_start(self.label_message_type, False, False, 0)
        self.pack_start(self.label_line_number, False, False, 0)
        self.pack_start(self.label_message, True, True, 0)



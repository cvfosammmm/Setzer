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
from gi.repository import Gtk, GLib
from gi.repository import Gdk, GdkPixbuf

import os


class AddRemovePackagesDialogView(object):
    ''' Create document templates for users to build on. '''

    def __init__(self, main_window):
        builder = Gtk.Builder.new_from_string('<?xml version="1.0" encoding="UTF-8"?><interface><object class="GtkDialog" id="dialog"><property name="use-header-bar">1</property></object></interface>', -1)

        self.dialog = builder.get_object('dialog')
        self.dialog.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.dialog.set_modal(True)
        self.dialog.set_transient_for(main_window)
        self.dialog.set_destroy_with_parent(True)
        self.dialog.set_default_size(650, -1)
        self.dialog.set_can_focus(False)
        self.topbox = self.dialog.get_content_area()
        self.topbox.set_border_width(0)
        self.topbox.set_size_request(650, -1)

        self.create_headerbar()
        self.create_add_box()
        self.create_remove_box()

        self.topbox.show_all()

    def create_headerbar(self):
        self.headerbar = self.dialog.get_header_bar()
        self.headerbar.set_title(_('Add / Remove Packages'))
        self.headerbar.show_all()

    def create_add_box(self):
        self.add_box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.add_box.get_style_context().add_class('add-remove-packages-add-box')

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_size_request(300, 146)
        self.scrolled_window.set_margin_right(18)
        self.add_list = Gtk.ListBox()
        self.add_list.set_can_focus(True)
        self.add_list.set_size_request(298, -1)
        self.add_list.set_vexpand(False)
        self.add_list.set_sort_func(self.sort_function)
        self.scrolled_window.add(self.add_list)

        self.add_details = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.add_description = Gtk.Label('')
        self.add_description.set_yalign(0)
        self.add_description.set_xalign(0)
        self.add_description.set_size_request(300, 110)
        self.add_description.set_line_wrap(True)
        self.add_description.set_width_chars(30)
        self.add_details.pack_start(self.add_description, False, False, 0)
        self.add_button = Gtk.Button()
        self.add_button.set_label(_('Add Package'))
        add_button_wrapper = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        add_button_wrapper.pack_start(self.add_button, False, False, 0)
        self.add_button.get_style_context().add_class('suggested-action')
        self.add_details.pack_start(add_button_wrapper, False, False, 0)
        
        self.add_box.pack_start(self.scrolled_window, False, False, 0)
        self.add_box.pack_start(self.add_details, False, False, 0)

        self.topbox.pack_start(self.add_box, False, False, 0)

    def create_remove_box(self):
        self.remove_box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.remove_box.set_margin_top(18)
        self.remove_box.set_margin_bottom(18)
        self.remove_box.set_margin_left(18)
        self.remove_box.set_margin_right(18)
        self.remove_box.get_style_context().add_class('add-remove-packages-remove-box')

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_size_request(300, 146)
        self.scrolled_window.set_margin_right(18)
        self.remove_list = Gtk.ListBox()
        self.remove_list.set_can_focus(True)
        self.remove_list.set_size_request(298, -1)
        self.remove_list.set_vexpand(False)
        self.remove_list.set_sort_func(self.sort_function)
        self.scrolled_window.add(self.remove_list)

        self.remove_details = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.remove_description = Gtk.Label('')
        self.remove_description.set_yalign(0)
        self.remove_description.set_xalign(0)
        self.remove_description.set_size_request(300, 110)
        self.remove_description.set_line_wrap(True)
        self.remove_description.set_width_chars(30)
        self.remove_details.pack_start(self.remove_description, False, False, 0)
        self.remove_button = Gtk.Button()
        self.remove_button.set_label(_('Remove Package'))
        remove_button_wrapper = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        remove_button_wrapper.pack_start(self.remove_button, False, False, 0)
        self.remove_details.pack_start(remove_button_wrapper, False, False, 0)
        
        self.remove_box.pack_start(self.scrolled_window, False, False, 0)
        self.remove_box.pack_start(self.remove_details, False, False, 0)

        self.topbox.pack_start(self.remove_box, False, False, 0)

    def sort_function(self, row1, row2, user_data=None):
        val1 = row1.get_child().get_text().lower()
        val2 = row2.get_child().get_text().lower()

        if val1 > val2:
            return 1
        elif  val1 == val2:
            return 0
        elif val1 < val2:
            return -1

    def run(self):
        return self.dialog.run()
        
    def __del__(self):
        self.dialog.destroy()



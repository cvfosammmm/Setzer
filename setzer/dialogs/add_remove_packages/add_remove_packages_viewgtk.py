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
from gi.repository import Gtk

import os

from setzer.dialogs.helpers.dialog_viewgtk import DialogView


class AddRemovePackagesDialogView(DialogView):

    def __init__(self, main_window):
        DialogView.__init__(self, main_window)

        self.set_default_size(650, -1)
        self.set_can_focus(False)
        self.headerbar.set_title_widget(Gtk.Label.new(_('Add / Remove Packages')))
        self.topbox.set_size_request(650, -1)

        self.create_add_box()
        self.create_remove_box()

    def create_add_box(self):
        self.add_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.add_box.get_style_context().add_class('add-remove-packages-add-box')

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_size_request(300, 146)
        self.scrolled_window.set_margin_end(18)
        self.add_list = Gtk.ListBox()
        self.add_list.set_can_focus(True)
        self.add_list.set_size_request(298, -1)
        self.add_list.set_vexpand(False)
        self.add_list.set_sort_func(self.sort_function)
        self.scrolled_window.set_child(self.add_list)

        self.add_details = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.add_description = Gtk.Label.new('')
        self.add_description.set_yalign(0)
        self.add_description.set_xalign(0)
        self.add_description.set_size_request(300, 110)
        self.add_description.set_wrap(True)
        self.add_description.set_width_chars(30)
        self.add_details.append(self.add_description)
        self.add_button = Gtk.Button()
        self.add_button.set_label(_('Add Package'))
        add_button_wrapper = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        add_button_wrapper.append(self.add_button)
        self.add_button.get_style_context().add_class('suggested-action')
        self.add_details.append(add_button_wrapper)
        
        self.add_box.append(self.scrolled_window)
        self.add_box.append(self.add_details)

        self.topbox.append(self.add_box)

    def create_remove_box(self):
        self.remove_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.remove_box.set_margin_top(18)
        self.remove_box.set_margin_bottom(18)
        self.remove_box.set_margin_start(18)
        self.remove_box.set_margin_end(18)
        self.remove_box.get_style_context().add_class('add-remove-packages-remove-box')

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_size_request(300, 146)
        self.scrolled_window.set_margin_end(18)
        self.remove_list = Gtk.ListBox()
        self.remove_list.set_can_focus(True)
        self.remove_list.set_size_request(298, -1)
        self.remove_list.set_vexpand(False)
        self.remove_list.set_sort_func(self.sort_function)
        self.scrolled_window.set_child(self.remove_list)

        self.remove_details = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.remove_description = Gtk.Label.new('')
        self.remove_description.set_yalign(0)
        self.remove_description.set_xalign(0)
        self.remove_description.set_size_request(300, 110)
        self.remove_description.set_wrap(True)
        self.remove_description.set_width_chars(30)
        self.remove_details.append(self.remove_description)
        self.remove_button = Gtk.Button()
        self.remove_button.set_label(_('Remove Package'))
        remove_button_wrapper = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        remove_button_wrapper.append(self.remove_button)
        self.remove_details.append(remove_button_wrapper)
        
        self.remove_box.append(self.scrolled_window)
        self.remove_box.append(self.remove_details)

        self.topbox.append(self.remove_box)

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



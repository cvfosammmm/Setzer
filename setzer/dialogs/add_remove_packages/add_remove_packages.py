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
from gi.repository import Gio
from gi.repository import GLib

import setzer.dialogs.add_remove_packages.add_remove_packages_viewgtk as view
from setzer.app.latex_db import LaTeXDB

import pickle
import os


class AddRemovePackagesDialog(object):

    def __init__(self, main_window):
        self.main_window = main_window
        self.packages = LaTeXDB.get_packages_dict()

        self.add_list_rows = dict()
        self.remove_list_rows = dict()

    def run(self, document):
        self.document = document

        self.setup()
        self.view.present()

    def setup(self):
        self.view = view.AddRemovePackagesDialogView(self.main_window)

        self.add_package_selection = None
        self.remove_package_selection = None

        self.view.add_button.set_sensitive(False)
        self.view.remove_button.set_sensitive(False)
        self.view.add_button.set_visible(False)
        self.view.remove_button.set_visible(False)

        self.view.add_list.connect('row-selected', self.add_list_row_selected)
        self.view.remove_list.connect('row-selected', self.remove_list_row_selected)
        self.view.add_button.connect('clicked', self.add_button_clicked)
        self.view.remove_button.connect('clicked', self.remove_button_clicked)

        for name, details in self.packages.items():
            if details['command'] in self.document.parser.symbols['packages']:
                row = self.add_to_list(self.view.remove_list, name)
                self.remove_list_rows[name] = row
            else:
                row = self.add_to_list(self.view.add_list, name)
                self.add_list_rows[name] = row

        self.view.remove_list.select_row(self.view.remove_list.get_row_at_index(0))
        self.view.add_list.select_row(self.view.add_list.get_row_at_index(0))

    def add_list_row_selected(self, box, row, user_data=None):
        if row != None:
            child_name = row.get_child().get_text()
            description = self.packages[child_name]['description']
            command = self.packages[child_name]['command']
            self.view.add_description.set_markup('<b>' + child_name + ':</b> ' + description)
            self.add_package_selection = command
        else:
            self.view.add_description.set_markup('')
        self.view.add_button.set_sensitive(row != None)
        self.view.add_button.set_visible(row != None)

    def remove_list_row_selected(self, box, row, user_data=None):
        if row != None:
            child_name = row.get_child().get_text()
            description = self.packages[child_name]['description']
            command = self.packages[child_name]['command']
            self.view.remove_description.set_markup('<b>' + child_name + ':</b> ' + description)
            self.remove_package_selection = command
        else:
            self.view.remove_description.set_markup('')
        self.view.remove_button.set_sensitive(row != None)
        self.view.remove_button.set_visible(row != None)

    def add_button_clicked(self, button):
        self.document.add_packages([self.add_package_selection])
        self.document.scroll_cursor_onscreen()
        selected_row = self.view.add_list.get_selected_row()
        selected_row_index = selected_row.get_index()
        new_row = self.view.add_list.get_row_at_index(selected_row_index + 1)
        if new_row == None:
            new_row = self.view.add_list.get_row_at_index(selected_row_index - 1)

        self.view.add_list.remove(selected_row)
        row = self.add_to_list(self.view.remove_list, self.add_package_selection)
        self.remove_list_rows[self.add_package_selection] = row
        self.view.remove_list.select_row(row)

        if new_row != None:
            self.view.add_list.select_row(new_row)

    def remove_button_clicked(self, button):
        self.document.remove_packages([self.remove_package_selection])
        selected_row = self.view.remove_list.get_selected_row()
        selected_row_index = selected_row.get_index()
        new_row = self.view.remove_list.get_row_at_index(selected_row_index + 1)
        if new_row == None:
            new_row = self.view.remove_list.get_row_at_index(selected_row_index - 1)

        self.view.remove_list.remove(selected_row)
        row = self.add_to_list(self.view.add_list, self.remove_package_selection)
        self.add_list_rows[self.remove_package_selection] = row
        self.view.add_list.select_row(row)

        if new_row != None:
            self.view.remove_list.select_row(new_row)

    def add_to_list(self, listbox, label_text):
        label = Gtk.Label.new(label_text)
        label.set_xalign(0)
        row = Gtk.ListBoxRow()
        row.set_child(label)
        listbox.prepend(row)
        return row



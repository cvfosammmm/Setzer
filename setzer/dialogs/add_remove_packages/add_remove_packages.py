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
from gi.repository import Gio
from gi.repository import GLib

from setzer.dialogs.dialog import Dialog
import setzer.dialogs.add_remove_packages.add_remove_packages_viewgtk as view
from setzer.app.service_locator import ServiceLocator

import pickle
import os


class AddRemovePackagesDialog(Dialog):

    def __init__(self, main_window, workspace):
        self.main_window = main_window
        self.workspace = workspace

        self.packages = ServiceLocator.get_packages_dict()

        self.current_values = dict()

    def run(self, document):
        self.document = document
        self.setup()
        self.view.run()
        self.view.dialog.hide()
        del(self.view)

    def setup(self):
        self.view = view.AddRemovePackagesDialogView(self.main_window)

        self.add_package_selection = None
        self.remove_package_selection = None

        def add_list_row_selected(box, row, user_data=None):
            if row != None:
                child_name = row.get_child().get_text()
                description = self.packages[child_name]['description']
                command = self.packages[child_name]['command']
                self.view.add_description.set_markup('<b>' + child_name + ':</b> ' + description)
                self.add_package_selection = command
                self.view.add_button.set_sensitive(True)
                self.view.add_button.show()
            else:
                self.view.add_description.set_markup('')
                self.view.add_button.set_sensitive(False)
                self.view.add_button.hide()

        def remove_list_row_selected(box, row, user_data=None):
            if row != None:
                child_name = row.get_child().get_text()
                description = self.packages[child_name]['description']
                command = self.packages[child_name]['command']
                self.view.remove_description.set_markup('<b>' + child_name + ':</b> ' + description)
                self.remove_package_selection = command
                self.view.remove_button.set_sensitive(True)
                self.view.remove_button.show()
            else:
                self.view.remove_description.set_markup('')
                self.view.remove_button.set_sensitive(False)
                self.view.remove_button.hide()

        def add_button_clicked(button):
            self.document.add_packages([self.add_package_selection])
            selected_row = self.view.add_list.get_selected_row()
            selected_row_index = selected_row.get_index()
            new_row = self.view.add_list.get_row_at_index(selected_row_index + 1)
            if new_row == None:
                new_row = self.view.add_list.get_row_at_index(selected_row_index - 1)

            self.view.add_list.remove(selected_row)
            self.add_to_list(self.view.remove_list, self.add_package_selection)
            for row in self.view.remove_list.get_children():
                if row.get_child().get_text() == self.add_package_selection:
                    self.view.remove_list.select_row(row)

            if new_row != None:
                self.view.add_list.select_row(new_row)

        def remove_button_clicked(button):
            self.document.content.remove_packages([self.remove_package_selection])
            selected_row = self.view.remove_list.get_selected_row()
            selected_row_index = selected_row.get_index()
            new_row = self.view.remove_list.get_row_at_index(selected_row_index + 1)
            if new_row == None:
                new_row = self.view.remove_list.get_row_at_index(selected_row_index - 1)

            self.view.remove_list.remove(selected_row)
            self.add_to_list(self.view.add_list, self.remove_package_selection)
            for row in self.view.add_list.get_children():
                if row.get_child().get_text() == self.remove_package_selection:
                    self.view.add_list.select_row(row)

            if new_row != None:
                self.view.remove_list.select_row(new_row)

        self.view.topbox.show_all()

        self.view.add_button.set_sensitive(False)
        self.view.remove_button.set_sensitive(False)
        self.view.add_button.hide()
        self.view.remove_button.hide()

        self.view.add_list.connect('row-selected', add_list_row_selected)
        self.view.remove_list.connect('row-selected', remove_list_row_selected)
        self.view.add_button.connect('clicked', add_button_clicked)
        self.view.remove_button.connect('clicked', remove_button_clicked)

        for name, details in self.packages.items():
            if details['command'] in self.document.get_packages():
                self.add_to_list(self.view.remove_list, name)
            else:
                self.add_to_list(self.view.add_list, name)

    def add_to_list(self, listbox, label_text):
        label = Gtk.Label(label_text)
        label.set_xalign(0)
        label.show_all()
        listbox.prepend(label)
        if listbox.get_selected_row() == None:
            listbox.select_row(listbox.get_row_at_index(0))



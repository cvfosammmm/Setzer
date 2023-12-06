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
from gi.repository import Pango

import os.path

from setzer.helpers.observable import Observable


class FilechooserButtonView(Gtk.Button):

    def __init__(self):
        Gtk.Button.__init__(self)

        self.button_widget = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
        self.button_label = Gtk.Label.new(_('(None)'))
        self.button_label.set_ellipsize(Pango.EllipsizeMode.START)
        self.button_widget.append(Gtk.Image.new_from_icon_name('document-open-symbolic'))
        self.button_widget.append(self.button_label)
        self.set_child(self.button_widget)


class FilechooserButton(Observable):

    def __init__(self, parent_window):
        Observable.__init__(self)

        self.parent_window = parent_window
        self.default_folder = None
        self.filename = None
        self.filters = list()
        self.title = _('Choose File')

        self.view = FilechooserButtonView()

        self.view.connect('clicked', self.on_button_clicked)

    def reset(self):
        self.default_folder = None
        self.filename = None
        self.view.button_label.set_text(_('(None)'))

    def set_default_folder(self, folder):
        self.default_folder = folder

    def set_title(self, title):
        self.title = title

    def get_filename(self):
        return self.filename

    def add_filter(self, file_filter):
        self.filters.append(file_filter)

    def on_button_clicked(self, button):
        self.dialog = Gtk.FileDialog()
        self.dialog.set_modal(True)
        self.dialog.set_title(self.title)

        for file_filter in self.filters:
            self.dialog.set_default_filter(file_filter)

        if self.default_folder != None:
            self.dialog.set_current_folder(self.default_folder)

        self.dialog.open(self.parent_window, None, self.dialog_process_response)

    def dialog_process_response(self, dialog, result):
        try:
            file = dialog.open_finish(result)
        except Exception: pass
        else:
            if file != None:
                self.filename = file.get_path()
                self.view.button_label.set_text(os.path.basename(self.filename))
                self.add_change_code('file-set')



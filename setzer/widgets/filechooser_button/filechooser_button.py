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
from gi.repository import Gtk
from gi.repository import Pango

import os.path

from setzer.helpers.observable import Observable


class FilechooserButtonView(Gtk.Button):

    def __init__(self):
        Gtk.Button.__init__(self)

        self.button_widget = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.button_label = Gtk.Label(_('(None)'))
        self.button_label.set_ellipsize(Pango.EllipsizeMode.START)
        self.button_widget.pack_end(Gtk.Image.new_from_icon_name('document-open-symbolic', Gtk.IconSize.BUTTON), False, False, 0)
        self.button_widget.pack_start(self.button_label, False, False, 0)
        self.add(self.button_widget)


class FilechooserButton(Observable):

    def __init__(self, main_window):
        Observable.__init__(self)

        self.main_window = main_window
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
        action = Gtk.FileChooserAction.OPEN
        buttons = (_('_Cancel'), Gtk.ResponseType.CANCEL, _('_Select'), Gtk.ResponseType.APPLY)
        dialog = Gtk.FileChooserDialog(self.title, self.main_window, action, buttons)

        for file_filter in self.filters:
            dialog.add_filter(file_filter)

        for widget in dialog.get_header_bar().get_children():
            if isinstance(widget, Gtk.Button) and widget.get_label() == _('_Select'):
                widget.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
                widget.set_can_default(True)
                widget.grab_default()

        if self.default_folder != None:
            dialog.set_current_folder(self.default_folder)

        response = dialog.run()
        if response == Gtk.ResponseType.APPLY:
            self.filename = dialog.get_filename()
            self.view.button_label.set_text(os.path.basename(self.filename))
            self.add_change_code('file-set')
        dialog.hide()
        del(dialog)



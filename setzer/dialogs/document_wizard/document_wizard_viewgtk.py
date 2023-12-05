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
from gi.repository import Gtk, GLib, Gdk, GdkPixbuf

import os

from setzer.dialogs.helpers.dialog_viewgtk import DialogView


class DocumentWizardView(DialogView):

    def __init__(self, main_window):
        DialogView.__init__(self, main_window)

        self.set_default_size(750, 500)
        self.headerbar.set_title_widget(Gtk.Label.new(_('Add / Remove Packages')))
        self.headerbar.set_show_title_buttons(False)
        self.topbox.set_size_request(750, 450)

        self.center_box = Gtk.CenterBox()
        self.center_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.pages = list()

        self.title_label = Gtk.Label.new(_('Create a template document'))
        self.title_label.get_style_context().add_class('title')
        self.subtitle_label = Gtk.Label.new('')
        self.subtitle_label.get_style_context().add_class('subtitle')

        self.title_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.title_box.append(self.title_label)
        self.title_box.append(self.subtitle_label)

        self.title_widget = Gtk.CenterBox()
        self.title_widget.set_orientation(Gtk.Orientation.VERTICAL)
        self.title_widget.set_center_widget(self.title_box)

        self.cancel_button = Gtk.Button.new_with_mnemonic(_('_Cancel'))
        self.cancel_button.set_can_focus(False)

        self.back_button = Gtk.Button.new_with_mnemonic(_('_Back'))
        self.back_button.set_can_focus(False)
        
        self.next_button = Gtk.Button.new_with_mnemonic(_('_Next'))
        self.next_button.set_can_focus(False)
        self.next_button.get_style_context().add_class('suggested-action')

        self.create_button = Gtk.Button.new_with_mnemonic(_('_Create'))
        self.create_button.set_can_focus(False)
        self.create_button.get_style_context().add_class('suggested-action')

        self.headerbar.set_title_widget(self.title_widget)
        self.headerbar.pack_start(self.cancel_button)
        self.headerbar.pack_start(self.back_button)
        self.headerbar.pack_end(self.create_button)
        self.headerbar.pack_end(self.next_button)

        self.notebook = Gtk.Notebook()
        self.notebook.set_show_tabs(False)
        self.notebook.set_show_border(False)
        self.center_box.set_center_widget(self.notebook)
        self.topbox.append(self.center_box)



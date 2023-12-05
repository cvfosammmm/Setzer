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
from gi.repository import Gtk, GLib
from gi.repository import Gdk, GdkPixbuf

import os

import setzer.widgets.filechooser_button.filechooser_button as filechooser_button
from setzer.dialogs.helpers.dialog_viewgtk import DialogView


class IncludeLaTeXFileView(DialogView):

    def __init__(self, main_window):
        DialogView.__init__(self, main_window)

        self.set_default_size(400, -1)
        self.set_can_focus(False)
        self.get_style_context().add_class('include-latex-file-dialog')
        self.headerbar.set_show_title_buttons(False)
        self.headerbar.set_title_widget(Gtk.Label.new(_('Include LaTeX file')))
        self.topbox.set_size_request(400, -1)

        self.cancel_button = Gtk.Button.new_with_mnemonic(_('_Cancel'))
        self.cancel_button.set_can_focus(False)
        self.headerbar.pack_start(self.cancel_button)

        self.include_button = Gtk.Button.new_with_mnemonic(_('_Include'))
        self.include_button.set_can_focus(False)
        self.include_button.get_style_context().add_class('suggested-action')
        self.headerbar.pack_end(self.include_button)

        self.content = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.content.set_vexpand(True)
        self.content.set_margin_start(18)
        self.content.set_margin_end(18)
        self.topbox.append(self.content)

        label = Gtk.Label.new(_('LaTeX file to include'))
        label.set_xalign(0)
        label.set_margin_bottom(3)
        label.set_margin_top(18)
        self.content.append(label)
        self.file_chooser_button = filechooser_button.FilechooserButton(self)
        self.file_chooser_button.set_title(_('Select a LaTeX File'))
        self.content.append(self.file_chooser_button.view)

        label = Gtk.Label.new(_('Type of path to included file'))
        label.set_xalign(0)
        label.set_margin_bottom(3)
        label.set_margin_top(18)
        self.content.append(label)

        self.pathtype_switcher = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.pathtype_switcher.get_style_context().add_class('linked')
        self.pathtype_buttons = dict()

        self.pathtype_info_button = Gtk.ToggleButton()
        self.pathtype_info_button.set_child(Gtk.Image.new_from_icon_name('dialog-information-symbolic'))
        self.pathtype_info_button.get_style_context().add_class('circular')
        self.pathtype_info_button.get_style_context().add_class('flat')

        box = Gtk.CenterBox()
        box.set_orientation(Gtk.Orientation.HORIZONTAL)
        box.set_start_widget(self.pathtype_switcher)
        box.set_end_widget(self.pathtype_info_button)
        box.set_margin_bottom(18)
        self.content.append(box)

        self.description_revealer = Gtk.Revealer()
        description = Gtk.Label()
        description.set_wrap(True)
        description.set_markup(_('<b>Relative Path:</b> Set the path relative to the main document. This is useful when the included file is in the same folder as the main document and you want to move around both of them together.') + ' (' + _('recommended') + ')\n\n' + _('<b>Absolute Path:</b> Specify the absolute location of the included file in your filesystem.'))
        description.set_xalign(0)
        description.set_margin_bottom(18)
        self.description_revealer.set_child(description)
        self.content.append(self.description_revealer)



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

import setzer.widgets.filechooser_button.filechooser_button as filechooser_button


class IncludeLaTeXFileView(object):

    def __init__(self, main_window):
        builder = Gtk.Builder.new_from_string('<?xml version="1.0" encoding="UTF-8"?><interface><object class="GtkDialog" id="dialog"><property name="use-header-bar">1</property></object></interface>', -1)

        self.dialog = builder.get_object('dialog')
        self.dialog.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.dialog.set_modal(True)
        self.dialog.set_transient_for(main_window)
        self.dialog.set_destroy_with_parent(True)
        self.dialog.set_default_size(400, -1)
        self.dialog.set_can_focus(False)
        self.dialog.get_style_context().add_class('include-latex-file-dialog')
        self.topbox = self.dialog.get_content_area()
        self.topbox.set_border_width(0)
        self.topbox.set_size_request(400, -1)
        
        self.create_headerbar()

        self.content = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.content.set_margin_left(18)
        self.content.set_margin_right(18)
        label = Gtk.Label(_('LaTeX file to include'))
        label.set_xalign(0)
        label.set_margin_bottom(3)
        label.set_margin_top(18)
        self.content.pack_start(label, False, False, 0)
        self.file_chooser_button = filechooser_button.FilechooserButton(main_window)
        self.file_chooser_button.set_title(_('Select a LaTeX File'))
        self.content.pack_start(self.file_chooser_button.view, False, False, 0)

        label = Gtk.Label(_('Type of path to included file'))
        label.set_xalign(0)
        label.set_margin_bottom(3)
        label.set_margin_top(18)
        self.content.pack_start(label, False, False, 0)

        box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.pathtype_switcher = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.pathtype_switcher.get_style_context().add_class('linked')
        self.pathtype_buttons = dict()
        image = Gtk.Image.new_from_icon_name('dialog-information-symbolic', Gtk.IconSize.MENU)
        self.pathtype_info_button = Gtk.ToggleButton()
        self.pathtype_info_button.set_image(image)
        self.pathtype_info_button.get_style_context().add_class('circular')
        self.pathtype_info_button.get_style_context().add_class('flat')
        box.pack_start(self.pathtype_switcher, False, False, 0)
        box.pack_end(self.pathtype_info_button, False, False, 0)
        box.set_margin_bottom(18)
        self.content.pack_start(box, False, False, 0)

        self.description_revealer = Gtk.Revealer()
        description = Gtk.Label()
        description.set_line_wrap(True)
        description.set_markup(_('<b>Relative Path:</b> Set the path relative to the main document. This is useful when the included file is in the same folder as the main document and you want to move around both of them together.') + ' (' + _('recommended') + ')\n\n' + _('<b>Absolute Path:</b> Specify the absolute location of the included file in your filesystem.'))
        description.set_xalign(0)
        description.set_margin_bottom(18)
        self.description_revealer.add(description)
        self.content.pack_start(self.description_revealer, False, False, 0)

        self.topbox.pack_start(self.content, True, True, 0)
        self.topbox.show_all()

    def create_headerbar(self):
        self.headerbar = self.dialog.get_header_bar()
        self.headerbar.set_show_close_button(False)
        self.headerbar.set_title(_('Include LaTeX file'))

        self.cancel_button = self.dialog.add_button(_('_Cancel'), Gtk.ResponseType.CANCEL)
        self.cancel_button.set_can_focus(False)
        
        self.create_button = self.dialog.add_button(_('_Include'), Gtk.ResponseType.APPLY)
        self.create_button.set_can_focus(False)
        self.create_button.get_style_context().add_class('suggested-action')
        
        self.headerbar.show_all()

    def run(self):
        return self.dialog.run()
        
    def __del__(self):
        self.dialog.destroy()



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
from gi.repository import Gdk
from gi.repository import Pango


class DocumentStructurePageView(Gtk.Overlay):

    def __init__(self):
        Gtk.Overlay.__init__(self)

        self.vbox = Gtk.VBox()
        self.content_vbox = Gtk.VBox()

        self.get_style_context().add_class('sidebar-document-structure')

        self.tabs_box = Gtk.HBox()
        self.tabs_box.get_style_context().add_class('tabs-box')
        self.tabs_box.pack_start(Gtk.Label('Files'), False, False, 0)
        self.vbox.pack_start(self.tabs_box, False, False, 0)

        self.tabs = Gtk.Toolbar()
        self.tabs.set_style(Gtk.ToolbarStyle.ICONS)
        self.tabs.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.tabs.set_icon_size(Gtk.IconSize.SMALL_TOOLBAR)
        self.tabs_box.pack_end(self.tabs, False, False, 0)

        self.prev_button = Gtk.ToolButton()
        self.prev_button.set_icon_name('go-up-symbolic')
        self.prev_button.set_focus_on_click(False)
        self.prev_button.set_tooltip_text(_('Back'))
        self.tabs.insert(self.prev_button, -1)

        self.next_button = Gtk.ToolButton()
        self.next_button.set_icon_name('go-down-symbolic')
        self.next_button.set_focus_on_click(False)
        self.next_button.set_tooltip_text(_('Forward'))
        self.tabs.insert(self.next_button, -1)

        self.content_files = Gtk.DrawingArea()
        self.content_files.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.content_files.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.content_vbox.pack_start(self.content_files, False, False, 0)

        self.structure_label = Gtk.Label(_('Document Structure'))
        self.structure_label.set_xalign(0)
        self.content_vbox.pack_start(self.structure_label, False, False, 0)

        self.content_structure = Gtk.DrawingArea()
        self.content_structure.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.content_structure.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.content_vbox.pack_start(self.content_structure, False, False, 0)

        style_context = self.content_structure.get_style_context()
        self.font = self.content_structure.get_style_context().get_font(style_context.get_state())
        self.font_size = (self.font.get_size() * 4) / (3 * Pango.SCALE)
        self.line_height = int(self.font_size) + 11

        self.structure_label_overlay = Gtk.Label(_('Document Structure'))
        self.structure_label_overlay.set_xalign(0)
        self.structure_label_overlay.set_halign(Gtk.Align.START)
        self.structure_label_overlay.set_valign(Gtk.Align.START)
        self.structure_label_overlay.set_size_request(148, -1)
        self.structure_label_overlay.get_style_context().add_class('overlay')
        self.add_overlay(self.structure_label_overlay)
        self.set_overlay_pass_through(self.structure_label_overlay, True)

        self.labels_label = Gtk.Label(_('Labels'))
        self.labels_label.set_xalign(0)
        self.content_vbox.pack_start(self.labels_label, False, False, 0)

        self.labels_label_overlay = Gtk.Label(_('Labels'))
        self.labels_label_overlay.set_xalign(0)
        self.labels_label_overlay.set_halign(Gtk.Align.START)
        self.labels_label_overlay.set_valign(Gtk.Align.START)
        self.labels_label_overlay.set_size_request(148, -1)
        self.labels_label_overlay.get_style_context().add_class('overlay')
        self.add_overlay(self.labels_label_overlay)
        self.set_overlay_pass_through(self.labels_label_overlay, True)

        self.content_labels = Gtk.DrawingArea()
        self.content_labels.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.content_labels.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.content_vbox.pack_start(self.content_labels, False, False, 0)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.add(self.content_vbox)
        self.vbox.pack_start(self.scrolled_window, True, True, 0)

        self.add(self.vbox)
        self.show_all()

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE
                     
    def do_get_preferred_width(self):
        return 252, 300



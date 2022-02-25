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
        self.get_style_context().add_class('sidebar-document-structure')

        self.vbox = Gtk.VBox()
        self.content_vbox = Gtk.VBox()

        self.add_buttons()
        self.add_scrolled_window()

        self.content_widgets = dict()
        self.labels = dict()

        self.add_content_widget('files')
        self.add_label('structure', _('Document Structure'))
        self.add_content_widget('structure')
        self.add_label('labels', _('Labels'))
        self.add_content_widget('labels')

        style_context = self.content_widgets['structure'].get_style_context()
        self.font = style_context.get_font(style_context.get_state())
        self.font_size = (self.font.get_size() * 4) / (3 * Pango.SCALE)
        self.line_height = int(self.font_size) + 11

        self.show_all()

    def add_content_widget(self, name):
        content_widget = Gtk.DrawingArea()
        content_widget.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        content_widget.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.content_vbox.pack_start(content_widget, False, False, 0)

        self.content_widgets[name] = content_widget

    def add_label(self, name, text):
        label_inline = Gtk.Label(text)
        label_inline.set_xalign(0)
        self.content_vbox.pack_start(label_inline, False, False, 0)

        label_overlay = Gtk.Label(text)
        label_overlay.set_xalign(0)
        label_overlay.set_halign(Gtk.Align.START)
        label_overlay.set_valign(Gtk.Align.START)
        label_overlay.set_size_request(148, -1)
        label_overlay.get_style_context().add_class('overlay')
        self.add_overlay(label_overlay)
        self.set_overlay_pass_through(label_overlay, True)

        self.labels[name] = {'inline': label_inline, 'overlay': label_overlay}

    def add_buttons(self):
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

    def add_scrolled_window(self):
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.add(self.content_vbox)
        self.vbox.pack_start(self.scrolled_window, True, True, 0)
        self.add(self.vbox)

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE
                     
    def do_get_preferred_width(self):
        return 252, 300



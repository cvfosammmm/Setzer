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
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import Pango


class PreviewView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self, orientation = Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('preview')

        self.action_bar = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.action_bar.set_size_request(-1, 37)

        self.external_viewer_button = Gtk.Button.new_from_icon_name('external-viewer-symbolic', Gtk.IconSize.MENU)
        self.external_viewer_button.set_tooltip_text(_('External Viewer'))
        self.external_viewer_button.get_style_context().add_class('flat')
        self.external_viewer_button.set_can_focus(False)
        self.external_viewer_button_revealer = Gtk.Revealer()
        self.external_viewer_button_revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)
        box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        box.pack_start(self.external_viewer_button, False, False, 0)
        self.external_viewer_button_revealer.add(box)
        self.action_bar.pack_end(self.external_viewer_button_revealer, False, False, 0)

        self.pack_start(self.action_bar, False, False, 0)

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.drawing_area.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)

        self.menu_item_backward_sync = Gtk.MenuItem.new_with_label(_('Show Source'))
        self.menu_item_zoom_in = Gtk.MenuItem.new_with_label(_('Zoom In'))
        self.menu_item_zoom_out = Gtk.MenuItem.new_with_label(_('Zoom Out'))
        self.menu_item_zoom_fit_to_width = Gtk.MenuItem.new_with_label(_('Fit to Width'))
        self.menu_item_zoom_fit_to_text_width = Gtk.MenuItem.new_with_label(_('Fit to Text Width'))
        self.menu_item_zoom_fit_to_height = Gtk.MenuItem.new_with_label(_('Fit to Height'))
        self.context_menu = Gtk.Menu()
        self.context_menu.append(self.menu_item_backward_sync)
        self.context_menu.append(Gtk.SeparatorMenuItem())
        self.context_menu.append(self.menu_item_zoom_in)
        self.context_menu.append(self.menu_item_zoom_out)
        self.context_menu.append(self.menu_item_zoom_fit_to_width)
        self.context_menu.append(self.menu_item_zoom_fit_to_text_width)
        self.context_menu.append(self.menu_item_zoom_fit_to_height)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.add(self.drawing_area)

        self.blank_slate = BlankSlateView()

        self.overlay = Gtk.Overlay()
        self.stack = Gtk.Stack()
        self.stack.add_named(self.blank_slate, 'blank_slate')
        self.stack.add_named(self.scrolled_window, 'pdf')
        self.overlay.add(self.stack)
        self.pack_start(self.overlay, True, True, 0)

        self.target_label = Gtk.Label()
        self.target_label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        self.target_label.set_halign(Gtk.Align.START)
        self.target_label.set_valign(Gtk.Align.END)
        self.target_label.get_style_context().add_class('target-label')
        self.overlay.add_overlay(self.target_label)
        self.overlay.set_overlay_pass_through(self.target_label, True)

        self.show_all()

    def set_layout_data(self, layout_data):
        self.layout_data = layout_data

    def set_link_target_string(self, target_string):
        self.target_label.set_text(target_string)
        if target_string: self.target_label.show_all()
        else: self.target_label.hide()


class BlankSlateView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self, orientation = Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('preview_blank')

        self.pack_start(Gtk.DrawingArea(), True, True, 0)
        image = Gtk.Image.new_from_icon_name('own-no-preview-symbolic', Gtk.IconSize.DIALOG)
        image.set_pixel_size(150)
        self.pack_start(image, False, False, 0)
        header = Gtk.Label(_('No preview available'))
        header.get_style_context().add_class('header')
        self.pack_start(header, False, False, 0)
        body = Gtk.Label(_('To show a .pdf preview of your document, click the build button in the headerbar.'))
        body.get_style_context().add_class('body')
        body.set_line_wrap(True)
        self.pack_start(body, False, False, 0)
        self.pack_start(Gtk.DrawingArea(), True, True, 0)



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
from gi.repository import Gtk, Pango

from setzer.widgets.fixed_width_label.fixed_width_label import FixedWidthLabel
from setzer.popovers.popover_manager import PopoverManager


class PreviewPanelView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('preview')

        self.zoom_out_button = Gtk.Button.new_from_icon_name('zoom-out-symbolic')
        self.zoom_out_button.set_tooltip_text(_('Zoom out'))
        self.zoom_out_button.get_style_context().add_class('flat')
        self.zoom_out_button.set_can_focus(False)
        self.zoom_out_button.get_style_context().add_class('scbar')

        self.zoom_level_label = FixedWidthLabel(66)
        self.zoom_level_label.get_style_context().add_class('zoom-level-button')

        self.zoom_level_popover = PopoverManager.create_popover('preview_zoom_level')
        self.zoom_level_button = PopoverManager.create_popover_button('preview_zoom_level')
        self.zoom_level_button.set_can_focus(False)
        self.zoom_level_button.set_tooltip_text(_('Set zoom level'))
        self.zoom_level_button.get_style_context().add_class('flat')
        self.zoom_level_button.get_style_context().add_class('scbar')
        self.zoom_level_button.set_can_focus(False)
        self.zoom_level_button.set_child(self.zoom_level_label)

        self.zoom_in_button = Gtk.Button.new_from_icon_name('zoom-in-symbolic')
        self.zoom_in_button.set_tooltip_text(_('Zoom in'))
        self.zoom_in_button.get_style_context().add_class('flat')
        self.zoom_in_button.set_can_focus(False)
        self.zoom_in_button.get_style_context().add_class('scbar')

        self.recolor_pdf_toggle = Gtk.ToggleButton()
        self.recolor_pdf_toggle.set_icon_name('color-symbolic')
        self.recolor_pdf_toggle.set_tooltip_text(_('Match theme colors'))
        self.recolor_pdf_toggle.get_style_context().add_class('flat')
        self.recolor_pdf_toggle.set_can_focus(False)
        self.recolor_pdf_toggle.get_style_context().add_class('scbar')

        self.external_viewer_button = Gtk.Button.new_from_icon_name('external-viewer-symbolic')
        self.external_viewer_button.set_tooltip_text(_('External Viewer'))
        self.external_viewer_button.get_style_context().add_class('flat')
        self.external_viewer_button.set_can_focus(False)
        self.external_viewer_button.get_style_context().add_class('scbar')

        self.action_bar_right = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.action_bar_right.append(self.zoom_out_button)
        self.action_bar_right.append(self.zoom_level_button)
        self.action_bar_right.append(self.zoom_in_button)
        self.action_bar_right.append(self.recolor_pdf_toggle)
        self.action_bar_right.append(self.external_viewer_button)

        self.paging_label = FixedWidthLabel(100)
        self.paging_label.layout.set_alignment(Pango.Alignment.LEFT)
        self.paging_label.get_style_context().add_class('paging-widget')

        self.action_bar_left = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.action_bar_left.append(self.paging_label)

        self.action_bar = Gtk.CenterBox()
        self.action_bar.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.action_bar.set_size_request(-1, 37)
        self.action_bar.set_start_widget(self.action_bar_left)
        self.action_bar.set_end_widget(self.action_bar_right)

        self.notebook = Gtk.Notebook()
        self.notebook.set_show_tabs(False)
        self.notebook.set_show_border(False)
        self.notebook.set_vexpand(True)
        self.notebook.insert_page(Gtk.DrawingArea(), None, 0)

        self.append(self.action_bar)
        self.append(self.notebook)

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE
                     
    def do_get_preferred_width(self):
        return 300, 500



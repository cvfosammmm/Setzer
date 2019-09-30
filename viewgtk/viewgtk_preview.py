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
gi.require_version('GtkSource', '3.0')
gi.require_version('Poppler', '0.18')
from gi.repository import Gdk
from gi.repository import Gtk
import math

import helpers.helpers as helpers


class PreviewView(Gtk.Notebook):

    def __init__(self):
        Gtk.Notebook.__init__(self)
        self.set_show_tabs(False)
        self.set_show_border(False)
        
        self.box = Gtk.VBox()
        self.box.get_style_context().add_class('preview')
        
        self.zoom_widget = PreviewZoomWidget()
        self.paging_widget = PreviewPagingWidget()

        self.action_bar = Gtk.ActionBar()
        self.action_bar.pack_end(self.zoom_widget)
        self.action_bar.pack_start(self.paging_widget)
        self.box.pack_end(self.action_bar, False, False, 0)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.drawing_area = Gtk.DrawingArea()
        self.scrolled_window.add(self.drawing_area)
        self.box.pack_start(self.scrolled_window, True, True, 0)

        self.blank_slate = Gtk.VBox()
        self.blank_slate.get_style_context().add_class('preview_blank')
        self.blank_slate.pack_start(Gtk.DrawingArea(), True, True, 0)
        image = Gtk.Image.new_from_icon_name('own-no-preview-symbolic', Gtk.IconSize.DIALOG)
        image.set_pixel_size(150)
        self.blank_slate.pack_start(image, False, False, 0)
        header = Gtk.Label('No preview available')
        header.get_style_context().add_class('header')
        self.blank_slate.pack_start(header, False, False, 0)
        body = Gtk.Label('To show a .pdf preview of your document, click the build button in the headerbar.')
        body.get_style_context().add_class('body')
        body.set_line_wrap(True)
        self.blank_slate.pack_start(body, False, False, 0)
        self.blank_slate.pack_start(Gtk.DrawingArea(), True, True, 0)

        self.insert_page(self.blank_slate, None, 0)
        self.insert_page(self.box, None, 1)
        self.show_all()
        
    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE
                     
    def do_get_preferred_width(self):
        return 300, 500


class PreviewZoomWidget(Gtk.HBox):

    def __init__(self):
        Gtk.HBox.__init__(self)
        self.get_style_context().add_class('zoom_widget')
        
        self.zoom_out_button = Gtk.Button.new_from_icon_name('zoom-out-symbolic', Gtk.IconSize.MENU)
        self.zoom_out_button.get_style_context().add_class('flat')
        self.zoom_out_button.set_can_focus(False)
        self.zoom_in_button = Gtk.Button.new_from_icon_name('zoom-in-symbolic', Gtk.IconSize.MENU)
        self.zoom_in_button.get_style_context().add_class('flat')
        self.zoom_in_button.get_style_context().add_class('zoom_in_button')
        self.zoom_in_button.set_can_focus(False)
        
        self.label = Gtk.Label('100.0%')
        self.label.set_xalign(0.5)
        
        self.pack_start(self.zoom_out_button, False, False, 0)
        self.pack_start(self.label, False, False, 0)
        self.pack_start(self.zoom_in_button, False, False, 0)


class PreviewPagingWidget(Gtk.HBox):

    def __init__(self):
        Gtk.HBox.__init__(self)
        
        self.label = Gtk.Label('')
        self.label.get_style_context().add_class('page_counter')
        self.pack_start(self.label, False, False, 0)



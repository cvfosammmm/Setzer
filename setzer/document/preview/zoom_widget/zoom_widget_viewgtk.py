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
        self.show_all()



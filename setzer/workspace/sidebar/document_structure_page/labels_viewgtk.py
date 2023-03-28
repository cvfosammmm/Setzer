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
from gi.repository import Pango


class LabelsSectionView(Gtk.DrawingArea):

    def __init__(self):
        Gtk.DrawingArea.__init__(self)

        self.bg_color = None
        self.hover_color = None
        self.fg_color = None
        self.icon_infos = dict()
        self.icons = dict()

        self.icon_infos['tag'] = Gtk.IconTheme.get_default().lookup_icon('tag-symbolic', 16 * self.get_scale_factor(), 0)

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK)
        self.add_events(Gdk.EventMask.LEAVE_NOTIFY_MASK)
        self.add_events(Gdk.EventMask.POINTER_MOTION_MASK)

        style_context = self.get_style_context()
        self.font = style_context.get_font(style_context.get_state())
        self.font_size = (self.font.get_size() * 4) / (3 * Pango.SCALE)
        self.line_height = int(self.font_size) + 11



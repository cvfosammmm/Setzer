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
from gi.repository import Gtk


class DialogView(object):

    def __init__(self, main_window):
        self.dialog = Gtk.Window()
        self.dialog.set_modal(True)
        self.dialog.set_transient_for(main_window)
        self.dialog.set_destroy_with_parent(True)

        self.headerbar = Gtk.HeaderBar()
        self.dialog.set_titlebar(self.headerbar)

        self.topbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.dialog.set_child(self.topbox)



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
from gi.repository import Gtk
from gi.repository import GtkSource
from gi.repository import GdkPixbuf

import os.path


class CodeFoldingView(GtkSource.GutterRendererPixbuf):

    def __init__(self):
        GtkSource.GutterRendererPixbuf.__init__(self)
        path = os.path.dirname(os.path.realpath(__file__)) + '/resources/'
        self.pixbuf_unfolded = GdkPixbuf.Pixbuf.new_from_file_at_size(path + 'unfolded.png', 18, 18)
        self.pixbuf_folded = GdkPixbuf.Pixbuf.new_from_file_at_size(path + 'folded.png', 18, 18)
        self.pixbuf_neutral = GdkPixbuf.Pixbuf.new_from_file_at_size(path + 'neutral.png', 18, 18)
        self.set_size(18)



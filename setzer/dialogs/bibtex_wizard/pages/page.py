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


class Page(object):

    def load_presets(self, presets):
        pass

    def on_activation(self):
        pass


class PageView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self, orientation = Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('bibtex-wizard-page')

        self.set_margin_start(18)
        self.set_margin_top(18)
        self.set_margin_bottom(18)

        self.header = Gtk.Label()
        self.header.set_xalign(0)
        self.header.set_margin_bottom(12)
        self.header.get_style_context().add_class('bibtex-wizard-header')
        
        self.headerbar_subtitle = ''



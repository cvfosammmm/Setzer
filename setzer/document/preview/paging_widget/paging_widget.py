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
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango

from setzer.widgets.fixed_width_label.fixed_width_label import FixedWidthLabel


class PagingWidget(object):

    def __init__(self, preview):
        self.preview = preview
        self.view = FixedWidthLabel(160)
        self.view.layout.set_alignment(Pango.Alignment.LEFT)
        self.view.get_style_context().add_class('paging-widget')

        self.preview.view.action_bar_left.append(self.view)
        self.update_label()

        self.preview.connect('pdf_changed', self.on_pdf_changed)
        self.preview.connect('position_changed', self.on_position_changed)
        self.preview.zoom_manager.connect('zoom_level_changed', self.on_zoom_level_changed)

    def on_pdf_changed(self, preview):
        self.update_label()

    def on_position_changed(self, preview):
        self.update_label()

    def on_zoom_level_changed(self, preview):
        self.update_label()

    def update_label(self):
        if self.preview.pdf_filename != None:
            total = str(self.preview.poppler_document.get_n_pages())
        else:
            total = "0"

        if self.preview.layout != None:
            offset = self.preview.view.content.scrolling_offset_y
            current = str(self.preview.layout.get_page_by_offset(offset))
        else:
            current = "0"

        self.view.set_text(_('Page ') + current + _(' of ') + total)



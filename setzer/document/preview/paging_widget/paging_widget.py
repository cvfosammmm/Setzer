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


class PagingWidget(object):

    def __init__(self, preview, layouter):
        self.preview = preview
        self.layouter = layouter
        self.view = PagingWidgetView()

        self.preview.view.action_bar.pack_start(self.view, False, False, 0)
        self.update_number_of_pages()
        self.update_current_page()

        self.preview.connect('pdf_changed', self.on_pdf_changed)
        self.preview.connect('position_changed', self.on_position_changed)
        self.preview.zoom_manager.connect('zoom_level_changed', self.on_zoom_level_changed)

    def on_pdf_changed(self, preview):
        self.update_number_of_pages()
        self.update_current_page()

    def on_position_changed(self, preview):
        self.update_current_page()

    def on_zoom_level_changed(self, preview):
        self.update_current_page()

    def update_number_of_pages(self):
        if self.preview.pdf_filename != None:
            self.view.label_number_of_pages.set_text(str(self.preview.number_of_pages))
        else:
            self.view.label_number_of_pages.set_text("0")

    def update_current_page(self):
        if self.layouter.has_layout:
            self.view.label_current_page.set_text(str(self.layouter.get_current_page()))
        else:
            self.view.label_current_page.set_text("0")


class PagingWidgetView(Gtk.HBox):

    def __init__(self):
        Gtk.HBox.__init__(self)
        self.set_margin_left(9)

        self.pack_start(Gtk.Label(_('Page ')), False, False, 0)
        self.label_current_page = Gtk.Label('')
        self.pack_start(self.label_current_page, False, False, 0)
        self.pack_start(Gtk.Label(_(' of ')), False, False, 0)
        self.label_number_of_pages = Gtk.Label('')
        self.pack_start(self.label_number_of_pages, False, False, 0)
        self.show_all()



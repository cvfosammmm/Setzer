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
from gi.repository import Gtk

import setzer.document.preview.zoom_widget.zoom_widget_viewgtk as view


class ZoomWidget(object):

    def __init__(self, preview):
        self.preview = preview
        self.view = view.PreviewZoomWidget(self)
        self.preview.view.action_bar_right.prepend(self.view)

        self.preview.connect('pdf_changed', self.on_pdf_changed)
        self.preview.zoom_manager.connect('zoom_level_changed', self.on_zoom_level_changed)

        self.view.zoom_in_button.connect('clicked', self.on_zoom_button_clicked, 'in')
        self.view.zoom_out_button.connect('clicked', self.on_zoom_button_clicked, 'out')

        self.update_zoom_level()

        self.view.button_fit_to_width.connect('clicked', self.on_fit_to_width_button_clicked)
        self.view.button_fit_to_text_width.connect('clicked', self.on_fit_to_text_width_button_clicked)
        self.view.button_fit_to_height.connect('clicked', self.on_fit_to_height_button_clicked)
        for level, button in self.view.zoom_level_buttons.items():
            button.connect('clicked', self.on_set_zoom_button_clicked, level)

    def on_pdf_changed(self, preview):
        if self.preview.poppler_document != None:
            self.view.set_reveal_child(True)
        else:
            self.view.set_reveal_child(False)

    def on_zoom_level_changed(self, preview):
        self.update_zoom_level()

    def on_zoom_button_clicked(self, button, direction):
        if direction == 'in':
            self.preview.zoom_manager.zoom_in()
        else:
            self.preview.zoom_manager.zoom_out()

    def on_fit_to_width_button_clicked(self, button):
        self.preview.zoom_manager.set_zoom_fit_to_width_auto_offset()
        self.view.popover.popdown()

    def on_fit_to_text_width_button_clicked(self, button):
        self.preview.zoom_manager.set_zoom_fit_to_text_width()
        self.view.popover.popdown()

    def on_fit_to_height_button_clicked(self, button):
        self.preview.zoom_manager.set_zoom_fit_to_height()
        self.view.popover.popdown()

    def on_set_zoom_button_clicked(self, button, level):
        self.preview.zoom_manager.set_zoom_level_auto_offset(level)
        self.view.popover.popdown()

    def update_zoom_level(self):
        if self.preview.zoom_manager.get_zoom_level() != None:
            self.view.label.set_text('{0:.1f}%'.format(self.preview.zoom_manager.get_zoom_level() * 100))



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

import setzer.document.preview.zoom_widget.zoom_widget_viewgtk as view


class ZoomWidget(object):

    def __init__(self, preview):
        self.preview = preview
        self.view = view.PreviewZoomWidget()
        self.preview.view.action_bar.pack_end(self.view, False, False, 0)

        self.preview.connect('pdf_changed', self.on_pdf_changed)
        self.preview.connect('zoom_level_changed', self.on_zoom_level_changed)

        self.view.zoom_in_button.connect('clicked', self.on_zoom_button_clicked, 'in')
        self.view.zoom_out_button.connect('clicked', self.on_zoom_button_clicked, 'out')

        self.update_zoom_level()
        self.view.hide()

        model_button = Gtk.ModelButton()
        model_button.set_label(_('Fit to Width'))
        model_button.get_child().set_halign(Gtk.Align.START)
        model_button.connect('clicked', self.on_fit_to_width_button_clicked)
        self.view.zoom_button_box.pack_start(model_button, False, False, 0)
        model_button = Gtk.ModelButton()
        model_button.set_label(_('Fit to Text Width'))
        model_button.get_child().set_halign(Gtk.Align.START)
        model_button.connect('clicked', self.on_fit_to_text_width_button_clicked)
        self.view.zoom_button_box.pack_start(model_button, False, False, 0)
        model_button = Gtk.ModelButton()
        model_button.set_label(_('Fit to Height'))
        model_button.get_child().set_halign(Gtk.Align.START)
        model_button.connect('clicked', self.on_fit_to_height_button_clicked)
        self.view.zoom_button_box.pack_start(model_button, False, False, 0)
        separator = Gtk.SeparatorMenuItem()
        self.view.zoom_button_box.pack_start(separator, False, False, 0)
        for level in self.preview.zoom_levels:
            model_button = Gtk.ModelButton()
            model_button.set_label('{0:.0f}%'.format(level * 100))
            model_button.get_child().set_halign(Gtk.Align.START)
            model_button.connect('clicked', self.on_set_zoom_button_clicked, level)
            self.view.zoom_button_box.pack_start(model_button, False, False, 0)
        self.view.zoom_button_box.show_all()

    def on_pdf_changed(self, preview):
        if self.preview.pdf_loaded:
            self.view.set_reveal_child(True)
        else:
            self.view.set_reveal_child(False)

    def on_zoom_level_changed(self, preview):
        self.update_zoom_level()

    def on_zoom_button_clicked(self, button, direction):
        if direction == 'in':
            self.preview.zoom_in()
        else:
            self.preview.zoom_out()

    def on_fit_to_width_button_clicked(self, button):
        self.preview.set_zoom_fit_to_width_auto_offset()

    def on_fit_to_text_width_button_clicked(self, button):
        self.preview.set_zoom_fit_to_text_width()

    def on_fit_to_height_button_clicked(self, button):
        self.preview.set_zoom_fit_to_height()

    def on_set_zoom_button_clicked(self, button, level):
        self.preview.set_zoom_level_auto_offset(level)

    def update_zoom_level(self):
        if self.preview.zoom_level != None:
            self.view.label.set_text('{0:.1f}%'.format(self.preview.zoom_level * 100))
    


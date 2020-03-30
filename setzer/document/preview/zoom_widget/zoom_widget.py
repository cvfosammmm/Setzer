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

import setzer.document.preview.zoom_widget.zoom_widget_viewgtk as view


class ZoomWidget(object):

    def __init__(self, preview):
        self.preview = preview
        self.view = view.PreviewZoomWidget()
        self.preview.view.action_bar.pack_end(self.view, False, False, 0)

        self.preview.register_observer(self)

        self.view.zoom_in_button.connect('clicked', self.on_zoom_button_clicked, 'in')
        self.view.zoom_out_button.connect('clicked', self.on_zoom_button_clicked, 'out')

        self.update_zoom_level()
        self.view.hide()

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'pdf_changed':
            if self.preview.pdf_loaded:
                self.view.show_all()
            else:
                self.view.hide()

        if change_code == 'zoom_level_changed':
            self.update_zoom_level()

    def on_zoom_button_clicked(self, button, direction):
        if direction == 'in':
            self.preview.zoom_in()
        else:
            self.preview.zoom_out()

    def update_zoom_level(self):
        if self.preview.layouter.has_layout and self.preview.zoom_level != None:
            self.view.label.set_text('{0:.1f}%'.format(self.preview.zoom_level * 100))
    


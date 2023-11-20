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

from setzer.popovers.preview_zoom_level.preview_zoom_level_viewgtk import PreviewZoomLevelView


class PreviewZoomLevel(object):

    def __init__(self, popover_manager, workspace):
        self.workspace = workspace
        self.view = PreviewZoomLevelView(popover_manager)

        self.view.button_fit_to_width.connect('clicked', self.on_fit_to_width_button_clicked)
        self.view.button_fit_to_text_width.connect('clicked', self.on_fit_to_text_width_button_clicked)
        self.view.button_fit_to_height.connect('clicked', self.on_fit_to_height_button_clicked)
        for level, button in self.view.zoom_level_buttons.items():
            button.connect('clicked', self.on_set_zoom_button_clicked, level)

    def on_fit_to_width_button_clicked(self, button):
        document = self.workspace.get_root_or_active_latex_document()
        if document != None:
            document.preview.zoom_manager.set_zoom_fit_to_width_auto_offset()

    def on_fit_to_text_width_button_clicked(self, button):
        document = self.workspace.get_root_or_active_latex_document()
        if document != None:
            document.preview.zoom_manager.set_zoom_fit_to_text_width()

    def on_fit_to_height_button_clicked(self, button):
        document = self.workspace.get_root_or_active_latex_document()
        if document != None:
            document.preview.zoom_manager.set_zoom_fit_to_height()

    def on_set_zoom_button_clicked(self, button, level):
        document = self.workspace.get_root_or_active_latex_document()
        if document != None:
            document.preview.zoom_manager.set_zoom_level_auto_offset(level)



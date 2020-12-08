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
gi.require_version('PangoCairo', '1.0')
from gi.repository import Pango
from gi.repository import PangoCairo

import math

from setzer.helpers.timer import timer
from setzer.app.service_locator import ServiceLocator


class LineNumbers(object):

    def __init__(self, document, document_view):
        self.source_view = document_view.source_view

        self.font_manager = ServiceLocator.get_font_manager()

        self.size = 0
        self.visible = False
        self.update_size()

        document.gutter.add_widget(self)

        settings = ServiceLocator.get_settings()
        self.set_visibility(settings.get_value('preferences', 'show_line_numbers'))
        settings.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'settings_changed':
            section, item, value = parameter
            if (section, item) == ('preferences', 'show_line_numbers'):
                self.set_visibility(value)

    def on_click(self, event):
        return False

    #@timer
    def on_draw(self, drawing_area, ctx, lines, current_line, offset):
        layout = PangoCairo.create_layout(ctx)
        layout.set_font_description(self.font_desc)
        layout.set_width(self.size)
        layout.set_alignment(Pango.Alignment.RIGHT)

        for line in lines:
            ctx.move_to(offset + self.size, line[1])
            if line[0] == current_line:
                self.font_desc.set_weight(Pango.Weight.BOLD)
                layout.set_font_description(self.font_desc)
            else:
                self.font_desc.set_weight(Pango.Weight.NORMAL)
                layout.set_font_description(self.font_desc)
            layout.set_text(str(line[0]))
            PangoCairo.show_layout(ctx, layout)

    def update_size(self):
        self.font_desc = self.font_manager.get_font_desc()
        char_width = self.font_manager.get_char_width(self.source_view)
        self.size = math.ceil(math.log(self.source_view.get_buffer().get_line_count() + 1, 10)) * char_width

    def get_size(self):
        return self.size

    def set_visibility(self, value):
        self.visible = value
        self.source_view.queue_draw()

    def is_visible(self):
        return self.visible



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

from setzer.app.service_locator import ServiceLocator


class CodeFoldingPresenter(object):

    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.source_buffer = self.model.document.source_buffer
        self.source_gutter = self.model.document.view.source_view.get_gutter(Gtk.TextWindowType.LEFT)
        self.tag = self.source_buffer.create_tag('invisible_region', invisible=1)

        self.lines_skip_query_data = dict()

        self.source_gutter.insert(self.view, 3)
        self.view.connect('query-data', self.query_data)
        self.model.register_observer(self)

        font_manager = ServiceLocator.get_font_manager()
        font_manager.register_observer(self)
        char_width = font_manager.get_char_width(self.source_buffer.view)
        self.view.set_size(2 * char_width)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'is_enabled_changed':
            if self.model.is_enabled:
                self.show_folding_bar()
            else:
                self.hide_folding_bar()

        if change_code == 'buffer_changed':
            buffer = parameter
            for i in range(len(self.lines_skip_query_data), buffer.get_end_iter().get_line() + 1):
                self.lines_skip_query_data[i] = False

        if change_code == 'folding_regions_updated':
            self.update_line_visibility()

        if change_code == 'folding_state_changed':
            if parameter['is_folded']:
                self.hide_region(parameter)
            else:
                self.show_region(parameter)

        if change_code == 'font_string_changed':
            char_width = notifying_object.get_char_width(self.source_buffer.view)
            self.view.set_size(2 * char_width)

    def show_region(self, region):
        mark_start = region['mark_start']
        start_iter = self.source_buffer.get_iter_at_mark(mark_start)
        mark_end = region['mark_end']
        end_iter = self.source_buffer.get_iter_at_mark(mark_end)
        end_iter.forward_char()
        self.source_buffer.remove_tag(self.tag, start_iter, end_iter)
        for some_region in self.model.folding_regions.values():
            if some_region['is_folded']:
                if some_region['starting_line'] >= region['starting_line'] and some_region['ending_line'] <= region['ending_line']:
                    self.hide_region(some_region)
        self.update_line_visibility()

    def hide_region(self, region):
        mark_start = region['mark_start']
        start_iter = self.source_buffer.get_iter_at_mark(mark_start)
        mark_end = region['mark_end']
        end_iter = self.source_buffer.get_iter_at_mark(mark_end)
        end_iter.forward_char()
        self.source_buffer.apply_tag(self.tag, start_iter, end_iter)
        self.update_line_visibility()

    def update_line_visibility(self):
        for i in range(len(self.lines_skip_query_data)):
            self.lines_skip_query_data[i] = False
        for region in self.model.folding_regions.values():
            if region['is_folded']:
                for line in range(region['starting_line'] + 1, region['ending_line']):
                    self.lines_skip_query_data[line] = True
        self.source_gutter.queue_draw()

    def query_data(self, renderer, start_iter, end_iter, state):
        if self.lines_skip_query_data[start_iter.get_line()]: return
        if start_iter.get_line() in self.model.folding_regions.keys():
            if self.model.folding_regions[start_iter.get_line()]['is_folded']:
                renderer.set_icon_name('own-folded-symbolic')
            else:
                renderer.set_icon_name('own-unfolded-symbolic')
        else:
            renderer.set_icon_name('own-no-folding-symbolic')

    def show_folding_bar(self):
        self.view.set_visible(True)

    def hide_folding_bar(self):
        self.view.set_visible(False)



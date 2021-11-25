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

from setzer.helpers.timer import timer


class CodeFoldingPresenter(object):

    def __init__(self, model):
        self.model = model
        self.source_buffer = self.model.document.content.source_buffer
        self.tag = self.source_buffer.create_tag('invisible_region', invisible=1)

    def show_region(self, region):
        offset_start = region['offset_start']
        start_iter = self.source_buffer.get_iter_at_offset(offset_start)
        start_iter.forward_to_line_end()
        offset_end = region['offset_end']
        end_iter = self.source_buffer.get_iter_at_offset(offset_end)
        if not end_iter.ends_line():
            end_iter.forward_to_line_end()
        end_iter.forward_char()
        self.source_buffer.remove_tag(self.tag, start_iter, end_iter)
        for some_region in self.model.folding_regions.values():
            if some_region['is_folded']:
                if some_region['starting_line'] >= region['starting_line'] and some_region['ending_line'] <= region['ending_line']:
                    self.hide_region(some_region)

    def hide_region(self, region):
        offset_start = region['offset_start']
        start_iter = self.source_buffer.get_iter_at_offset(offset_start)
        start_iter.forward_to_line_end()
        offset_end = region['offset_end']
        end_iter = self.source_buffer.get_iter_at_offset(offset_end)
        if not end_iter.ends_line():
            end_iter.forward_to_line_end()
        end_iter.forward_char()
        self.source_buffer.apply_tag(self.tag, start_iter, end_iter)



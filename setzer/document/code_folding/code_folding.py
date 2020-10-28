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
from gi.repository import GObject

import setzer.document.code_folding.code_folding_viewgtk as code_folding_view
import setzer.document.code_folding.code_folding_controller as code_folding_controller
import setzer.document.code_folding.code_folding_presenter as code_folding_presenter
from setzer.helpers.observable import Observable


class CodeFolding(Observable):

    def __init__(self, document):
        Observable.__init__(self)

        self.is_enabled = False

        self.folding_regions = dict()
        self.folding_regions_by_region_id = dict()
        self.maximum_region_id = 0
        self.initial_folded_regions_set = False
        self.initial_folding_done = False
        self.initial_folding_regions_checked_count = 0

        self.document = document
        self.view = code_folding_view.CodeFoldingView()
        self.presenter = code_folding_presenter.CodeFoldingPresenter(self, self.view)
        self.controller = code_folding_controller.CodeFoldingController(self)

        self.on_buffer_changed(self.document.get_buffer())

    def enable_code_folding(self):
        self.is_enabled = True
        GObject.timeout_add(1, self.update_folding_regions)
        self.add_change_code('is_enabled_changed')

    def disable_code_folding(self):
        self.is_enabled = False
        for region in self.folding_regions.values():
            self.toggle_folding_region(region, show_region_regardless_of_state=True)
        self.add_change_code('is_enabled_changed')

    def toggle_folding_region(self, region, show_region_regardless_of_state=False, hide_region_regardless_of_state=False):
        if show_region_regardless_of_state:
            is_folded = False
        elif hide_region_regardless_of_state:
            is_folded = True
        else:
            is_folded = not region['is_folded']
        region['is_folded'] = is_folded
        self.add_change_code('folding_state_changed', region)

    def on_buffer_changed(self, buffer):
        self.add_change_code('buffer_changed', buffer)

    def get_folding_region_by_region_id(self, region_id):
        return self.folding_regions_by_region_id[region_id]

    def update_folding_regions(self):
        folding_regions = dict()
        folding_regions_by_region_id = dict()
        lines_with_regions = set()
        blocks = self.document.parser.get_blocks()
        if blocks == None: return self.is_enabled

        for block in blocks:
            if block[1] != None:
                start_iter = self.document.source_buffer.get_iter_at_offset(block[0])
                start_iter.forward_to_line_end()
                line_number = start_iter.get_line()
                if not line_number in lines_with_regions:
                    lines_with_regions |= {line_number}
                    end_iter = self.document.source_buffer.get_iter_at_offset(block[1])
                    if not end_iter.ends_line():
                        end_iter.forward_to_line_end()
                    marks = start_iter.get_marks()
                    block_in_buffer = False
                    for mark in marks:
                        if mark.get_name() != None and mark.get_name().startswith('folding_region_start'):
                            block_in_buffer = True
                            region_id = int(mark.get_name()[21:])
                    if block_in_buffer:
                        #if region_id in self.folding_regions_by_region_id:
                        region_dict = self.get_folding_region_by_region_id(region_id)
                        region_dict['starting_line'] = start_iter.get_line()
                        region_dict['ending_line'] = end_iter.get_line()
                        self.document.source_buffer.move_mark_by_name('folding_region_end_' + str(region_id), end_iter)
                        folding_regions_by_region_id[region_id] = region_dict
                    else:
                        mark_start = Gtk.TextMark.new('folding_region_start_' + str(self.maximum_region_id), False)
                        mark_end = Gtk.TextMark.new('folding_region_end_' + str(self.maximum_region_id), False)
                        self.document.source_buffer.add_mark(mark_start, start_iter)
                        self.document.source_buffer.add_mark(mark_end, end_iter)
                        region_dict = {'mark_start': mark_start, 'mark_end': mark_end, 'is_folded': False, 'starting_line': start_iter.get_line(), 'ending_line': end_iter.get_line(), 'id': self.maximum_region_id}
                        folding_regions_by_region_id[self.maximum_region_id] = region_dict
                        self.maximum_region_id += 1
                    folding_regions[start_iter.get_line()] = region_dict

        regions_to_delete = [region_id for region_id in self.folding_regions_by_region_id if region_id not in folding_regions_by_region_id]
        for region_id in regions_to_delete:
            region = self.folding_regions_by_region_id[region_id]
            self.toggle_folding_region(region, show_region_regardless_of_state=True)
            self.document.source_buffer.delete_mark(region['mark_start'])
            self.document.source_buffer.delete_mark(region['mark_end'])

        self.folding_regions = folding_regions
        self.folding_regions_by_region_id = folding_regions_by_region_id

        if not self.initial_folding_done:
            self.initial_folding()
        else:
            self.add_change_code('folding_regions_updated')

        return self.is_enabled

    def get_folded_regions(self):
        folded_regions = list()
        for region in self.folding_regions.values():
            if region['is_folded']:
                folded_regions.append({'starting_line': region['starting_line'], 'ending_line': region['ending_line']})
        return folded_regions

    def set_initial_folded_regions(self, folded_regions):
        self.initial_folded_regions = folded_regions
        self.initial_folded_regions_set = True

    def initial_folding(self):
        self.initial_folding_regions_checked_count += 1
        if self.initial_folded_regions_set:
            if self.initial_folded_regions != None:
                for region in self.initial_folded_regions:
                    if region['starting_line'] in self.folding_regions:
                        if region['ending_line'] == self.folding_regions[region['starting_line']]['ending_line']:
                            folding_region = self.folding_regions[region['starting_line']]
                            self.toggle_folding_region(folding_region, hide_region_regardless_of_state=True)
            self.initial_folding_done = True
        if self.initial_folding_regions_checked_count >= 3:
            self.initial_folding_done = True



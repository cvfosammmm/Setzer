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

import setzer.document.latex.code_folding.code_folding_viewgtk as code_folding_view
import setzer.document.latex.code_folding.code_folding_controller as code_folding_controller
import setzer.document.latex.code_folding.code_folding_presenter as code_folding_presenter
from setzer.helpers.observable import Observable
from setzer.helpers.timer import timer


class CodeFolding(Observable):

    def __init__(self, document):
        Observable.__init__(self)

        self.is_enabled = False

        self.blocks = list()
        self.marks_start = dict()
        self.marks_end = dict()
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

        self.document.register_observer(self)
        self.add_change_code('buffer_changed', self.document.get_buffer())

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'text_inserted':
            self.on_text_inserted(parameter)

        if change_code == 'text_deleted':
            self.on_text_deleted(parameter)

        if change_code == 'buffer_changed':
            self.add_change_code('buffer_changed', parameter)
            self.update_folding_regions()

    def enable_code_folding(self):
        self.is_enabled = True
        self.add_change_code('is_enabled_changed')

    def disable_code_folding(self):
        self.is_enabled = False
        for region in self.folding_regions.values():
            self.toggle_folding_region(region, show_region_regardless_of_state=True)
        self.add_change_code('is_enabled_changed')

    #@timer
    def on_text_deleted(self, parameter):
        buffer, start_iter, end_iter = parameter
        offset_start = start_iter.get_offset()
        offset_end = end_iter.get_offset()
        length = offset_end - offset_start
        for index in list(self.marks_start):
            if index > offset_start:
                if index >= offset_end:
                    region = self.folding_regions_by_region_id[self.marks_start[index]]
                    region['offset_start'] = index - length
                    self.marks_start[index - length] = self.marks_start[index]
                del(self.marks_start[index])
        for index in list(self.marks_end):
            if index > offset_start:
                if index >= offset_end:
                    for region_id in self.marks_end[index]:
                        region = self.folding_regions_by_region_id[region_id]
                        region['offset_end'] = index - length
                    self.marks_end[index - length] = self.marks_end[index]
                del(self.marks_end[index])

    #@timer
    def on_text_inserted(self, parameter):
        buffer, location_iter, text, text_length = parameter
        length = text_length
        offset = location_iter.get_offset() + length
        for index in reversed(list(self.marks_start)):
            if index >= offset:
                region = self.folding_regions_by_region_id[self.marks_start[index]]
                region['offset_start'] = index + length
                self.marks_start[index + length] = self.marks_start[index]
                del(self.marks_start[index])
        for index in reversed(list(self.marks_end)):
            if index >= offset:
                for region_id in self.marks_end[index]:
                    region = self.folding_regions_by_region_id[region_id]
                    region['offset_end'] = index + length
                self.marks_end[index + length] = self.marks_end[index]
                del(self.marks_end[index])

    def toggle_folding_region(self, region, show_region_regardless_of_state=False, hide_region_regardless_of_state=False):
        if show_region_regardless_of_state:
            is_folded = False
        elif hide_region_regardless_of_state:
            is_folded = True
        else:
            is_folded = not region['is_folded']
        region['is_folded'] = is_folded
        self.add_change_code('folding_state_changed', region)

    def get_folding_region_by_region_id(self, region_id):
        return self.folding_regions_by_region_id[region_id]

    #@timer
    def update_folding_regions(self):
        folding_regions = dict()
        folding_regions_by_region_id = dict()
        last_line = -1
        blocks = self.document.get_blocks()
        if not self.blocks_changed(blocks): return
        self.blocks = blocks

        for block in blocks:
            if block[1] != None:
                start_iter = self.document.source_buffer.get_iter_at_offset(block[0])
                line_start = start_iter.get_line()
                if line_start != last_line:
                    end_iter = self.document.source_buffer.get_iter_at_offset(block[1])
                    offset_start = start_iter.get_offset()
                    offset_end = end_iter.get_offset()
                    line_end = end_iter.get_line()
                    region_id = self.get_mark_start_at_offset(offset_start)
                    if region_id != None:
                        region_dict = self.get_folding_region_by_region_id(region_id)
                        region_dict['starting_line'] = line_start
                        region_dict['ending_line'] = line_end
                        region_dict['offset_end'] = offset_end
                        self.move_mark_end(region_dict['offset_end'], offset_end, region_id)
                        folding_regions_by_region_id[region_id] = region_dict
                    else:
                        self.add_mark_start(self.maximum_region_id, offset_start)
                        self.add_mark_end(self.maximum_region_id, offset_end)
                        region_dict = {'offset_start': offset_start, 'offset_end': offset_end, 'is_folded': False, 'starting_line': line_start, 'ending_line': line_end, 'id': self.maximum_region_id}
                        folding_regions_by_region_id[self.maximum_region_id] = region_dict
                        self.maximum_region_id += 1
                    folding_regions[line_start] = region_dict
                last_line = line_start

        self.delete_invalid_regions(folding_regions_by_region_id)

        self.folding_regions = folding_regions
        self.folding_regions_by_region_id = folding_regions_by_region_id

        if not self.initial_folding_done:
            self.initial_folding()
        else:
            self.add_change_code('folding_regions_updated')

    #@timer
    def delete_invalid_regions(self, folding_regions_by_region_id):
        regions_to_delete = [region_id for region_id in self.folding_regions_by_region_id if region_id not in folding_regions_by_region_id]
        for region_id in regions_to_delete:
            region = self.folding_regions_by_region_id[region_id]
            self.toggle_folding_region(region, show_region_regardless_of_state=True)
            self.delete_mark_start(region['offset_start'])
            self.delete_mark_end(region['offset_end'], region_id)

    def add_mark_start(self, region_id, offset):
        self.marks_start[offset] = region_id

    def delete_mark_start(self, offset):
        del(self.marks_start[offset])

    def get_mark_start_at_offset(self, offset):
        if offset in self.marks_start:
            return self.marks_start[offset]
        return None

    def move_mark_end(self, old_offset, new_offset, region_id):
        self.delete_mark_end(old_offset, region_id)
        self.add_mark_end(region_id, new_offset)

    def add_mark_end(self, region_id, offset):
        if offset in self.marks_end:
            self.marks_end[offset].append(region_id)
        else:
            self.marks_end[offset] = [region_id]

    def delete_mark_end(self, offset, region_id):
        if not offset in self.marks_end: return
        if len(self.marks_end[offset]) == 1:
            del(self.marks_end[offset])
        else:
            self.marks_end[offset].remove(region_id)

    def blocks_changed(self, blocks):
        if len(blocks) != len(self.blocks):
            return True
        for block_old, block_new in zip(blocks, self.blocks):
            if block_old[0] != block_new[0] or block_old[1] != block_new[1]:
                return True
        return False

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



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

from setzer.helpers.observable import Observable
from setzer.helpers.timer import timer


class CodeFolding(Observable):

    def __init__(self, document):
        Observable.__init__(self)
        self.document = document
        self.source_buffer = self.document.source_buffer
        self.tag = self.source_buffer.create_tag('invisible_region', invisible=1)

        self.region_offsets = dict()
        self.folding_regions = dict()
        self.folding_regions_by_region_id = dict()
        self.maximum_region_id = 0

        self.document.parser.connect('updated', self.on_parser_update)

    def on_parser_update(self, parser):
        region_offsets = dict()

        if parser.last_edit[0] == 'insert':
            _, location_iter, text, text_length = parser.last_edit

            length = len(text)
            offset_start = location_iter.get_offset() + length - 1
            offset_end = offset_start + 1

        elif parser.last_edit[0] == 'delete':
            _, start_iter, end_iter = parser.last_edit

            offset_start = start_iter.get_offset()
            offset_end = end_iter.get_offset()
            length = offset_start - offset_end

        for index, region_id in self.region_offsets.items():
            if index <= offset_start:
                region_offsets[index] = region_id
            elif index >= offset_end:
                index2 = index + length
                region = self.folding_regions_by_region_id[region_id]
                region['offset_start'] = index2
                region_offsets[index2] = region_id

        self.region_offsets = region_offsets

        folding_regions = dict()
        folding_regions_by_region_id = dict()
        last_line = -1

        for block in parser.symbols['blocks']:
            if block[1] != None:
                if block[2] != last_line:
                    if block[0] in self.region_offsets:
                        region_id = self.region_offsets[block[0]]
                        region_dict = self.folding_regions_by_region_id[region_id]
                        region_dict['starting_line'] = block[2]
                        region_dict['ending_line'] = block[3]
                        region_dict['offset_end'] = block[1]
                        folding_regions_by_region_id[region_id] = region_dict
                    else:
                        self.region_offsets[block[0]] = self.maximum_region_id
                        region_dict = {'offset_start': block[0], 'offset_end': block[1], 'is_folded': False, 'starting_line': block[2], 'ending_line': block[3], 'id': self.maximum_region_id}
                        folding_regions_by_region_id[self.maximum_region_id] = region_dict
                        self.maximum_region_id += 1
                    folding_regions[block[2]] = region_dict
                last_line = block[2]

        self.delete_invalid_regions(folding_regions_by_region_id)

        self.folding_regions = folding_regions
        self.folding_regions_by_region_id = folding_regions_by_region_id

    def delete_invalid_regions(self, folding_regions_by_region_id):
        regions_to_delete = [region_id for region_id in self.folding_regions_by_region_id if region_id not in folding_regions_by_region_id]
        for region_id in regions_to_delete:
            region = self.folding_regions_by_region_id[region_id]
            self.unfold(region)
            del(self.region_offsets[region['offset_start']])

    def fold(self, region):
        region['is_folded'] = True
        self.hide_region(region)

    def unfold(self, region):
        region['is_folded'] = False
        self.show_region(region)

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
        for some_region in self.folding_regions.values():
            if some_region['is_folded']:
                if some_region['starting_line'] >= region['starting_line'] and some_region['ending_line'] <= region['ending_line']:
                    self.hide_region(some_region)
        self.add_change_code('folding_state_changed', region)

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
        self.add_change_code('folding_state_changed', region)



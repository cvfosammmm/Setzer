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
        self.folding_regions = dict()

        self.document.parser.connect('finished_parsing', self.on_parser_update)

    def on_parser_update(self, parser):
        # update offsets of previous regions (they will be used
        # in the algorithm below).

        folding_regions = dict()
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
        for index, region in self.folding_regions.items():
            if index <= offset_start:
                folding_regions[index] = region
            elif index >= offset_end:
                folding_regions[index + length] = region

        # update regions from the new parsing results.
        # if the offset of a region matches a previously included region,
        # that region is assumed to be the same as the previous one:
        # it will match if it's in the same place, after the above
        # relocations are taken into account.
        # this step is important, because we want to keep track of
        # which regions are folded, so we have to transfer that
        # state to the new regions, by identifying them with previous
        # ones.

        last_line = -1
        self.folding_regions = dict()
        for block in parser.symbols['blocks']:
            if block[1] != None:
                if block[2] != last_line:
                    if block[0] in folding_regions:
                        region = folding_regions[block[0]]
                        del(folding_regions[block[0]])
                    else:
                        region = {'is_folded': False}
                    region['offset_start'] = block[0]
                    region['offset_end'] = block[1]
                    region['starting_line'] = block[2]
                    region['ending_line'] = block[3]
                    self.folding_regions[block[0]] = region
                last_line = block[2]

        # in a last step, the regions that are no longer
        # included, but were previously, are unfolded.

        for region in folding_regions.values():
            self.unfold(region)

    def get_region_by_line(self, line):
        offset = self.source_buffer.get_iter_at_line(line).iter.get_offset()
        if offset in self.folding_regions:
            return self.folding_regions[offset]
        return None

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



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

from setzer.helpers.observable import Observable
from setzer.app.service_locator import ServiceLocator
from setzer.helpers.timer import timer


class CodeFolding(Observable):

    def __init__(self, document):
        Observable.__init__(self)
        self.document = document
        self.source_buffer = self.document.source_buffer
        self.settings = ServiceLocator.get_settings()
        self.tag = self.source_buffer.create_tag('invisible_region', invisible=1)

        self.folding_regions = dict()
        self.folding_regions_by_line = dict()
        self.initial_folded_regions = None

        self.document.parser.connect('finished_parsing', self.on_parser_update)
        self.settings.connect('settings_changed', self.on_settings_changed)

    def on_settings_changed(self, settings, parameter):
        section, item, value = parameter
        if item == 'enable_code_folding' and value == False:
            for region in self.folding_regions.values():
                self.unfold(region)

    def on_parser_update(self, parser):
        # this method updates the dict of folding regions after the
        # main text changed and the parser has updated the blocks (potential
        # folding regions). the first step is to update the offsets of
        # previous folding regions (update their positions w.r.t. the
        # amount of text inserted or deleted). these updated positions
        # will be used in the algorithm further below.

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

        # now update the folding regions w.r.t. the new parsing results.
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
        self.folding_regions_by_line = dict()
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
                    self.folding_regions_by_line[block[2]] = region
                last_line = block[2]

        # in a last step, the regions that are no longer
        # included, but were previously, are unfolded.

        for region in folding_regions.values():
            self.unfold(region)

        self.initial_folding()

    def get_region_by_line(self, line):
        if line in self.folding_regions_by_line:
            return self.folding_regions_by_line[line]
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
        self.add_change_code('folding_state_changed')

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
        self.add_change_code('folding_state_changed')

    def get_folded_regions(self):
        folded_regions = list()
        for region in self.folding_regions.values():
            if region['is_folded']:
                folded_regions.append({'starting_line': region['starting_line'], 'ending_line': region['ending_line']})
        return folded_regions

    def set_initial_folded_regions(self, folded_regions):
        if self.settings.get_value('preferences', 'enable_code_folding'):
            self.initial_folded_regions = folded_regions
            self.initial_folding()

    def initial_folding(self):
        if self.initial_folded_regions != None:
            for line_range in self.initial_folded_regions:
                region = self.get_region_by_line(line_range['starting_line'])
                if region != None and line_range['ending_line'] == region['ending_line']:
                    self.fold(region)
        self.initial_folded_regions = None



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
gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GtkSource

import document.code_folding.code_folding_viewgtk as code_folding_view
import document.code_folding.code_folding_controller as code_folding_controller
import document.code_folding.code_folding_presenter as code_folding_presenter
from helpers.helpers import timer


class CodeFolding(object):

    def __init__(self, document):
        self.is_enabled = False

        self.folding_regions = dict()
        self.folding_regions_by_region_id = dict()
        self.maximum_region_id = 0

        self.document = document
        self.source_view = document.view.source_view
        self.view = code_folding_view.CodeFoldingView()
        self.presenter = code_folding_presenter.CodeFoldingPresenter(self, self.view)
        self.controller = code_folding_controller.CodeFoldingController(self, self.view)

        self.source_view.get_gutter(Gtk.TextWindowType.LEFT).insert(self.view, 3)
        self.source_view.connect('button-press-event', self.on_click)

    def enable_code_folding(self):
        self.is_enabled = True
        GObject.timeout_add(1, self.update_folding_regions)
        self.presenter.show_folding_bar()

    def disable_code_folding(self):
        self.is_enabled = False
        for region in self.folding_regions.values():
            self.toggle_folding_region(region, show_region_regardless_of_state=True)
        self.presenter.hide_folding_bar()

    def on_click(self, widget, event):
        x, y = self.source_view.window_to_buffer_coords(Gtk.TextWindowType.LEFT, event.x, event.y)
        if event.window == self.source_view.get_window(Gtk.TextWindowType.LEFT):
            line_iter, line_top = self.source_view.get_line_at_y(y)
            line_number = line_iter.get_line()
            if x >= -18 and line_number in self.folding_regions:
                if event.type == Gdk.EventType.BUTTON_PRESS:
                    self.toggle_folding_region(self.folding_regions[line_number])
                return True
            return False
        else:
            return False

    def toggle_folding_region(self, region, show_region_regardless_of_state=False):
        if show_region_regardless_of_state:
            is_folded = False
        else:
            is_folded = not region['is_folded']
        source_buffer = self.document.source_buffer
        mark_start = region['mark_start']
        mark_end = region['mark_end']
        start_iter = source_buffer.get_iter_at_mark(mark_start)
        end_iter = source_buffer.get_iter_at_mark(mark_end)
        end_iter.forward_char()
        if is_folded:
            source_buffer.apply_tag_by_name('invisible', start_iter, end_iter)
        else:
            source_buffer.remove_tag_by_name('invisible', start_iter, end_iter)
        region['is_folded'] = is_folded
        self.query_data()

    def query_data(self):
        start_iter = self.document.source_buffer.get_start_iter()
        end_iter = self.document.source_buffer.get_end_iter()
        self.view.query_data(start_iter, end_iter, GtkSource.GutterRendererState.NORMAL)

    def get_folding_region_by_region_id(self, region_id):
        return self.folding_regions_by_region_id[region_id]

    #@timer
    def update_folding_regions(self):
        folding_regions = dict()
        folding_regions_by_region_id = dict()
        blocks = self.document.parser.get_blocks()
        if blocks == None: return self.is_enabled

        for block in blocks:
            start_iter = self.document.source_buffer.get_iter_at_offset(block[0])
            start_iter.forward_to_line_end()
            end_iter = self.document.source_buffer.get_iter_at_offset(block[1])
            end_iter.forward_to_line_end()
            marks = start_iter.get_marks()
            block_in_buffer = False
            for mark in marks:
                if mark.get_name() != None and mark.get_name().startswith('folding_region_start'):
                    block_in_buffer = True
                    region_id = int(mark.get_name()[21:])
            if block_in_buffer:
                region_dict = self.get_folding_region_by_region_id(region_id)
                region_dict['starting_line'] = start_iter.get_line()
                region_dict['ending_line'] = end_iter.get_line()
                folding_regions_by_region_id[region_id] = region_dict
            else:
                mark_start = Gtk.TextMark.new('folding_region_start_' + str(self.maximum_region_id), False)
                mark_end = Gtk.TextMark.new('folding_region_end_' + str(self.maximum_region_id), False)
                self.document.source_buffer.add_mark(mark_start, start_iter)
                self.document.source_buffer.add_mark(mark_end, end_iter)
                region_dict = {'mark_start': mark_start, 'mark_end': mark_end, 'is_folded': False, 'starting_line': start_iter.get_line(), 'ending_line': end_iter.get_line()}
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
        self.query_data()

        return self.is_enabled



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

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango, Graphene

import re
import os.path

from setzer.app.color_manager import ColorManager
from setzer.app.service_locator import ServiceLocator
from setzer.popovers.helpers.popover import Popover
from setzer.widgets.search_entry.search_entry import SearchEntry


class DocumentChooserView(Popover):
    
    def __init__(self, popover_manager):
        Popover.__init__(self, popover_manager)

        self.set_width(414)

        self.box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.box.get_style_context().add_class('documentchooser')

        self.search_entry = SearchEntry()

        self.auto_suggest_entries = list()
        self.auto_suggest_list = DocumentChooserList()
        self.auto_suggest_list.set_size_request(398, -1)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_child(self.auto_suggest_list)
        self.scrolled_window.get_style_context().add_class('frame')
        self.scrolled_window.set_min_content_height(10 * self.auto_suggest_list.line_height + 120)
        self.scrolled_window.set_min_content_width(398)
        self.scrolled_window.set_max_content_height(10 * self.auto_suggest_list.line_height + 120)
        self.scrolled_window.set_max_content_width(398)
        
        self.not_found_slate = Gtk.CenterBox()
        self.not_found_slate.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.not_found_slate.get_style_context().add_class('not_found')
        self.not_found_slate.get_style_context().add_class('frame')

        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 12)
        image = Gtk.Image.new_from_icon_name('system-search-symbolic')
        image.set_pixel_size(64)
        image.set_vexpand(False)
        box.append(image)
        box.append(Gtk.Label.new(_('No results')))

        outer_box = Gtk.CenterBox()
        outer_box.set_orientation(Gtk.Orientation.VERTICAL)
        outer_box.set_center_widget(box)

        self.not_found_slate.set_center_widget(outer_box)

        self.other_documents_button = Gtk.Button.new_with_label(_('Other Documents') + '...')
        self.other_documents_button.set_can_focus(False)

        self.notebook = Gtk.Notebook()
        self.notebook.set_can_focus(False)
        self.notebook.set_show_tabs(False)
        self.notebook.set_show_border(False)
        self.notebook.insert_page(self.scrolled_window, None, 0)
        self.notebook.insert_page(self.not_found_slate, None, 1)
        self.notebook.set_current_page(0)
        self.notebook.set_vexpand(True)

        self.box.append(self.search_entry)
        self.box.append(self.notebook)
        self.box.append(self.other_documents_button)

        self.add_widget(self.box)

    def update_items(self, items):
        self.auto_suggest_entries = []
        for item in items:
            entry = DocumentChooserEntry(item[0], item[1])
            self.auto_suggest_entries.append(entry)
        self.search_filter()

    def search_filter(self):
        query = self.search_entry.get_text()
        count = 0

        entries = list()
        for entry in self.auto_suggest_entries:
            if query == '':
                entry.highlight_search(query)
                count += 1
            elif query.lower() in entry.filename.lower() or query.lower() in entry.folder.lower():
                entry.highlight_search(query)
                entries.append(entry)
                count += 1
        if query == '': entries = self.auto_suggest_entries

        self.auto_suggest_list.set_data(entries)
        self.update_search_entry(count)

    def update_search_entry(self, results_count):
        if results_count == 0:
            self.search_entry.get_style_context().add_class('error')
            self.notebook.set_current_page(1)
        else:
            self.search_entry.get_style_context().remove_class('error')
            self.notebook.set_current_page(0)


class DocumentChooserList(Gtk.Widget):
    
    def __init__(self):
        Gtk.Widget.__init__(self)

        self.items = []
        self.hover_item = None
        self.selected_index = None
        self.offset_start = 0
        self.offset_end = 0

        self.font = self.get_pango_context().get_font_description()
        self.font_size = self.font.get_size() / Pango.SCALE

        self.layout_header = Pango.Layout(self.get_pango_context())
        self.layout_header.set_ellipsize(Pango.EllipsizeMode.START)
        self.layout_header.set_width(374 * Pango.SCALE)
        self.layout_header.set_font_description(self.font)
        self.layout_header.set_text('\n')

        self.layout_subheader = Pango.Layout(self.get_pango_context())
        self.layout_subheader.set_ellipsize(Pango.EllipsizeMode.START)
        self.layout_subheader.set_width(374 * Pango.SCALE)
        self.font.set_size(10 * Pango.SCALE)
        self.layout_subheader.set_font_description(self.font)
        self.layout_subheader.set_text('\n')

        self.line_height = self.layout_header.get_extents()[0].height / Pango.SCALE
        self.subline_height = self.layout_subheader.get_extents()[0].height / Pango.SCALE
        self.layout_header.set_spacing((25 + self.line_height) * Pango.SCALE)
        self.layout_subheader.set_spacing((25 + 2 * self.line_height - self.subline_height) * Pango.SCALE)

    def do_snapshot(self, snapshot):
        fg_color = ColorManager.get_ui_color('view_fg_color')
        fg_color_light = ColorManager.get_ui_color('fg_color_light')
        bg_color = ColorManager.get_ui_color('view_bg_color')
        hover_color = ColorManager.get_ui_color('view_hover_color')
        active_color = ColorManager.get_ui_color('list_selection_color')
        active_hover_color = ColorManager.get_ui_color('list_selection_hover_color')
        border_color = ColorManager.get_ui_color('borders')

        snapshot.append_color(bg_color, Graphene.Rect().init(0, 0, self.get_allocated_width(), self.get_allocated_height()))

        if self.hover_item != None and self.selected_index != None and self.hover_item == self.selected_index:
            highlight_color = active_hover_color
            snapshot.append_color(highlight_color, Graphene.Rect().init(0, self.hover_item * (25 + 2 * self.line_height), self.get_allocated_width(), 25 + 2 * self.line_height))
        if self.hover_item != None and self.hover_item != self.selected_index:
            highlight_color = hover_color
            snapshot.append_color(highlight_color, Graphene.Rect().init(0, self.hover_item * (25 + 2 * self.line_height), self.get_allocated_width(), 25 + 2 * self.line_height))
        if self.selected_index != None and self.hover_item != self.selected_index:
            highlight_color = active_color
            snapshot.append_color(highlight_color, Graphene.Rect().init(0, self.selected_index * (25 + 2 * self.line_height), self.get_allocated_width(), 25 + 2 * self.line_height))

        filename_text = ''
        folder_text = ''
        for item in self.items:
            filename_text += item.filename_markup + '\n'
            folder_text += item.folder_markup + '\n'

        snapshot.translate(Graphene.Point().init(6, 8))
        self.layout_header.set_markup(filename_text)
        snapshot.append_layout(self.layout_header, fg_color)

        snapshot.translate(Graphene.Point().init(0, self.line_height + 10))
        self.layout_subheader.set_markup(folder_text)
        snapshot.append_layout(self.layout_subheader, fg_color_light)
        
        snapshot.translate(Graphene.Point().init(-6, self.line_height + 7))
        for i in range(len(self.items)):
            snapshot.append_color(border_color, Graphene.Rect().init(0, 0, self.get_allocated_width(), 1))
            snapshot.translate(Graphene.Point().init(0, 2 * self.line_height + 25))

    def set_data(self, items):
        self.items = items
        self.set_size_request(386, len(items) * (2 * self.line_height + 25))

        self.queue_draw()


class DocumentChooserEntry(object):

    def __init__(self, folder, filename):
        self.filename = filename
        self.filename_markup = filename
        self.folder = folder
        self.folder_markup = self.folder
        
    def highlight_search(self, query):
        if query != '':
            markup = self.filename
            counter = 0
            for pos in re.finditer(re.escape(query.lower()), self.filename.lower()):
                markup = markup[:pos.start()+counter] + '<b>' + markup[pos.start()+counter:pos.end()+counter] + '</b>' + markup[pos.end()+counter:]
                counter += 7
        else: 
            markup = self.filename
        self.filename_markup = markup
        if query != '':
            markup = self.folder
            counter = 0
            for pos in re.finditer(re.escape(query.lower()), self.folder.lower()):
                markup = markup[:pos.start()+counter] + '<span alpha="100%"><b>' + markup[pos.start()+counter:pos.end()+counter] + '</b></span>' + markup[pos.end()+counter:]
                counter += 33
        else:
            markup = self.folder
        self.folder_markup = markup



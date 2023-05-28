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
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Pango

import re


class DocumentChooser(Gtk.Popover):
    ''' GEdit like document chooser widget '''
    
    def __init__(self):
        Gtk.Popover.__init__(self)
        
        self.search_entry = Gtk.SearchEntry()
        self.icon_name = self.search_entry.get_icon_name(Gtk.EntryIconPosition.PRIMARY)
        
        self.auto_suggest_entries = list()
        self.auto_suggest_box = Gtk.ListBox()
        self.auto_suggest_box.set_size_request(398, -1)
        
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.add(self.auto_suggest_box)
        self.scrolled_window.get_style_context().add_class('frame')
        self.scrolled_window.set_min_content_height(295)
        self.scrolled_window.set_min_content_width(398)
        self.scrolled_window.set_max_content_height(295)
        self.scrolled_window.set_max_content_width(398)
        
        self.not_found_slate = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.not_found_slate.get_style_context().add_class('not_found')
        self.not_found_slate.get_style_context().add_class('frame')
        box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        image = Gtk.Image.new_from_icon_name('system-search-symbolic', Gtk.IconSize.MENU)
        image.set_pixel_size(64)
        box.pack_start(image, True, True, 0)
        box.pack_start(Gtk.Label(_('No results')), False, False, 0)
        outer_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        outer_box.set_center_widget(box)
        self.not_found_slate.set_center_widget(outer_box)
        
        self.other_documents_button = Gtk.Button.new_with_label(_('Other Documents') + '...')
        self.other_documents_button.set_action_name('win.open-document-dialog')

        self.notebook = Gtk.Notebook()
        self.notebook.set_show_tabs(False)
        self.notebook.set_show_border(False)
        self.notebook.insert_page(self.scrolled_window, None, 0)
        self.notebook.insert_page(self.not_found_slate, None, 1)
        self.notebook.set_current_page(0)

        self.box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.box.pack_start(self.search_entry, False, False, 0)
        self.box.pack_start(self.notebook, True, True, 0)
        self.box.pack_start(self.other_documents_button, False, False, 0)
        self.box.show_all()
        self.add(self.box)

        self.get_style_context().add_class('documentchooser')
        
    def update_autosuggest(self, items):
        for entry in self.auto_suggest_box.get_children():
            self.auto_suggest_box.remove(entry)
        for item in items:
            entry = DocumentChooserEntry(item[0], item[1])
            self.auto_suggest_box.add(entry)
        return self.search_filter()

    def search_filter(self):
        query = self.search_entry.get_buffer().get_text()
        count = 0
        for entry in self.auto_suggest_box.get_children():
            if query == '':
                if count < 5:
                    entry.highlight_search(query)
                    entry.show_all()
                    count += 1
            elif query.lower() in entry.filename.lower() or query.lower() in entry.folder.lower():
                entry.highlight_search(query)
                entry.show_all()
                count += 1
            else:
                entry.hide()
        self.update_search_entry(count)
        
    def update_search_entry(self, results_count):
        if results_count == 0:
            self.search_entry.get_style_context().add_class('error')
            self.search_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, 'face-uncertain-symbolic')
            self.notebook.set_current_page(1)
        else:
            self.search_entry.get_style_context().remove_class('error')
            self.search_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, self.icon_name)
            self.notebook.set_current_page(0)


class DocumentChooserEntry(Gtk.ListBoxRow):
    ''' an item in the document chooser '''
    
    def __init__(self, folder, filename):
        Gtk.ListBoxRow.__init__(self)
        
        self.filename = filename
        self.filename_label = Gtk.Label()
        self.filename_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.filename_label.set_use_markup(True)
        self.filename_label.set_markup(self.filename)
        self.filename_label.set_xalign(0)
        self.folder = folder
        self.folder_label = Gtk.Label()
        self.folder_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.folder_label.set_use_markup(True)
        self.folder_label.set_markup(self.folder)
        self.folder_label.set_xalign(0)
        self.folder_label.get_style_context().add_class('folder')
        
        self.box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.add(self.box)
        
        self.box.pack_start(self.filename_label, False, False, 0)
        self.box.pack_start(self.folder_label, False, False, 0)
        
    def highlight_search(self, query):
        if query != '':
            markup = self.filename
            counter = 0
            for pos in re.finditer(re.escape(query.lower()), self.filename.lower()):
                markup = markup[:pos.start()+counter] + '<b>' + markup[pos.start()+counter:pos.end()+counter] + '</b>' + markup[pos.end()+counter:]
                counter += 7
        else: 
            markup = self.filename
        self.filename_label.set_markup(markup)
        if query != '':
            markup = self.folder
            counter = 0
            for pos in re.finditer(re.escape(query.lower()), self.folder.lower()):
                markup = markup[:pos.start()+counter] + '<span alpha="100%"><b>' + markup[pos.start()+counter:pos.end()+counter] + '</b></span>' + markup[pos.end()+counter:]
                counter += 33
        else:
            markup = self.folder
        self.folder_label.set_markup(markup)



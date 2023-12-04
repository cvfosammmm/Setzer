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
from gi.repository import Gtk, Gdk

import re
import os.path

from setzer.popovers.document_chooser.document_chooser_viewgtk import DocumentChooserView
from setzer.app.color_manager import ColorManager
from setzer.app.service_locator import ServiceLocator


class DocumentChooser(object):

    def __init__(self, popover_manager, workspace):
        self.popover_manager = popover_manager
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()
        self.view = DocumentChooserView(popover_manager)

        self.workspace.connect('update_recently_opened_documents', self.on_update_recently_opened_documents)
        self.popover_manager.connect('popdown', self.on_popover_popdown)
        self.popover_manager.connect('popup', self.on_popover_popup)

        self.view.search_entry.connect('changed', self.on_document_chooser_search_changed)
        self.view.search_entry.connect('activate', self.on_search_activate)
        self.view.search_entry.connect('stop_search', self.on_stop_search)
        self.view.search_entry.connect('next_match', self.on_next_match)
        self.view.search_entry.connect('previous_match', self.on_previous_match)

        motion_controller = Gtk.EventControllerMotion()
        motion_controller.connect('enter', self.on_enter)
        motion_controller.connect('motion', self.on_hover)
        motion_controller.connect('leave', self.on_leave)
        self.view.auto_suggest_list.add_controller(motion_controller)

        event_controller = Gtk.GestureClick()
        event_controller.connect('pressed', self.on_button_press)
        event_controller.connect('released', self.on_button_release)
        event_controller.set_button(1)
        self.view.auto_suggest_list.add_controller(event_controller)

        self.view.other_documents_button.connect('clicked', self.on_other_docs_clicked)

    def update_first_item_index(self):
        if self.view.auto_suggest_list.selected_index == None: return

        adjustment = self.view.scrolled_window.get_vadjustment()
        item_height = 2 * self.view.auto_suggest_list.line_height + 25
        page_size = adjustment.get_page_size()
        offset = adjustment.get_value()
        if offset > self.view.auto_suggest_list.selected_index * item_height:
            adjustment.set_value(self.view.auto_suggest_list.selected_index * item_height)
        if offset < (self.view.auto_suggest_list.selected_index + 1) * item_height - page_size:
            adjustment.set_value((self.view.auto_suggest_list.selected_index + 1) * item_height - page_size)

    def on_enter(self, controller, x, y):
        self.update_hover_state(y)

    def on_hover(self, controller, x, y):
        self.update_hover_state(y)

    def on_leave(self, controller):
        self.view.auto_suggest_list.hover_item = None
        self.view.auto_suggest_list.queue_draw()

    def on_button_press(self, event_controller, n_press, x, y):
        self.view.auto_suggest_list.selected_index = self.view.auto_suggest_list.hover_item
        self.view.auto_suggest_list.queue_draw()

    def on_button_release(self, event_controller, n_press, x, y):
        if self.view.auto_suggest_list.hover_item != None and self.view.auto_suggest_list.hover_item == self.view.auto_suggest_list.selected_index:
            item = self.view.auto_suggest_list.items[self.view.auto_suggest_list.hover_item]
            self.popover_manager.popdown()
            filename = item.folder + '/' + item.filename
            self.workspace.open_document_by_filename(filename)
        self.view.auto_suggest_list.selected_index = None

    def update_hover_state(self, y):
        item_num = int((y) // (25 + 2 * self.view.auto_suggest_list.line_height))

        if item_num < 0 or item_num > (len(self.view.auto_suggest_list.items) - 1):
            self.view.auto_suggest_list.hover_item = None
        else:
            self.view.auto_suggest_list.hover_item = item_num
        self.view.auto_suggest_list.queue_draw()

    def on_update_recently_opened_documents(self, workspace, recently_opened_documents):
        items = list()
        data = recently_opened_documents.values()
        for item in sorted(data, key=lambda val: -val['date']):
            items.append(os.path.split(item['filename']))
        self.view.update_items(items)

    def on_popover_popup(self, name):
        if name != 'open_document': return

        self.view.search_entry.grab_focus()
        self.view.auto_suggest_list.selected_index = None

    def on_popover_popdown(self, name):
        if name != 'open_document': return

        self.view.auto_suggest_list.hover_item = None
        self.view.auto_suggest_list.selected_index = None
        self.view.search_entry.set_text('')
        active_document = self.workspace.get_active_document()
        if active_document != None:
            active_document.view.source_view.grab_focus()

    def on_document_chooser_search_changed(self, search_entry):
        self.view.search_filter()
        self.view.auto_suggest_list.selected_index = None

    def on_search_activate(self, search_entry=None):
        if self.view.auto_suggest_list.selected_index != None:
            item = self.view.auto_suggest_list.items[self.view.auto_suggest_list.selected_index]
            filename = item.folder + '/' + item.filename
            self.workspace.open_document_by_filename(filename)
            self.popover_manager.popdown()

    def on_next_match(self, search_entry=None):
        no_items = len(self.view.auto_suggest_list.items)
        if self.view.auto_suggest_list.selected_index == None and no_items > 0:
            self.view.auto_suggest_list.selected_index = 0
        elif no_items > 0:
            self.view.auto_suggest_list.selected_index = (self.view.auto_suggest_list.selected_index + 1) % no_items
        self.update_first_item_index()
        self.view.auto_suggest_list.queue_draw()

    def on_previous_match(self, search_entry=None):
        no_items = len(self.view.auto_suggest_list.items)
        if self.view.auto_suggest_list.selected_index == None and no_items > 0:
            self.view.auto_suggest_list.selected_index = no_items - 1
        elif no_items > 0:
            self.view.auto_suggest_list.selected_index = (self.view.auto_suggest_list.selected_index - 1) % no_items
        self.update_first_item_index()
        self.view.auto_suggest_list.queue_draw()

    def on_stop_search(self, search_entry=None):
        self.popover_manager.popdown()

    def on_other_docs_clicked(self, button):
        self.workspace.actions.actions['open-document-dialog'].activate()
        self.popover_manager.popdown()



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

from workspace.build_log.build_log_viewgtk import *
from workspace.build_log.build_log_presenter import *
from helpers.observable import *
from app.service_locator import ServiceLocator


class BuildLog(Observable):

    def __init__(self, workspace):
        Observable.__init__(self)
        self.workspace = workspace
        self.settings = ServiceLocator.get_settings()
        self.document = None

        self.items = list()
        self.symbols = {'Badbox': 'own-badbox-symbolic', 'Error': 'dialog-error-symbolic', 'Warning': 'dialog-warning-symbolic'}

        self.view = ServiceLocator.get_main_window().build_log
        self.presenter = BuildLogPresenter(self, self.view)
        self.view.list.connect('row-activated', self.on_build_log_row_activated)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'document_state_change' and parameter == 'idle':
            if notifying_object == self.document:
                self.update_items(True)

    def set_document(self, document):
        self.document = document
        self.update_items()
        self.document.register_observer(self)

    def update_items(self, just_built=False):
        self.clear_items()
        for item in self.document.build_log_items:
            self.add_item(item[0], item[1], item[2], item[3])
        self.signal_finish_adding()

        if just_built and self.has_items(self.settings.get_value('preferences', 'autoshow_build_log')):
            self.workspace.set_show_build_log(True)

    def on_build_log_row_activated(self, box, row, data=None):
        if self.document == None: return

        item = row.get_child()
        if item.filename == self.document.get_filename():
            buff = self.document.get_buffer()
            if buff != None:
                line_number = item.line_number - 1
                if line_number >= 0:
                    buff.place_cursor(buff.get_iter_at_line(line_number))
                self.document.view.source_view.scroll_mark_onscreen(buff.get_insert())
                self.document.view.source_view.grab_focus()
        else:
            if item.filename != None:
                document_candidate = self.workspace.get_document_by_filename(item.filename)
                if document_candidate != None:
                    self.workspace.set_active_document(document_candidate)
                else:
                    self.workspace.create_document_from_filename(item.filename, True)
                buff = self.workspace.active_document.get_buffer()
                if buff != None:
                    line_number = item.line_number - 1
                    if line_number >= 0:
                        buff.place_cursor(buff.get_iter_at_line(line_number))
                    self.workspace.active_document.view.source_view.scroll_mark_onscreen(buff.get_insert())
                    self.workspace.active_document.view.source_view.grab_focus()

    def add_item(self, item_type, filename, line_number, message):
        item = [item_type, filename, line_number, message]
        self.items.append(item)
        self.add_change_code('build_log_new_item', item)

    def signal_finish_adding(self):
        self.add_change_code('build_log_finished_adding', self.document.has_been_built)

    def clear_items(self):
        self.items = list()
        self.add_change_code('build_log_cleared_items', None)
        
    def has_items(self, types='all'):
        if types == 'errors':
            for item in self.items:
                if item[0] == 'Error':
                    return True
            return False
        elif types == 'errors_warnings':
            for item in self.items:
                if item[0] == 'Error' or item[0] == 'Warning':
                    return True
            return False
        elif types == 'all':
            for item in self.items:
                if item[0] == 'Error' or item[0] == 'Warning' or item[0] == 'Badbox':
                    return True
            return False
        else:
            return False

    def count_items(self, types='all'):
        count = 0
        if types == 'errors':
            for item in self.items:
                if item[0] == 'Error':
                    count += 1
        elif types == 'errors_warnings':
            for item in self.items:
                if item[0] == 'Error' or item[0] == 'Warning':
                    count += 1
        elif types == 'all':
            for item in self.items:
                if item[0] == 'Error' or item[0] == 'Warning' or item[0] == 'Badbox':
                    count += 1
        elif types == 'warnings':
            for item in self.items:
                if item[0] == 'Warning':
                    count += 1
        elif types == 'badboxes':
            for item in self.items:
                if item[0] == 'Badbox':
                    count += 1
        return count



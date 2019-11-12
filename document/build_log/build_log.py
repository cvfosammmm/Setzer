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

from document.build_log.build_log_viewgtk import *
from document.build_log.build_log_presenter import *
from helpers.observable import *


class BuildLog(Observable):

    def __init__(self, document):
        Observable.__init__(self)
        self.document = document

        self.items = list()
        self.symbols = {'Badbox': 'own-badbox-symbolic', 'Error': 'dialog-error-symbolic', 'Warning': 'dialog-warning-symbolic'}

        self.view = BuildLogView()
        self.presenter = BuildLogPresenter(self, self.view)

    def add_item(self, item_type, filename, line_number, message):
        item = [item_type, filename, line_number, message]
        self.items.append(item)
        self.add_change_code('build_log_new_item', item)

    def signal_finish_adding(self):
        self.add_change_code('build_log_finished_adding', None)

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



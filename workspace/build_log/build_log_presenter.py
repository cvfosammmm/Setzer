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


class BuildLogPresenter(object):
    ''' Mediator between build log and view. '''
    
    def __init__(self, build_log, build_log_view):
        self.build_log = build_log
        self.view = build_log_view
        self.set_header_data(0, 0, False)
        self.build_log.register_observer(self)

    '''
    *** notification handlers, get called by observed document
    '''

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'build_log_new_item':
            item = parameter
            symbols = {'Badbox': 'own-badbox-symbolic', 'Error': 'dialog-error-symbolic', 'Warning': 'dialog-warning-symbolic'}
            row = BuildLogRowView(symbols[item[0]], item[0], item[1].rsplit('/', 1)[1], "Line " + str(item[2]), item[3])
            self.view.list.prepend(row)

        if change_code == 'build_log_finished_adding':
            self.set_header_data(self.build_log.count_items('errors'), self.build_log.count_items('warnings') + self.build_log.count_items('badboxes'), True)
            self.view.list.show_all()
            for row in self.view.list:
                message_type = row.get_child().label_message_type.get_text()
                line_number = row.get_child().line_number

                if message_type != 'Error': return
                elif line_number >= 0:
                    row.activate()
                    return

        if change_code == 'build_log_cleared_items':
            for entry in self.view.list.get_children():
                self.view.list.remove(entry)

    def set_header_data (self, errors, warnings, tried_building=False):
        if tried_building:
            if errors == 0:
                if warnings == 0:
                    self.view.header_label.set_markup('<b>Building successful</b> (no warnings or badboxes).')
                else:
                    self.view.header_label.set_markup('<b>Building successful</b> (' + str(warnings) + ' warning' + ('s' if warnings > 1 else '') + ' or badbox' + ('es' if warnings > 1 else '') + ').')
            else:
                if warnings == 0:
                    self.view.header_label.set_markup('<b>Building failed with ' + str(errors) + ' error' + ('s' if errors > 1 else '') + '</b> (no warnings or badboxes).')
                else:
                    self.view.header_label.set_markup('<b>Building failed with ' + str(errors) + ' error' + ('s' if errors > 1 else '') + '</b> (' + str(warnings) + ' warning' + ('s' if warnings > 1 else '') + ' or badbox' + ('es' if warnings > 1 else '') + ').')
        else:
            self.view.header_label.set_markup('')
    


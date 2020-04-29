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

from gettext import ngettext

import setzer.workspace.build_log.build_log_viewgtk as build_log_view


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
            row = build_log_view.BuildLogRowView(item[0], item[2], item[3], item[4], item[5])
            self.view.list.prepend(row)

        if change_code == 'build_log_finished_adding':
            self.set_header_data(self.build_log.count_items('errors'), self.build_log.count_items('warnings') + self.build_log.count_items('badboxes'), parameter)
            self.view.list.show_all()

        if change_code == 'build_log_cleared_items':
            for entry in self.view.list.get_children():
                self.view.list.remove(entry)

    def set_header_data(self, errors, warnings, tried_building=False):
        if tried_building:
            if self.build_log.document.build_time != None:
                time_string = '{:.2f}s, '.format(self.build_log.document.build_time)
            else:
                time_string = ''
            str_errors = ngettext('error', 'errors', errors)
            str_warnings = ngettext('warning', 'warnings', warnings)
            str_badboxes = ngettext('badbox', 'badboxes', warnings)
            if errors == 0:
                if warnings == 0:
                    self.view.header_label.set_markup('<b>' + _('Building successful') + '</b> (' + time_string + _('no warnings or badboxes') + ').')
                else:
                    self.view.header_label.set_markup('<b>' + _('Building successful') + '</b> (' + time_string + _('{amount} {str_warnings} or {str_badboxes}').format(amount=str(warnings),str_warnings=str_warnings,str_badboxes=str_badboxes) + ').')
            else:
                if warnings == 0:
                    self.view.header_label.set_markup('<b>' + _('Building failed with {amount} {str_errors}').format(amount=str(errors),str_errors=str_errors) + '</b> (' + _('no warnings or badboxes') + ').')
                else:
                    self.view.header_label.set_markup('<b>' + _('Building failed with {amount} {str_errors}').format(amount=str(errors),str_errors=str_errors) + '</b> (' + _('{amount} {str_warnings} or {str_badboxes}').format(amount=str(warnings),str_warnings=str_warnings,str_badboxes=str_badboxes) + ').')
        else:
            self.view.header_label.set_markup('')
    


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
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango

import os.path

import setzer.workspace.build_log.build_log_viewgtk as build_log_view
import setzer.helpers.drawing as drawing_helper
from setzer.helpers.timer import timer


class BuildLogPresenter(object):
    ''' Mediator between build log and view. '''
    
    def __init__(self, build_log, build_log_view):
        self.build_log = build_log
        self.view = build_log_view

        self.set_header_data(0, 0, False)

        self.build_log.connect('build_log_finished_adding', self.on_build_log_finished_adding)
        self.build_log.connect('hover_item_changed', self.on_hover_item_changed)
        self.view.scrolled_window.get_vadjustment().connect('value-changed', self.on_scroll)

        self.max_width = -1
        self.height = -1

    def on_scroll(self, adjustment, *arguments):
        self.update_list()

    def on_build_log_finished_adding(self, build_log, has_been_built):
        num_errors = self.build_log.count_items('errors')
        num_others = self.build_log.count_items('warnings') + self.build_log.count_items('badboxes')
        self.set_header_data(num_errors, num_others, has_been_built)
        self.view.scrolled_window.get_vadjustment().set_value(0)
        self.view.scrolled_window.get_hadjustment().set_value(0)
        self.update_list()

    def on_hover_item_changed(self, build_log):
        self.view.list.hover_item = build_log.hover_item
        self.update_list()

    #@timer
    def update_list(self):
        value = self.view.scrolled_window.get_vadjustment().get_value()
        page_size = self.view.scrolled_window.get_vadjustment().get_page_size()
        self.view.list.set_data(self.build_log.items, value, value + page_size)

    def set_header_data(self, errors, warnings, tried_building=False):
        if tried_building:
            if self.build_log.document.build_system.build_time != None:
                time_string = '{:.2f}s, '.format(self.build_log.document.build_system.build_time)
            else:
                time_string = ''

            str_errors = ngettext('Building failed with {amount} error', 'Building failed with {amount} errors', errors)
            str_warnings = ngettext('{amount} warning or badbox', '{amount} warnings or badboxes', warnings)

            if errors == 0:
                markup = '<b>' + _('Building successful') + '</b> (' + time_string
            else:
                markup = '<b>' + str_errors.format(amount=str(errors)) + '</b> ('

            if warnings == 0:
                markup += _('no warnings or badboxes') 
            else:
                markup += str_warnings.format(amount=str(warnings))

            markup += ').'
            self.view.header_label.set_markup(markup)
        else:
            self.view.header_label.set_markup('')



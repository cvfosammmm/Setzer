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
from gi.repository import Gtk

import setzer.workspace.help_panel.help_panel_viewgtk as help_panel_view

class HelpPanelPresenter(object):

    def __init__(self, help_panel, view):
        self.help_panel = help_panel
        self.view = view

        self.help_panel.register_observer(self)

        self.view.content.load_uri(self.help_panel.current_uri)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'search_query_changed':
            results_list = self.help_panel.search_results
            for item in self.view.search_result_items:
                self.view.search_results.remove(item)
            self.view.search_result_items = list()
            if results_list:
                for item in results_list:
                    list_item = help_panel_view.SearchResultView(item)
                    self.view.search_results.prepend(list_item)
                    self.view.search_result_items.append(list_item)
                self.view.search_results.show_all()
            else:
                pass

        elif change_code == 'uri_changed':
            if self.view.content.get_uri() != parameter:
                self.view.content.load_uri(parameter)
            self.view.search_button.set_active(False)



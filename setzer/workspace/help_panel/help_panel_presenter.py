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

import setzer.workspace.help_panel.help_panel_viewgtk as help_panel_view


class HelpPanelPresenter(object):

    def __init__(self, help_panel, view):
        self.help_panel = help_panel
        self.view = view

        self.help_panel.connect('search_query_changed', self.on_search_query_changed)
        self.help_panel.connect('uri_changed', self.on_uri_changed)

        self.view.content.load_uri(self.help_panel.current_uri)

    def on_search_query_changed(self, help_panel):
        results_list = self.help_panel.search_results
        for item in self.view.search_result_items:
            self.view.search_results.remove(item)
        self.view.search_result_items = list()
        if results_list:
            self.view.search_entry.get_style_context().remove_class('error')
            for item in reversed(results_list):
                list_item = help_panel_view.SearchResultView(item)
                self.view.search_results.prepend(list_item)
                self.view.search_result_items.append(list_item)
        elif self.help_panel.query != '':
            self.view.search_entry.get_style_context().add_class('error')
        else:
            self.view.search_entry.get_style_context().remove_class('error')

    def on_uri_changed(self, help_panel, uri):
        if self.view.content.get_uri() != uri:
            self.view.content.load_uri(uri)
        self.view.search_button.set_active(False)



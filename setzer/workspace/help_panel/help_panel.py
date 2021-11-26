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
gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2
from gi.repository import GLib

import os.path
import pickle

from setzer.helpers.observable import Observable
import setzer.workspace.help_panel.help_panel_controller as help_panel_controller
import setzer.workspace.help_panel.help_panel_presenter as help_panel_presenter
from setzer.app.service_locator import ServiceLocator


class HelpPanel(Observable):

    def __init__(self, workspace):
        Observable.__init__(self)

        self.workspace = workspace
        self.view = ServiceLocator.get_main_window().help_panel

        self.path = 'file://' + os.path.join(ServiceLocator.get_resources_path(), 'help')
        self.home_uri = self.path + '/latex2e_0.html'
        self.current_uri = self.home_uri

        with open(os.path.join(ServiceLocator.get_resources_path(), 'help', 'search_index.pickle'), 'rb') as filehandle:
            self.search_index = pickle.load(filehandle)

        self.search_results_blank = list()
        self.search_results = self.search_results_blank
        self.query = ''

        GLib.idle_add(self.activate, priority=GLib.PRIORITY_LOW)

    def activate(self):
        self.view.settings = WebKit2.Settings()
        self.view.settings.set_enable_java(False)
        self.view.settings.set_enable_javascript(False)
        self.view.settings.set_enable_javascript_markup(False)
        self.view.settings.set_enable_plugins(False)
        self.view.settings.set_enable_developer_extras(False)
        self.view.settings.set_enable_page_cache(False)

        self.view.content = WebKit2.WebView.new_with_settings(self.view.settings)
        self.view.content.set_can_focus(False)

        self.view.stack.add_named(self.view.content, 'content')
        self.view.stack.add_named(self.view.search_widget, 'search')

        self.view.show_all()

        self.controller = help_panel_controller.HelpPanelController(self, self.view)
        self.presenter = help_panel_presenter.HelpPanelPresenter(self, self.view)

        self.add_change_code('search_query_changed')

    def set_uri(self, uri):
        self.current_uri = uri
        self.add_change_code('uri_changed', uri)

    def set_uri_by_search_item(self, uri_ending, text, location):
        self.current_uri = self.path + '/' + uri_ending

        self.search_results_blank = [item for item in self.search_results_blank if (item[0] != uri_ending or item[1] != text or item[2] != location)]
        self.search_results_blank.append([uri_ending, text, location])

        if len(self.search_results_blank) > 8:
            self.search_results_blank.pop()

        self.add_change_code('uri_changed', self.current_uri)

    def set_search_query(self, query):
        self.query = query
        if query == '':
            self.search_results = self.search_results_blank
        else:
            words = query.split()
            self.search_results = list()
            for item in self.search_index:
                if len(self.search_results) == 8: break

                found = True
                for word in words:
                    if item[0].find(word.lower()) == -1:
                        found = False
                        break
                if found:
                    headline = item[2]
                    headline = headline.replace('&gt;', '>').replace('&lt;', '<').replace('&quot;', '"').replace('&amp;', '&')
                    location = item[3]
                    location = location.replace('&gt;', '>').replace('&lt;', '<').replace('&quot;', '"').replace('&amp;', '&')
                    for word in words:
                        headline = headline.replace(word, '•' + word + '◆').replace(word.lower(), '•' + word.lower() + '◆').replace(word.title(), '•' + word.title() + '◆')
                        location = location.replace(word, '•' + word + '◆').replace(word.lower(), '•' + word.lower() + '◆').replace(word.title(), '•' + word.title() + '◆')
                    headline = headline.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;').replace('•', '<b>').replace('◆', '</b>')
                    location = location.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;').replace('•', '<b>').replace('◆', '</b>')
                    self.search_results.append([item[1], headline, location])
        self.add_change_code('search_query_changed')



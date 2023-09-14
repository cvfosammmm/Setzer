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
gi.require_versions({'Gtk': '4.0', 'WebKit': '6.0'})
from gi.repository import WebKit, Gtk

import setzer.workspace.help_panel.help_panel_viewgtk as help_panel_view
from setzer.app.service_locator import ServiceLocator
from setzer.app.color_manager import ColorManager


class HelpPanelPresenter(object):

    def __init__(self, help_panel, view):
        self.help_panel = help_panel
        self.view = view

        self.help_panel.connect('search_query_changed', self.on_search_query_changed)
        self.help_panel.connect('uri_changed', self.on_uri_changed)

        self.view.content.load_uri(self.help_panel.current_uri)

        self.update_colors()
        ServiceLocator.get_settings().connect('settings_changed', self.on_settings_changed)

    def on_settings_changed(self, settings, parameter):
        section, item, value = parameter

        if item == 'color_scheme':
            self.update_colors()

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

    def update_colors(self):
        css = '''body {margin: 1em; margin-top: 0px; padding-top: 1px; background: @view_bg_color; color: @view_fg_color; }
a {color: @link_color; }
a:visited {color: @link_color_visited; }
a:active {color: @link_color_active; }
a.external:after {text-decoration: underline; text-decoration-color: @view_bg_color; content: ' 🡭'; }'''
        css = css.replace('@view_bg_color', ColorManager.get_ui_color_string('view_bg_color'))
        css = css.replace('@view_fg_color', ColorManager.get_ui_color_string('view_fg_color'))
        css = css.replace('@link_color', ColorManager.get_ui_color_string('link_color'))
        css = css.replace('@link_color_visited', ColorManager.get_ui_color_string('link_color_visited'))
        css = css.replace('@link_color_active', ColorManager.get_ui_color_string('link_color_active'))

        style_sheet = WebKit.UserStyleSheet.new(css, WebKit.UserContentInjectedFrames.ALL_FRAMES, WebKit.UserStyleLevel.USER, None, None)

        self.view.user_content_manager.add_style_sheet(style_sheet)



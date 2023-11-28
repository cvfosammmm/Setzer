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
gi.require_version('WebKit', '6.0')
from gi.repository import WebKit

import webbrowser
import _thread as thread


class HelpPanelController(object):

    def __init__(self, help_panel, view):
        self.help_panel = help_panel
        self.view = view

        self.view.content.connect('decide-policy', self.on_policy_decision)
        self.view.content.connect('context-menu', self.on_context_menu)

        self.view.content.get_back_forward_list().connect('changed', self.on_back_forward_list_changed)
        self.view.back_button.connect('clicked', self.on_back_button_clicked)
        self.view.next_button.connect('clicked', self.on_next_button_clicked)
        self.view.up_button.connect('clicked', self.on_up_button_clicked)
        self.view.home_button.connect('clicked', self.on_home_button_clicked)
        self.view.search_button.connect('toggled', self.on_search_button_toggled)
        self.view.search_entry.connect('changed', self.on_search_entry_changed)
        self.view.search_entry.connect('stop_search', self.on_search_stopped)

        self.view.search_results.connect('row-activated', self.on_search_result_activated)

    def on_back_button_clicked(self, button):
        self.view.search_button.set_active(False)
        self.view.content.go_back()

    def on_next_button_clicked(self, button):
        self.view.search_button.set_active(False)
        self.view.content.go_forward()

    def on_up_button_clicked(self, button):
        self.view.search_button.set_active(False)
        if self.view.content.get_uri() != self.help_panel.current_uri.split('#')[0] + '#':
            self.view.content.load_uri(self.help_panel.current_uri.split('#')[0] + '#')
        else:
            self.view.content.load_uri(self.help_panel.current_uri.split('#')[0] + '#top')

    def on_home_button_clicked(self, button):
        self.view.search_button.set_active(False)
        self.view.content.load_uri(self.help_panel.home_uri)

    def on_search_button_toggled(self, button):
        if button.get_active():
            self.view.stack.set_visible_child_name('search')
            self.view.search_entry.set_text('')
            self.view.search_entry.grab_focus()
            self.help_panel.set_search_query(self.view.search_entry.get_text())
        else:
            self.view.stack.set_visible_child_name('content')
            self.help_panel.workspace.presenter.focus_active_document()

    def on_search_entry_changed(self, entry):
        self.help_panel.set_search_query(entry.get_text())

    def on_search_stopped(self, entry):
        self.view.search_button.set_active(False)

    def on_search_result_activated(self, box, row):
        self.help_panel.set_uri_by_search_item(row.uri_ending, row.text_label.get_text(), row.location_label.get_text())

    def on_back_forward_list_changed(self, back_forward_list, item_added=None, items_removed=None):
        self.view.back_button.set_sensitive(self.view.content.can_go_back())
        self.view.next_button.set_sensitive(self.view.content.can_go_forward())

    def on_policy_decision(self, view, decision, decision_type, user_data=None):
        na = WebKit.PolicyDecisionType.NAVIGATION_ACTION
        nwa = WebKit.PolicyDecisionType.NEW_WINDOW_ACTION
        ra = WebKit.PolicyDecisionType.RESPONSE
        if decision_type == na or decision_type == nwa:
            uri = decision.get_navigation_action().get_request().get_uri()
            if uri.startswith(self.help_panel.path):
                self.help_panel.set_uri(uri)
                return True
            else:
                thread.start_new_thread(webbrowser.open_new_tab, (uri,))
                decision.ignore()
                return True
        elif decision_type == ra:
            return False

    def on_context_menu(self, view, menu, event, hit_test_result, user_data=None):
        return True



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
gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2

import webbrowser


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

    def on_back_button_clicked(self, button):
        self.view.content.go_back()

    def on_next_button_clicked(self, button):
        self.view.content.go_forward()

    def on_up_button_clicked(self, button):
        if self.view.content.get_uri() != self.help_panel.uri + '#':
            self.view.content.load_uri(self.help_panel.uri + '#')
        else:
            self.view.content.load_uri(self.help_panel.uri + '#top')

    def on_back_forward_list_changed(self, back_forward_list, item_added=None, items_removed=None):
        self.view.back_button.set_sensitive(self.view.content.can_go_back())
        self.view.next_button.set_sensitive(self.view.content.can_go_forward())

    def on_policy_decision(self, view, decision, decision_type, user_data=None):
        na = WebKit2.PolicyDecisionType.NAVIGATION_ACTION
        nwa = WebKit2.PolicyDecisionType.NEW_WINDOW_ACTION
        ra = WebKit2.PolicyDecisionType.RESPONSE
        if decision_type == na or decision_type == nwa:
            uri = decision.get_navigation_action().get_request().get_uri()
            if uri.startswith(self.help_panel.uri):
                return False
            else:
                webbrowser.open_new_tab(uri)
                decision.ignore()
                return True
        elif decision_type == ra:
            return False

    def on_context_menu(self, view, menu, event, hit_test_result, user_data=None):
        return True



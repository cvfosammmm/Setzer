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

from setzer.widgets.search_entry.search_entry import SearchEntry


class HelpPanelView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('help')

        self.action_bar = Gtk.CenterBox()
        self.action_bar.set_size_request(-1, 37)
        self.action_bar_left = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.action_bar_right = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.action_bar.set_start_widget(self.action_bar_left)
        self.action_bar.set_end_widget(self.action_bar_right)

        self.home_button = Gtk.Button.new_from_icon_name('go-home-symbolic')
        self.home_button.set_tooltip_text(_('Home'))
        self.home_button.get_style_context().add_class('flat')
        self.home_button.set_can_focus(False)
        self.action_bar_left.append(self.home_button)

        self.up_button = Gtk.Button.new_from_icon_name('go-up-symbolic')
        self.up_button.set_tooltip_text(_('Top'))
        self.up_button.get_style_context().add_class('flat')
        self.up_button.set_can_focus(False)
        self.action_bar_left.append(self.up_button)

        self.back_button = Gtk.Button.new_from_icon_name('go-previous-symbolic')
        self.back_button.set_tooltip_text(_('Back'))
        self.back_button.get_style_context().add_class('flat')
        self.back_button.set_can_focus(False)
        self.action_bar_left.append(self.back_button)

        self.next_button = Gtk.Button.new_from_icon_name('go-next-symbolic')
        self.next_button.set_tooltip_text(_('Forward'))
        self.next_button.get_style_context().add_class('flat')
        self.next_button.set_can_focus(False)
        self.action_bar_left.append(self.next_button)

        self.search_button = Gtk.ToggleButton()
        self.search_button.set_icon_name('edit-find-symbolic')
        self.search_button.set_tooltip_text(_('Find'))
        self.search_button.get_style_context().add_class('flat')
        self.search_button.set_can_focus(False)
        self.action_bar_right.append(self.search_button)

        self.append(self.action_bar)

        self.search_widget = Gtk.CenterBox()
        self.search_widget.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.search_vbox = Gtk.CenterBox()
        self.search_vbox.set_orientation(Gtk.Orientation.VERTICAL)
        self.search_vbox.set_margin_start(18)
        self.search_vbox.set_margin_end(18)
        self.search_entry = SearchEntry()
        self.search_entry.set_size_request(360, -1)
        self.search_entry.set_margin_bottom(21)
        self.search_result_items = list()
        self.search_results = Gtk.ListBox()
        self.search_results.set_size_request(300, 359)
        self.search_results.set_can_focus(False)
        self.search_results.set_selection_mode(Gtk.SelectionMode.NONE)
        self.search_results.set_margin_start(26)
        self.search_results.set_margin_end(26)
        self.search_content_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.search_content_box.append(self.search_entry)
        self.search_content_box.append(self.search_results)
        self.search_vbox.set_center_widget(self.search_content_box)
        self.search_widget.set_center_widget(self.search_vbox)

        self.content = WebKit.WebView()
        self.user_content_manager = self.content.get_user_content_manager()

        self.settings = self.content.get_settings()
        self.settings.set_enable_javascript(False)
        self.settings.set_enable_javascript_markup(False)
        self.settings.set_enable_developer_extras(False)
        self.settings.set_enable_page_cache(False)

        self.stack = Gtk.Stack()
        self.stack.set_vexpand(True)
        self.stack.add_named(self.content, 'content')
        self.stack.add_named(self.search_widget, 'search')

        self.append(self.stack)

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE
                     
    def do_get_preferred_width(self):
        return 396, 500


class SearchResultView(Gtk.ListBoxRow):

    def __init__(self, data):
        Gtk.ListBoxRow.__init__(self)
        self.set_can_focus(False)
        self.uri_ending = data[0]
        self.box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.box.set_margin_start(3)
        self.box.set_margin_end(3)
        self.text_label = Gtk.Label()
        self.text_label.set_markup(data[1])
        self.text_label.set_xalign(0)
        self.location_label = Gtk.Label()
        self.location_label.set_markup('' + data[2] + '')
        self.location_label.set_xalign(0)
        self.location_label.get_style_context().add_class('location-label')
        self.box.append(self.text_label)
        self.box.append(self.location_label)
        self.set_child(self.box)



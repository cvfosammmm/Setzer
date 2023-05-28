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
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class HelpPanelView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self, orientation = Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('help')

        self.action_bar = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.action_bar.set_size_request(-1, 37)

        self.home_button = Gtk.Button.new_from_icon_name('go-home-symbolic', Gtk.IconSize.MENU)
        self.home_button.set_tooltip_text(_('Home'))
        self.home_button.get_style_context().add_class('flat')
        self.home_button.set_can_focus(False)
        self.action_bar.pack_start(self.home_button, False, False, 0)

        self.up_button = Gtk.Button.new_from_icon_name('go-up-symbolic', Gtk.IconSize.MENU)
        self.up_button.set_tooltip_text(_('Top'))
        self.up_button.get_style_context().add_class('flat')
        self.up_button.set_can_focus(False)
        self.action_bar.pack_start(self.up_button, False, False, 0)

        self.back_button = Gtk.Button.new_from_icon_name('go-previous-symbolic', Gtk.IconSize.MENU)
        self.back_button.set_tooltip_text(_('Back'))
        self.back_button.get_style_context().add_class('flat')
        self.back_button.set_can_focus(False)
        self.action_bar.pack_start(self.back_button, False, False, 0)

        self.next_button = Gtk.Button.new_from_icon_name('go-next-symbolic', Gtk.IconSize.MENU)
        self.next_button.set_tooltip_text(_('Forward'))
        self.next_button.get_style_context().add_class('flat')
        self.next_button.set_can_focus(False)
        self.action_bar.pack_start(self.next_button, False, False, 0)

        self.search_button = Gtk.ToggleButton()
        self.search_button.set_image(Gtk.Image.new_from_icon_name('edit-find-symbolic', Gtk.IconSize.MENU))
        self.search_button.set_tooltip_text(_('Find'))
        self.search_button.get_style_context().add_class('flat')
        self.search_button.set_can_focus(False)
        self.action_bar.pack_end(self.search_button, False, False, 0)

        self.pack_start(self.action_bar, False, False, 0)

        self.search_widget = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.search_vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.search_vbox.set_margin_left(18)
        self.search_vbox.set_margin_right(18)
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_size_request(360, -1)
        self.search_entry.set_margin_bottom(21)
        self.search_result_items = list()
        self.search_results = Gtk.ListBox()
        self.search_results.set_size_request(300, 359)
        self.search_results.set_can_focus(False)
        self.search_results.set_selection_mode(Gtk.SelectionMode.NONE)
        self.search_results.set_margin_left(26)
        self.search_results.set_margin_right(26)
        self.search_content_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.search_content_box.pack_start(self.search_entry, False, False, 0)
        self.search_content_box.pack_start(self.search_results, False, False, 0)
        self.search_vbox.set_center_widget(self.search_content_box)
        self.search_widget.set_center_widget(self.search_vbox)

        self.settings = None
        self.content = None

        self.stack = Gtk.Stack()
        self.pack_start(self.stack, True, True, 0)

        self.show_all()

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE
                     
    def do_get_preferred_width(self):
        return 396, 500


class SearchResultView(Gtk.ListBoxRow):

    def __init__(self, data):
        Gtk.ListBoxRow.__init__(self)
        self.set_can_focus(False)
        self.uri_ending = data[0]
        self.box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.box.set_margin_left(3)
        self.box.set_margin_right(3)
        self.text_label = Gtk.Label()
        self.text_label.set_markup(data[1])
        self.text_label.set_xalign(0)
        self.location_label = Gtk.Label()
        self.location_label.set_markup('' + data[2] + '')
        self.location_label.set_xalign(0)
        self.location_label.get_style_context().add_class('location-label')
        self.box.pack_start(self.text_label, False, False, 0)
        self.box.pack_start(self.location_label, False, False, 0)
        self.add(self.box)
        self.show_all()



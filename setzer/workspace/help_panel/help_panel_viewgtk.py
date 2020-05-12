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
from gi.repository import Gtk
from gi.repository import WebKit2


class HelpPanelView(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)
        self.get_style_context().add_class('help')

        self.action_bar = Gtk.HBox()
        self.action_bar.set_size_request(-1, 37)

        self.up_button = Gtk.Button.new_from_icon_name('go-up-symbolic', Gtk.IconSize.MENU)
        self.up_button.set_tooltip_text(_('Find'))
        self.up_button.get_style_context().add_class('flat')
        self.up_button.set_can_focus(False)
        self.action_bar.pack_start(self.up_button, False, False, 0)

        self.back_button = Gtk.Button.new_from_icon_name('go-previous-symbolic', Gtk.IconSize.MENU)
        self.back_button.set_tooltip_text(_('Find'))
        self.back_button.get_style_context().add_class('flat')
        self.back_button.set_can_focus(False)
        self.action_bar.pack_start(self.back_button, False, False, 0)

        self.next_button = Gtk.Button.new_from_icon_name('go-next-symbolic', Gtk.IconSize.MENU)
        self.next_button.set_tooltip_text(_('Find'))
        self.next_button.get_style_context().add_class('flat')
        self.next_button.set_can_focus(False)
        self.action_bar.pack_start(self.next_button, False, False, 0)

        self.pack_start(self.action_bar, False, False, 0)

        self.content = WebKit2.WebView()
        self.content.set_can_focus(False)
        self.pack_start(self.content, True, True, 0)

        self.show_all()

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.CONSTANT_SIZE
                     
    def do_get_preferred_width(self):
        return 300, 500



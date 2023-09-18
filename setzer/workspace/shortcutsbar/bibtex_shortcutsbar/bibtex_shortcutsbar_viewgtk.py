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
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


class BibTeXShortcutsbar(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.get_style_context().add_class('shortcutsbar')
        self.set_can_focus(False)

        self.top_icons = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.right_icons = Gtk.Box()
        self.right_icons.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.center_icons = Gtk.CenterBox()
        self.center_icons.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.center_icons.set_hexpand(True)

        self.populate_right_toolbar()

        self.append(self.top_icons)
        self.append(self.center_icons)
        self.append(self.right_icons)

    def populate_right_toolbar(self):
        self.button_search = Gtk.ToggleButton()
        self.button_search.set_icon_name('edit-find-symbolic')
        self.button_search.set_tooltip_text(_('Find') + ' (' + _('Ctrl') + '+F)')
        self.button_search.get_style_context().add_class('flat')
        self.button_search.get_style_context().add_class('scbar')
        self.right_icons.append(self.button_search)

        self.button_replace = Gtk.ToggleButton()
        self.button_replace.set_icon_name('edit-find-replace-symbolic')
        self.button_replace.set_tooltip_text(_('Find and Replace') + ' (' + _('Ctrl') + '+H)')
        self.button_replace.get_style_context().add_class('flat')
        self.button_replace.get_style_context().add_class('scbar')
        self.right_icons.append(self.button_replace)

        self.button_more = Gtk.MenuButton()
        self.button_more.set_icon_name('view-more-symbolic')
        self.button_more.get_style_context().add_class('flat')
        self.button_more.get_style_context().add_class('scbar')
        self.button_more.set_tooltip_text(_('Document'))
        self.right_icons.append(self.button_more)



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


class ShortcutsBarBottom(Gtk.Toolbar):

    def __init__(self):
        Gtk.Toolbar.__init__(self)

        self.set_style(Gtk.ToolbarStyle.ICONS)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_icon_size(Gtk.IconSize.SMALL_TOOLBAR)
        self.get_style_context().add_class('bottom')

        self.button_build_log = Gtk.ToggleToolButton()
        self.button_build_log.set_icon_name('utilities-system-monitor-symbolic')
        self.button_build_log.set_tooltip_text('Build log (F8)')
        self.insert(self.button_build_log, 0)

        self.button_find_and_replace = Gtk.ToggleToolButton()
        self.button_find_and_replace.set_icon_name('edit-find-replace-symbolic')
        self.button_find_and_replace.set_tooltip_text('Find and Replace (Ctrl+H)')
        self.insert(self.button_find_and_replace, 0)
        
        self.button_find = Gtk.ToggleToolButton()
        self.button_find.set_icon_name('edit-find-symbolic')
        self.button_find.set_tooltip_text('Find (Ctrl+F)')
        self.insert(self.button_find, 0)
        self.show_all()


class WizardButton(Gtk.ToolButton):

    def __init__(self):
        Gtk.ToolButton.__init__(self)
        self.icon_widget = Gtk.HBox()
        icon = Gtk.Image.new_from_icon_name('own-wizard-symbolic', Gtk.IconSize.MENU)
        icon.set_margin_left(4)
        self.icon_widget.pack_start(icon, False, False, 0)
        self.label_revealer = Gtk.Revealer()
        label = Gtk.Label('New Document Wizard')
        label.set_margin_left(6)
        label.set_margin_right(4)
        self.label_revealer.add(label)
        self.label_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
        self.label_revealer.set_reveal_child(True)
        self.icon_widget.pack_start(self.label_revealer, False, False, 0)

        self.set_icon_widget(self.icon_widget)
        self.set_action_name('win.show-document-wizard')
        self.set_focus_on_click(False)
        self.set_tooltip_text('Create a template document')
        self.show_all()



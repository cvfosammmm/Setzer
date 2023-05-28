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


class PageEditor(object):

    def __init__(self, preferences, settings):
        self.view = PageEditorView()
        self.preferences = preferences
        self.settings = settings

    def init(self):
        self.view.option_spaces_instead_of_tabs.set_active(self.settings.get_value('preferences', 'spaces_instead_of_tabs'))
        self.view.option_spaces_instead_of_tabs.connect('toggled', self.preferences.on_check_button_toggle, 'spaces_instead_of_tabs')

        self.view.tab_width_spinbutton.set_value(self.settings.get_value('preferences', 'tab_width'))
        self.view.tab_width_spinbutton.connect('value-changed', self.preferences.spin_button_changed, 'tab_width')

        self.view.option_show_line_numbers.set_active(self.settings.get_value('preferences', 'show_line_numbers'))
        self.view.option_show_line_numbers.connect('toggled', self.preferences.on_check_button_toggle, 'show_line_numbers')

        self.view.option_line_wrapping.set_active(self.settings.get_value('preferences', 'enable_line_wrapping'))
        self.view.option_line_wrapping.connect('toggled', self.preferences.on_check_button_toggle, 'enable_line_wrapping')

        self.view.option_code_folding.set_active(self.settings.get_value('preferences', 'enable_code_folding'))
        self.view.option_code_folding.connect('toggled', self.preferences.on_check_button_toggle, 'enable_code_folding')

        self.view.option_highlight_current_line.set_active(self.settings.get_value('preferences', 'highlight_current_line'))
        self.view.option_highlight_current_line.connect('toggled', self.preferences.on_check_button_toggle, 'highlight_current_line')

        self.view.option_highlight_matching_brackets.set_active(self.settings.get_value('preferences', 'highlight_matching_brackets'))
        self.view.option_highlight_matching_brackets.connect('toggled', self.preferences.on_check_button_toggle, 'highlight_matching_brackets')


class PageEditorView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self, orientation = Gtk.Orientation.VERTICAL)

        self.set_margin_start(18)
        self.set_margin_end(18)
        self.set_margin_top(18)
        self.set_margin_bottom(18)
        self.get_style_context().add_class('preferences-page')

        label = Gtk.Label()
        label.set_markup('<b>' + _('Tab Stops') + '</b>')
        label.set_xalign(0)
        label.set_margin_bottom(6)
        self.pack_start(label, False, False, 0)

        self.option_spaces_instead_of_tabs = Gtk.CheckButton(_('Insert spaces instead of tabs'))
        self.pack_start(self.option_spaces_instead_of_tabs, False, False, 0)

        label = Gtk.Label()
        label.set_markup(_('Set Tab Width:'))
        label.set_xalign(0)
        label.set_margin_top(18)
        label.set_margin_bottom(6)
        self.pack_start(label, False, False, 0)
        box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.tab_width_spinbutton = Gtk.SpinButton.new_with_range(1, 8, 1)
        box.pack_start(self.tab_width_spinbutton, False, False, 0)
        self.pack_start(box, False, False, 0)

        label = Gtk.Label()
        label.set_markup('<b>' + _('Line Numbers') + '</b>')
        label.set_xalign(0)
        label.set_margin_top(18)
        label.set_margin_bottom(6)
        self.pack_start(label, False, False, 0)
        self.option_show_line_numbers = Gtk.CheckButton(_('Show line numbers'))
        self.pack_start(self.option_show_line_numbers, False, False, 0)

        label = Gtk.Label()
        label.set_markup('<b>' + _('Line Wrapping') + '</b>')
        label.set_xalign(0)
        label.set_margin_top(18)
        label.set_margin_bottom(6)
        self.pack_start(label, False, False, 0)
        self.option_line_wrapping = Gtk.CheckButton(_('Enable line wrapping'))
        self.pack_start(self.option_line_wrapping, False, False, 0)

        label = Gtk.Label()
        label.set_markup('<b>' + _('Code Folding') + '</b>')
        label.set_xalign(0)
        label.set_margin_top(18)
        label.set_margin_bottom(6)
        self.pack_start(label, False, False, 0)
        self.option_code_folding = Gtk.CheckButton(_('Enable code folding'))
        self.pack_start(self.option_code_folding, False, False, 0)

        label = Gtk.Label()
        label.set_markup('<b>' + _('Highlighting') + '</b>')
        label.set_xalign(0)
        label.set_margin_top(18)
        label.set_margin_bottom(6)
        self.pack_start(label, False, False, 0)
        self.option_highlight_current_line = Gtk.CheckButton(_('Highlight current line'))
        self.pack_start(self.option_highlight_current_line, False, False, 0)
        self.option_highlight_matching_brackets = Gtk.CheckButton(_('Highlight matching brackets'))
        self.pack_start(self.option_highlight_matching_brackets, False, False, 0)



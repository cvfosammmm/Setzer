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


class PageAutocomplete(object):

    def __init__(self, preferences, settings):
        self.view = PageAutocompleteView()
        self.preferences = preferences
        self.settings = settings

    def init(self):
        self.view.option_autocomplete.set_active(self.settings.get_value('preferences', 'enable_autocomplete'))
        self.view.option_autocomplete.connect('toggled', self.preferences.on_check_button_toggle, 'enable_autocomplete')

        self.view.option_bracket_completion.set_active(self.settings.get_value('preferences', 'enable_bracket_completion'))
        self.view.option_bracket_completion.connect('toggled', self.preferences.on_check_button_toggle, 'enable_bracket_completion')

        self.view.option_selection_brackets.set_active(self.settings.get_value('preferences', 'bracket_selection'))
        self.view.option_selection_brackets.connect('toggled', self.preferences.on_check_button_toggle, 'bracket_selection')

        self.view.option_tab_jump_brackets.set_active(self.settings.get_value('preferences', 'tab_jump_brackets'))
        self.view.option_tab_jump_brackets.connect('toggled', self.preferences.on_check_button_toggle, 'tab_jump_brackets')

        self.view.option_update_matching_blocks.set_active(self.settings.get_value('preferences', 'update_matching_blocks'))
        self.view.option_update_matching_blocks.connect('toggled', self.preferences.on_check_button_toggle, 'update_matching_blocks')


class PageAutocompleteView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.set_margin_start(18)
        self.set_margin_end(18)
        self.set_margin_top(18)
        self.set_margin_bottom(18)
        self.get_style_context().add_class('preferences-page')

        label = Gtk.Label()
        label.set_markup('<b>' + _('LaTeX Commands') + '</b>')
        label.set_xalign(0)
        label.set_margin_bottom(6)
        self.append(label)

        self.option_autocomplete = Gtk.CheckButton.new_with_label(_('Suggest matching LaTeX Commands'))
        self.append(self.option_autocomplete)

        label = Gtk.Label()
        label.set_markup('<b>' + _('Others') + '</b>')
        label.set_xalign(0)
        label.set_margin_top(18)
        label.set_margin_bottom(6)
        self.append(label)

        self.option_bracket_completion = Gtk.CheckButton.new_with_label(_('Automatically add closing brackets'))
        self.append(self.option_bracket_completion)

        self.option_selection_brackets = Gtk.CheckButton.new_with_label(_('Add brackets to selected text, instead of replacing it with them'))
        self.append(self.option_selection_brackets)

        label = Gtk.Label()
        label.set_markup(_('Jump over closing brackets with <tt>Tab</tt>'))
        self.option_tab_jump_brackets = Gtk.CheckButton()
        self.option_tab_jump_brackets.set_child(label)
        self.append(self.option_tab_jump_brackets)

        label = Gtk.Label()
        label.set_markup(_('Update matching <tt>begin</tt> / <tt>end</tt> blocks'))
        self.option_update_matching_blocks = Gtk.CheckButton()
        self.option_update_matching_blocks.set_child(label)
        self.append(self.option_update_matching_blocks)



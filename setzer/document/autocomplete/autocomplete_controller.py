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
from gi.repository import Gtk, Gdk

from setzer.app.service_locator import ServiceLocator


class AutocompleteController(object):

    def __init__(self, autocomplete, document):
        self.autocomplete = autocomplete
        self.document = document
        self.source_buffer = document.source_buffer
        self.adjustment = self.document.view.scrolled_window.get_vadjustment()

        key_controller = Gtk.EventControllerKey()
        key_controller.connect('key-pressed', self.on_keypress)
        key_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.document.view.source_view.add_controller(key_controller)

        self.document.connect('changed', self.on_document_change)
        self.source_buffer.connect('notify::cursor-position', self.on_cursor_position_change)
        self.adjustment.connect('changed', self.on_adjustment_change)
        self.adjustment.connect('value-changed', self.on_adjustment_value_change)

    def on_keypress(self, controller, keyval, keycode, state):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if ServiceLocator.get_regex_object('[a-zA-Z]\Z').match(Gdk.keyval_name(keyval)) or keyval == Gdk.keyval_from_name('asterisk') or keyval == Gdk.keyval_from_name('BackSpace') or keyval == Gdk.keyval_from_name('Delete'):
            if state & modifiers == 0:
                if not self.autocomplete.is_active:
                    if self.autocomplete.handle_keypress_inside_begin_or_end(keyval):
                        return True

        if keyval in [Gdk.keyval_from_name('Tab'), Gdk.keyval_from_name('ISO_Left_Tab')]:
            if state & modifiers == 0:
                if self.autocomplete.is_active:
                    self.autocomplete.tab()
                    return True
                else:
                    self.autocomplete.activate_if_possible()
                    self.autocomplete.widget.queue_draw()
                    if self.autocomplete.is_active:
                        return True
                    elif self.autocomplete.jump_over_closing_bracket():
                        return True
                    elif self.autocomplete.select_next_placeholder():
                        return True
                    elif self.autocomplete.placeholder_selected():
                        return True
            elif state & modifiers == Gdk.ModifierType.SHIFT_MASK:
                if not self.autocomplete.is_active:
                    if self.autocomplete.select_previous_placeholder():
                        return True

        if keyval == Gdk.keyval_from_name('Return'):
            if state & modifiers == 0:
                if self.autocomplete.is_active:
                    self.autocomplete.submit()
                    return True

        if keyval == Gdk.keyval_from_name('Escape'):
            if state & modifiers == 0:
                self.autocomplete.deactivate()
                self.autocomplete.widget.queue_draw()
                return True

        if keyval == Gdk.keyval_from_name('Down'):
            if state & modifiers == 0:
                if self.autocomplete.is_active:
                    self.autocomplete.select_next()
                    self.autocomplete.widget.queue_draw()
                    return True

        if keyval == Gdk.keyval_from_name('Up'):
            if state & modifiers == 0:
                if self.autocomplete.is_active:
                    self.autocomplete.select_previous()
                    self.autocomplete.widget.queue_draw()
                    return True

        if not self.autocomplete.is_active:
            if keyval == Gdk.keyval_from_name('bracketleft'):
                self.autocomplete.autoclose_brackets('[')
                return True
            if keyval == Gdk.keyval_from_name('braceleft'):
                self.autocomplete.autoclose_brackets('{')
                return True
            if keyval == Gdk.keyval_from_name('parenleft'):
                self.autocomplete.autoclose_brackets('(')
                return True
            if keyval == Gdk.keyval_from_name('bracketright'):
                return self.autocomplete.handle_autoclosing_bracket_overwrite(']')
            if keyval == Gdk.keyval_from_name('braceright'):
                return self.autocomplete.handle_autoclosing_bracket_overwrite('}')
            if keyval == Gdk.keyval_from_name('parenright'):
                return self.autocomplete.handle_autoclosing_bracket_overwrite(')')
            if keyval == Gdk.keyval_from_name('backslash'):
                return self.autocomplete.handle_autoclosing_bracket_overwrite('\\')

    def on_document_change(self, document):
        if self.autocomplete.is_active:
            self.autocomplete.deactivate_if_necessary()
            self.autocomplete.update_suggestions()
            self.autocomplete.widget.queue_draw()
        elif self.document.parser.last_edit[0] == 'insert':
            if len(self.document.parser.last_edit[2]) == 1:
                self.autocomplete.activate_if_possible()
                self.autocomplete.widget.queue_draw()

    def on_cursor_position_change(self, buffer, position):
        if self.autocomplete.is_active:
            self.autocomplete.deactivate_if_necessary()
            self.autocomplete.update_suggestions()
            self.autocomplete.widget.queue_draw()
        self.autocomplete.cursor_unchanged_after_autoclosing_bracket = False

    def on_adjustment_change(self, adjustment):
        self.autocomplete.widget.queue_draw()

    def on_adjustment_value_change(self, adjustment):
        self.autocomplete.widget.queue_draw()



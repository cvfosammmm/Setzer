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


class UpdateMatchingBlocks(object):

    def __init__(self, document):
        self.document = document
        self.source_buffer = document.source_buffer

        self.is_enabled = self.document.settings.get_value('preferences', 'update_matching_blocks')

        key_controller = Gtk.EventControllerKey()
        key_controller.connect('key-pressed', self.on_keypress)
        key_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.document.view.source_view.add_controller(key_controller)

        self.document.settings.connect('settings_changed', self.on_settings_changed)

    def on_settings_changed(self, settings, parameter):
        section, item, value = parameter

        if item == 'update_matching_blocks':
            self.is_enabled = value

    def on_keypress(self, controller, keyval, keycode, state):
        if self.document.autocomplete.is_active: return False
        if not self.is_enabled: return False

        modifiers = Gtk.accelerator_get_default_mod_mask()

        if ServiceLocator.get_regex_object('[a-zA-Z]\\Z').match(Gdk.keyval_name(keyval)) or keyval == Gdk.keyval_from_name('asterisk') or keyval == Gdk.keyval_from_name('BackSpace') or keyval == Gdk.keyval_from_name('Delete'):
            if state & modifiers == 0:
                if not self.document.autocomplete.is_active:
                    if self.handle_keypress_inside_begin_or_end(keyval):
                        return True

        return False

    def handle_keypress_inside_begin_or_end(self, keyval):
        buffer = self.source_buffer
        insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
        line = self.document.get_line(insert_iter.get_line())
        offset = insert_iter.get_line_offset()
        cursor_offset = insert_iter.get_offset()
        line = line[:offset] + '%•%' + line[offset:]
        match_begin_end = ServiceLocator.get_regex_object(r'.*\\(begin|end)\{((?:[^\{\[\(])*)%•%((?:[^\{\[\(])*)\}').match(line)
        if match_begin_end == None: return False
        if keyval == Gdk.keyval_from_name('BackSpace') and len(match_begin_end.group(2)) == 0: return False
        if keyval == Gdk.keyval_from_name('Delete') and len(match_begin_end.group(3)) == 0: return False

        orig_offset = cursor_offset - insert_iter.get_line_offset() + match_begin_end.start()
        offset = None
        for block in self.document.parser.symbols['blocks']:
            if block[0] == orig_offset:
                if block[1] == None:
                    return False
                else:
                    offset = block[1] + 5 + len(match_begin_end.group(2))
                    break
            elif block[1] == orig_offset:
                if block[0] == None:
                    return False
                else:
                    offset = block[0] + 7 + len(match_begin_end.group(2))
                    break
        if offset == None: return False

        buffer.begin_user_action()
        if keyval == Gdk.keyval_from_name('asterisk'):
            if cursor_offset < offset: offset += 1
            buffer.insert_at_cursor('*')
            buffer.insert(buffer.get_iter_at_offset(offset), '*')
        elif keyval == Gdk.keyval_from_name('BackSpace'):
            if cursor_offset < offset: offset -= 1
            buffer.delete(buffer.get_iter_at_offset(cursor_offset - 1), buffer.get_iter_at_offset(cursor_offset))
            buffer.delete(buffer.get_iter_at_offset(offset - 1), buffer.get_iter_at_offset(offset))
        elif keyval == Gdk.keyval_from_name('Delete'):
            if cursor_offset < offset: offset -= 1
            buffer.delete(buffer.get_iter_at_offset(cursor_offset), buffer.get_iter_at_offset(cursor_offset + 1))
            buffer.delete(buffer.get_iter_at_offset(offset), buffer.get_iter_at_offset(offset + 1))
        else:
            if cursor_offset < offset: offset += 1
            char = Gdk.keyval_name(keyval)
            buffer.insert_at_cursor(char)
            buffer.insert(buffer.get_iter_at_offset(offset), char)
        buffer.end_user_action()

        return True



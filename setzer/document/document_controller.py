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

import os.path

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import GObject

from setzer.dialogs.dialog_locator import DialogLocator
from setzer.app.service_locator import ServiceLocator


class DocumentController(object):
    
    def __init__(self, document, document_view):

        self.document = document
        self.view = document_view

        self.workspace = ServiceLocator.get_workspace()

        self.view.source_view.connect('key-press-event', self.on_keypress)
        self.view.source_view.connect('button-press-event', self.on_buttonpress)
        self.continue_save_date_loop = True
        GObject.timeout_add(500, self.save_date_loop)

    '''
    *** signal handlers: changes in documents
    '''

    def on_buttonpress(self, widget, event, data=None):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if event.type == Gdk.EventType.BUTTON_PRESS:
            if event.state & modifiers == Gdk.ModifierType.CONTROL_MASK:
                if self.workspace.can_sync:
                    GLib.idle_add(self.workspace.forward_sync, self.document)
        return False

    def on_keypress(self, widget, event, data=None):
        modifiers = Gtk.accelerator_get_default_mod_mask()
        tab_keyvals = [Gdk.keyval_from_name('Tab'), Gdk.keyval_from_name('ISO_Left_Tab')]
        keypress_handled = False

        try: autocomplete = self.document.autocomplete
        except AttributeError: pass
        else:
            if not keypress_handled:
                keypress_handled = self.document.autocomplete.on_keypress(event)
                if keypress_handled:
                    return True

        if not keypress_handled and event.keyval == Gdk.keyval_from_name('c'):
            if event.state & modifiers == Gdk.ModifierType.CONTROL_MASK:
                self.document.content.copy()
                return True

        if not keypress_handled and event.keyval == Gdk.keyval_from_name('x'):
            if event.state & modifiers == Gdk.ModifierType.CONTROL_MASK:
                self.document.content.cut()
                return True

        if not keypress_handled and event.keyval == Gdk.keyval_from_name('v'):
            if event.state & modifiers == Gdk.ModifierType.CONTROL_MASK:
                self.document.content.paste()
                return True

        if not keypress_handled and event.keyval in tab_keyvals:
            if event.state & modifiers == 0:
                buffer = self.document.content.source_buffer
                insert = buffer.get_iter_at_mark(buffer.get_insert())
                insert.forward_chars(1)
                limit_iter = insert.copy()
                limit_iter.forward_lines(3)
                limit_iter.backward_chars(1)
                result = insert.forward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
                if result != None:
                    buffer.place_cursor(result[0])
                    buffer.select_range(result[0], result[1])
                    self.document.content.scroll_cursor_onscreen()
                    return True
                
                insert.backward_chars(1)
                result = insert.forward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
                if result != None:
                    buffer.select_range(result[0], result[1])
                    self.document.content.scroll_cursor_onscreen()
                    return True
            elif event.state & modifiers == Gdk.ModifierType.SHIFT_MASK:
                buffer = self.document.content.source_buffer
                insert = buffer.get_iter_at_mark(buffer.get_insert())
                limit_iter = insert.copy()
                limit_iter.backward_lines(3)
                result = insert.backward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
                if result != None:
                    buffer.select_range(result[0], result[1])
                    self.document.content.scroll_cursor_onscreen()
                    return True

                insert.forward_chars(1)
                result = insert.backward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
                if result != None:
                    buffer.select_range(result[0], result[1])
                    self.document.content.scroll_cursor_onscreen()
                    return True
        return False

    def save_date_loop(self):
        if self.document.filename == None: return True
        if self.document.deleted_on_disk_dialog_shown_after_last_save: return True
        if self.document.get_deleted_on_disk():
            DialogLocator.get_dialog('document_deleted_on_disk').run(self.document)
            self.document.deleted_on_disk_dialog_shown_after_last_save = True
            self.document.content.set_modified(True)
            return True
        if self.document.get_changed_on_disk():
            if DialogLocator.get_dialog('document_changed_on_disk').run(self.document):
                self.document.populate_from_filename()
                self.document.content.set_modified(False)
            else:
                self.document.content.set_modified(True)
            self.document.update_save_date()
        return self.continue_save_date_loop



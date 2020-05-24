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
from gi.repository import Gtk
from gi.repository import GObject

from setzer.dialogs.dialog_locator import DialogLocator


class DocumentController(object):
    
    def __init__(self, document, document_view):

        self.document = document
        self.view = document_view

        self.view.source_view.connect('key-press-event', self.on_keypress)
        self.view.source_view.connect('button-press-event', self.on_button_press)
        GObject.timeout_add(500, self.save_date_loop)
        
        def undo(menu_item): self.view.source_view.emit('undo')
        self.view.menu_item_undo.connect('activate', undo)

        def redo(menu_item): self.view.source_view.emit('redo')
        self.view.menu_item_redo.connect('activate', redo)

        def cut(menu_item): self.view.source_view.emit('cut-clipboard')
        self.view.menu_item_cut.connect('activate', cut)

        def copy(menu_item): self.view.source_view.emit('copy-clipboard')
        self.view.menu_item_copy.connect('activate', copy)

        def paste(menu_item): self.view.source_view.emit('paste-clipboard')
        self.view.menu_item_paste.connect('activate', paste)

        def delete(menu_item): self.view.source_view.emit('delete-from-cursor', Gtk.DeleteType.CHARS, 0)
        self.view.menu_item_delete.connect('activate', delete)

        def select_all(menu_item): self.view.source_view.emit('select-all', True)
        self.view.menu_item_select_all.connect('activate', select_all)

        if self.document.is_latex_document():
            self.view.menu_item_show_in_preview.connect('activate', self.on_show_in_preview)


    '''
    *** signal handlers: changes in documents
    '''

    def on_button_press(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.show_context_menu(event)
            return True

    def on_show_in_preview(self, menu_item):
        self.document.forward_sync()

    def on_keypress(self, widget, event, data=None):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        try: autocomplete = self.document.autocomplete
        except AttributeError: autocomplete = None
        if autocomplete != None:
            if event.keyval == Gdk.keyval_from_name('Down'):
                if event.state & modifiers == 0:
                    return autocomplete.on_down_press()

            if event.keyval == Gdk.keyval_from_name('Up'):
                if event.state & modifiers == 0:
                    return autocomplete.on_up_press()

            if event.keyval == Gdk.keyval_from_name('Escape'):
                if event.state & modifiers == 0:
                    return autocomplete.on_escape_press()

            if event.keyval == Gdk.keyval_from_name('Return'):
                if event.state & modifiers == 0:
                    return autocomplete.on_return_press()

        if event.keyval == Gdk.keyval_from_name('Menu') and event.state & modifiers == 0:
            self.show_context_menu(event)
            return True

        elif event.keyval == Gdk.keyval_from_name('Tab') or event.keyval == Gdk.keyval_from_name('ISO_Left_Tab'):
            if event.state & modifiers == 0:
                buffer = self.document.get_buffer()
                insert = buffer.get_iter_at_mark(buffer.get_insert())
                insert.forward_chars(1)
                limit_iter = insert.copy()
                limit_iter.forward_lines(3)
                limit_iter.backward_chars(1)
                result = insert.forward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
                if result != None:
                    buffer.place_cursor(result[0])
                    buffer.select_range(result[0], result[1])
                    self.view.source_view.scroll_to_iter(result[1], 0, False, 0, 0)
                    return True
                
                insert.backward_chars(1)
                result = insert.forward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
                if result != None:
                    buffer.select_range(result[0], result[1])
                    self.view.source_view.scroll_to_iter(result[1], 0, False, 0, 0)
                    return True
            elif event.state & modifiers == Gdk.ModifierType.SHIFT_MASK:
                buffer = self.document.get_buffer()
                insert = buffer.get_iter_at_mark(buffer.get_insert())
                limit_iter = insert.copy()
                limit_iter.backward_lines(3)
                result = insert.backward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
                if result != None:
                    buffer.select_range(result[0], result[1])
                    self.view.source_view.scroll_to_iter(result[0], 0, False, 0, 0)
                    return True

                insert.forward_chars(1)
                result = insert.backward_search('•', Gtk.TextSearchFlags.VISIBLE_ONLY, limit_iter)
                if result != None:
                    buffer.select_range(result[0], result[1])
                    self.view.source_view.scroll_to_iter(result[0], 0, False, 0, 0)
                    return True
        return False

    def show_context_menu(self, event):
        has_selection = self.document.source_buffer.get_has_selection()
        self.view.menu_item_cut.set_sensitive(has_selection)
        self.view.menu_item_copy.set_sensitive(has_selection)
        self.view.menu_item_delete.set_sensitive(has_selection)
        self.view.context_menu.show_all()
        self.view.context_menu.popup_at_pointer(event)

    def save_date_loop(self):
        if self.document.filename == None: return True
        if self.document.save_date <= os.path.getmtime(self.document.filename) - 0.001:
            if DialogLocator.get_dialog('document_changed_on_disk').run(self.document):
                self.document.populate_from_filename()
            else:
                self.document.source_buffer.set_modified(False)
            self.document.update_save_date()
        return True



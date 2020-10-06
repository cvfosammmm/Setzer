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
from gi.repository import Gtk


class ContextMenu(object):
    
    def __init__(self, document, document_view):
        self.document = document
        self.view = document_view

        self.view.source_view.connect('populate-popup', self.on_populate_popup)

    '''
    *** signal handlers: changes in documents
    '''

    def on_populate_popup(self, view, menu):
        for item in menu.get_children():
            menu.remove(item)

        menu_item_cut = Gtk.MenuItem.new_with_label(_('Cut'))
        menu_item_copy = Gtk.MenuItem.new_with_label(_('Copy'))
        menu_item_paste = Gtk.MenuItem.new_with_label(_('Paste'))
        menu_item_delete = Gtk.MenuItem.new_with_label(_('Delete'))
        menu_item_select_all = Gtk.MenuItem.new_with_label(_('Select All'))

        menu.append(menu_item_cut)
        menu.append(menu_item_copy)
        menu.append(menu_item_paste)
        menu.append(menu_item_delete)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(menu_item_select_all)

        menu_item_cut.connect('activate', self.on_cut)
        menu_item_copy.connect('activate', self.on_copy)
        menu_item_paste.connect('activate', self.on_paste)
        menu_item_delete.connect('activate', self.on_delete)
        menu_item_select_all.connect('activate', self.on_select_all)

        has_selection = self.document.source_buffer.get_has_selection()
        menu_item_cut.set_sensitive(has_selection)
        menu_item_copy.set_sensitive(has_selection)
        menu_item_delete.set_sensitive(has_selection)

        if self.document.is_latex_document():
            menu_item_comment = Gtk.MenuItem.new_with_label(_('Toggle Comment'))
            menu_item_comment.connect('activate', self.on_toggle_comment)
            menu_item_show_in_preview = Gtk.MenuItem.new_with_label(_('Show in Preview'))
            menu_item_show_in_preview.set_sensitive(self.document.can_forward_sync)
            menu_item_show_in_preview.connect('activate', self.on_show_in_preview)
            menu.append(Gtk.SeparatorMenuItem())
            menu.append(menu_item_comment)
            menu.append(menu_item_show_in_preview)
        menu.show_all()

    def on_cut(menu_item):
        self.view.source_view.emit('cut-clipboard')

    def on_copy(menu_item):
        self.view.source_view.emit('copy-clipboard')

    def on_paste(menu_item):
        self.view.source_view.emit('paste-clipboard')

    def on_delete(menu_item):
        self.view.source_view.emit('delete-from-cursor', Gtk.DeleteType.CHARS, 0)

    def on_select_all(menu_item):
        self.view.source_view.emit('select-all', True)

    def on_show_in_preview(self, menu_item):
        self.document.forward_sync()

    def on_toggle_comment(self, menu_item):
        self.document.comment_uncomment()



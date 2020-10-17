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


class ContextMenuPresenter(object):
    
    def __init__(self, context_menu, scbar_view):
        self.context_menu = context_menu
        self.context_menu.document_view.source_view.connect('populate-popup', self.on_populate_popup)
        self.scbar_view = scbar_view

        self.context_menu.document.source_buffer.connect('mark-set', self.on_mark_set)

        undo_manager = self.context_menu.document.source_buffer.get_undo_manager()
        undo_manager.connect('can-undo-changed', self.on_can_undo_changed)
        undo_manager.connect('can-redo-changed', self.on_can_redo_changed)

        self.on_can_undo_changed(undo_manager)
        self.on_can_redo_changed(undo_manager)

        if self.context_menu.document.is_latex_document():
            self.on_can_forward_sync_changed(self.context_menu.document.can_forward_sync)

    def set_zoom_level(self, zoom_level):
        self.scbar_view.model_button_reset_zoom.set_label("{:.0%}".format(zoom_level))

    def on_can_forward_sync_changed(self, can_sync):
        if self.context_menu.document.is_latex_document():
            self.scbar_view.model_button_show_in_preview.set_sensitive(can_sync)

    def on_mark_set(self, buffer, location, mark):
        has_selection = self.context_menu.document.source_buffer.get_has_selection()
        self.scbar_view.model_button_cut.set_sensitive(has_selection)
        self.scbar_view.model_button_copy.set_sensitive(has_selection)
        self.scbar_view.model_button_delete.set_sensitive(has_selection)

    def on_can_undo_changed(self, undo_manager):
        if undo_manager.can_undo():
            self.scbar_view.model_button_undo.set_sensitive(True)
        else:
            self.scbar_view.model_button_undo.set_sensitive(False)

    def on_can_redo_changed(self, undo_manager):
        if undo_manager.can_redo():
            self.scbar_view.model_button_redo.set_sensitive(True)
        else:
            self.scbar_view.model_button_redo.set_sensitive(False)

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

        menu_item_cut.connect('activate', self.context_menu.on_cut)
        menu_item_copy.connect('activate', self.context_menu.on_copy)
        menu_item_paste.connect('activate', self.context_menu.on_paste)
        menu_item_delete.connect('activate', self.context_menu.on_delete)
        menu_item_select_all.connect('activate', self.context_menu.on_select_all)

        has_selection = self.context_menu.document.source_buffer.get_has_selection()
        menu_item_cut.set_sensitive(has_selection)
        menu_item_copy.set_sensitive(has_selection)
        menu_item_delete.set_sensitive(has_selection)

        if self.context_menu.document.is_latex_document():
            menu_item_comment = Gtk.MenuItem.new_with_label(_('Toggle Comment'))
            menu_item_comment.connect('activate', self.context_menu.on_toggle_comment)
            menu_item_show_in_preview = Gtk.MenuItem.new_with_label(_('Show in Preview'))
            menu_item_show_in_preview.set_sensitive(self.context_menu.document.can_forward_sync)
            menu_item_show_in_preview.connect('activate', self.context_menu.on_show_in_preview)
            menu.append(Gtk.SeparatorMenuItem())
            menu.append(menu_item_comment)
            menu.append(menu_item_show_in_preview)
        menu.show_all()



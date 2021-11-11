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

import setzer.document.context_menu.context_menu_viewgtk as context_menu_view
from setzer.app.service_locator import ServiceLocator


class ContextMenu(object):
    
    def __init__(self, document, document_view):
        self.document = document
        self.document_view = document_view

        self.scbar_view = context_menu_view.ContextMenuView(document)
        stack = document_view.shortcutsbar_bottom.more_actions_popover.get_child()
        stack.add_named(self.scbar_view, 'main')

        self.scbar_view.model_button_undo.connect('clicked', self.on_undo)
        self.scbar_view.model_button_redo.connect('clicked', self.on_redo)
        self.scbar_view.model_button_cut.connect('clicked', self.on_cut)
        self.scbar_view.model_button_copy.connect('clicked', self.on_copy)
        self.scbar_view.model_button_paste.connect('clicked', self.on_paste)
        self.scbar_view.model_button_delete.connect('clicked', self.on_delete)
        self.scbar_view.model_button_select_all.connect('clicked', self.on_select_all)
        self.scbar_view.model_button_zoom_out.connect('button-press-event', self.on_zoom_out)
        self.scbar_view.model_button_zoom_in.connect('button-press-event', self.on_zoom_in)
        self.scbar_view.model_button_reset_zoom.connect('button-press-event', self.on_reset_zoom)

        if self.document.is_latex_document():
            self.scbar_view.model_button_toggle_comment.connect('clicked', self.on_toggle_comment)
            self.scbar_view.model_button_show_in_preview.connect('clicked', self.on_show_in_preview)

        self.document_view.source_view.connect('populate-popup', self.on_populate_popup)
        self.document.content.connect('selection_might_have_changed', self.on_has_selection_changed)
        self.document.content.connect('can_undo_changed', self.on_can_undo_changed)
        self.document.content.connect('can_redo_changed', self.on_can_redo_changed)

        self.scbar_view.model_button_undo.set_sensitive(self.document.content.get_can_undo())
        self.scbar_view.model_button_redo.set_sensitive(self.document.content.get_can_redo())

        self.can_sync = False
        self.has_selection = False
        self.workspace = ServiceLocator.get_workspace()
        if self.document.is_latex_document():
            self.workspace.connect('update_sync_state', self.on_update_sync_state)

        self.font_manager = ServiceLocator.get_font_manager()
        self.font_manager.connect('font_string_changed', self.on_font_string_changed)

    def on_font_string_changed(self, font_manager):
        zoom_level = self.font_manager.get_zoom_level()
        self.scbar_view.model_button_reset_zoom.set_label("{:.0%}".format(zoom_level))

    def on_update_sync_state(self, workspace):
        self.can_sync = self.workspace.can_sync
        self.scbar_view.model_button_show_in_preview.set_sensitive(self.can_sync)

    def on_has_selection_changed(self, document, has_selection):
        self.scbar_view.model_button_cut.set_sensitive(has_selection)
        self.scbar_view.model_button_copy.set_sensitive(has_selection)
        self.scbar_view.model_button_delete.set_sensitive(has_selection)
        self.has_selection = has_selection

    def on_can_undo_changed(self, content, can_undo):
        self.scbar_view.model_button_undo.set_sensitive(can_undo)

    def on_can_redo_changed(self, content, can_redo):
        self.scbar_view.model_button_redo.set_sensitive(can_redo)

    def on_undo(self, widget=None):
        self.document.content.undo()

    def on_redo(self, widget=None):
        self.document.content.redo()

    def on_cut(self, widget=None):
        self.document.content.cut()

    def on_copy(self, widget=None):
        self.document.content.copy()

    def on_paste(self, widget=None):
        self.document.content.paste()

    def on_delete(self, widget=None):
        self.document.content.delete_selection()

    def on_select_all(self, widget=None):
        self.document.content.select_all()

    def on_zoom_out(self, widget=None, event=None):
        ServiceLocator.get_font_manager().zoom_out()
        return True

    def on_zoom_in(self, widget=None, event=None):
        ServiceLocator.get_font_manager().zoom_in()
        return True

    def on_reset_zoom(self, widget=None, event=None):
        ServiceLocator.get_font_manager().reset_zoom()
        return True

    def on_show_in_preview(self, widget=None):
        self.workspace.forward_sync(self.document)

    def on_toggle_comment(self, menu_item):
        self.document.comment_uncomment()

    def on_populate_popup(self, view, menu):
        rc_view = context_menu_view.RCMenuView()

        for item in menu.get_children():
            menu.remove(item)

        menu.append(rc_view.menu_item_cut)
        menu.append(rc_view.menu_item_copy)
        menu.append(rc_view.menu_item_paste)
        menu.append(rc_view.menu_item_delete)
        menu.append(rc_view.separator_menu_item1)
        menu.append(rc_view.menu_item_select_all)

        rc_view.menu_item_cut.connect('activate', self.on_cut)
        rc_view.menu_item_copy.connect('activate', self.on_copy)
        rc_view.menu_item_paste.connect('activate', self.on_paste)
        rc_view.menu_item_delete.connect('activate', self.on_delete)
        rc_view.menu_item_select_all.connect('activate', self.on_select_all)

        rc_view.menu_item_cut.set_sensitive(self.has_selection)
        rc_view.menu_item_copy.set_sensitive(self.has_selection)
        rc_view.menu_item_delete.set_sensitive(self.has_selection)

        if self.document.is_latex_document():
            rc_view.menu_item_comment.connect('activate', self.on_toggle_comment)
            rc_view.menu_item_show_in_preview.set_sensitive(self.can_sync)
            rc_view.menu_item_show_in_preview.connect('activate', self.on_show_in_preview)
            menu.append(rc_view.separator_menu_item2)
            menu.append(rc_view.menu_item_comment)
            menu.append(rc_view.menu_item_show_in_preview)
        menu.show_all()



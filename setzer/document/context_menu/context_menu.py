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

import setzer.document.context_menu.context_menu_controller as context_menu_controller
import setzer.document.context_menu.context_menu_presenter as context_menu_presenter
import setzer.document.context_menu.context_menu_viewgtk as context_menu_view
from setzer.app.service_locator import ServiceLocator


class ContextMenu(object):
    
    def __init__(self, document, document_view):
        self.document = document
        self.document_view = document_view

        self.scbar_view = context_menu_view.ContextMenuView(document)
        stack = document_view.shortcuts_bar_bottom.more_actions_popover.get_child()
        stack.add_named(self.scbar_view, 'main')
        self.controller = context_menu_controller.ContextMenuController(self, self.scbar_view)
        self.presenter = context_menu_presenter.ContextMenuPresenter(self, self.scbar_view)

        self.can_sync = False
        self.forward_sync_manager = ServiceLocator.get_forward_sync_manager()
        self.forward_sync_manager.register_observer(self)

        self.font_manager = ServiceLocator.get_font_manager()
        self.font_manager.register_observer(self)

        document.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'update_sync_state':
            self.can_sync = self.forward_sync_manager.can_sync
            if self.document.is_latex_document():
                self.presenter.on_can_sync_changed(self.can_sync)

        if change_code == 'font_string_changed':
            zoom_level = self.font_manager.get_zoom_level()
            self.presenter.set_zoom_level(zoom_level)

    def on_undo(self, widget=None):
        self.document.undo()

    def on_redo(self, widget=None):
        self.document.redo()

    def on_cut(self, widget=None):
        self.document.cut()

    def on_copy(self, widget=None):
        self.document.copy()

    def on_paste(self, widget=None):
        self.document.paste()

    def on_delete(self, widget=None):
        self.document.delete_selection()

    def on_select_all(self, widget=None):
        self.document.select_all()

    def on_zoom_out(self, widget=None, event=None):
        ServiceLocator.get_main_window().zoom_out_action.activate()
        return True

    def on_zoom_in(self, widget=None, event=None):
        ServiceLocator.get_main_window().zoom_in_action.activate()
        return True

    def on_reset_zoom(self, widget=None, event=None):
        ServiceLocator.get_main_window().reset_zoom_action.activate()
        return True

    def on_show_in_preview(self, widget=None):
        self.forward_sync_manager.forward_sync(self.document)

    def on_toggle_comment(self, menu_item):
        self.document.comment_uncomment()



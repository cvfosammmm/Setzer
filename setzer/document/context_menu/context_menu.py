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
from gi.repository import Gdk
from gi.repository import Gtk

from setzer.app.service_locator import ServiceLocator
from setzer.helpers.popover_menu_builder import MenuBuilder


class ContextMenu(object):
    
    def __init__(self, document, document_view):
        self.document = document
        self.document_view = document_view

        self.popover_more = MenuBuilder.create_menu()
        self.popover_more.set_can_focus(False)
        self.popover_more.connect('closed', self.on_popover_close)
        self.popover_more.set_size_request(260, -1)
        self.build_popover(self.popover_more)

        self.popover_pointer = MenuBuilder.create_menu()
        self.popover_pointer.set_position(Gtk.PositionType.BOTTOM)
        self.popover_pointer.set_parent(self.document_view)
        self.popover_pointer.set_size_request(260, -1)
        self.popover_pointer.set_has_arrow(False)
        self.popover_pointer.set_offset(130, 0)
        self.popover_pointer.set_can_focus(False)
        self.popover_pointer.connect('closed', self.on_popover_close)
        self.build_popover(self.popover_pointer)

    def build_popover(self, popover):
        self.current_popover = popover

        button_undo = self.create_button(_('Undo'), 'win.undo', shortcut=_('Ctrl') + '+Z')
        MenuBuilder.add_widget(self.current_popover, button_undo)
        button_redo = self.create_button(_('Redo'), 'win.redo', shortcut=_('Shift') + '+' + _('Ctrl') + '+Z')
        MenuBuilder.add_widget(self.current_popover, button_redo)
        MenuBuilder.add_separator(self.current_popover)
        button_cut = self.create_button(_('Cut'), 'win.cut', shortcut=_('Ctrl') + '+X')
        MenuBuilder.add_widget(self.current_popover, button_cut)
        button_copy = self.create_button(_('Copy'), 'win.copy', shortcut=_('Ctrl') + '+C')
        MenuBuilder.add_widget(self.current_popover, button_copy)
        button_paste = self.create_button(_('Paste'), 'win.paste', shortcut=_('Ctrl') + '+V')
        MenuBuilder.add_widget(self.current_popover, button_paste)
        button_delete = self.create_button(_('Delete'), 'win.delete-selection')
        MenuBuilder.add_widget(self.current_popover, button_delete)
        MenuBuilder.add_separator(self.current_popover)
        button_select_all = self.create_button(_('Select All'), 'win.select-all', shortcut=_('Ctrl') + '+A')
        MenuBuilder.add_widget(self.current_popover, button_select_all)
        MenuBuilder.add_separator(self.current_popover)
        button_toggle_comment = self.create_button(_('Toggle Comment'), 'win.toggle-comment', shortcut=_('Ctrl') + '+K')
        MenuBuilder.add_widget(self.current_popover, button_toggle_comment)

    def create_button(self, label, action_name, shortcut=None):
        button = MenuBuilder.create_button(label, shortcut=shortcut)
        button.set_action_name(action_name)
        button.connect('clicked', self.on_menu_button_click, self.current_popover)
        return button

    def popup_at_cursor(self, x, y):
        rect = Gdk.Rectangle()
        rect.x = x
        rect.y = y
        rect.width = 1
        rect.height = 1
        self.popover_pointer.set_pointing_to(rect)
        self.popover_pointer.popup()

    def on_popover_close(self, popover):
        self.document_view.source_view.grab_focus()
        self.document_view.source_view.reset_cursor_blink()

    def on_menu_button_click(self, button, popover):
        popover.popdown()



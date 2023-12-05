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
from gi.repository import Gdk, Gtk, Pango

from setzer.app.service_locator import ServiceLocator
from setzer.app.font_manager import FontManager
from setzer.popovers.helpers.popover_menu_builder import MenuBuilder
from setzer.popovers.popover_manager import PopoverManager


class ContextMenu(object):

    def __init__(self, workspace):
        self.workspace = workspace
        self.document = None

        self.comment_button_pointer = None
        self.sync_button_pointer = None

        self.popover_more = PopoverManager.create_popover('context_menu')

        self.popover_pointer = MenuBuilder.create_menu()
        self.popover_pointer.set_position(Gtk.PositionType.BOTTOM)
        self.popover_pointer.set_size_request(300, -1)
        self.popover_pointer.set_has_arrow(False)
        self.popover_pointer.set_offset(150, 0)
        self.popover_pointer.set_can_focus(False)
        self.build_popover_pointer()

        self.workspace.connect('new_active_document', self.on_new_active_document)

    def on_new_active_document(self, workspace=None, parameter=None):
        self.document = self.workspace.active_document
        self.comment_button_pointer.set_visible(self.document != None and self.document.is_latex_document())
        self.sync_button_pointer.set_visible(self.document != None and self.document.is_latex_document())
        self.latex_buttons_separator_pointer.set_visible(self.document != None and self.document.is_latex_document())

    def build_popover_pointer(self):
        self.add_basic_buttons(self.popover_pointer)

        self.comment_button_pointer = self.create_button(self.popover_pointer, _('Toggle Comment'), 'win.toggle-comment', shortcut=_('Ctrl') + '+K')
        self.popover_pointer.add_widget(self.comment_button_pointer)
        self.sync_button_pointer = self.create_button(self.popover_pointer, _('Show in Preview'), 'win.forward-sync')
        self.popover_pointer.add_widget(self.sync_button_pointer)
        self.latex_buttons_separator_pointer = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        self.popover_pointer.add_widget(self.latex_buttons_separator_pointer)

        box = Gtk.CenterBox()
        box.set_orientation(Gtk.Orientation.HORIZONTAL)
        zoom_label = Gtk.Label.new(_('Zoom'))
        zoom_label.set_margin_start(10)
        box.set_start_widget(zoom_label)
        inner_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)

        button_zoom_out = MenuBuilder.create_button('', shortcut=None)
        button_zoom_out.set_icon_name('value-decrease-symbolic')
        button_zoom_out.set_action_name('win.zoom-out')
        inner_box.append(button_zoom_out)
        self.reset_zoom_button_pointer = MenuBuilder.create_button('', shortcut=None)
        self.reset_zoom_button_pointer.set_label('100%')
        self.reset_zoom_button_pointer.set_action_name('win.reset-zoom')
        self.reset_zoom_button_pointer.set_size_request(53, -1)
        inner_box.append(self.reset_zoom_button_pointer)
        button_zoom_in = MenuBuilder.create_button('', shortcut=None)
        button_zoom_in.set_icon_name('value-increase-symbolic')
        button_zoom_in.set_action_name('win.zoom-in')
        inner_box.append(button_zoom_in)
        box.set_end_widget(inner_box)
        self.popover_pointer.add_widget(box)

    def add_basic_buttons(self, popover):
        button_undo = self.create_button(popover, _('Undo'), 'win.undo', shortcut=_('Ctrl') + '+Z')
        popover.add_widget(button_undo)
        button_redo = self.create_button(popover, _('Redo'), 'win.redo', shortcut=_('Shift') + '+' + _('Ctrl') + '+Z')
        popover.add_widget(button_redo)
        popover.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
        button_cut = self.create_button(popover, _('Cut'), 'win.cut', shortcut=_('Ctrl') + '+X')
        popover.add_widget(button_cut)
        button_copy = self.create_button(popover, _('Copy'), 'win.copy', shortcut=_('Ctrl') + '+C')
        popover.add_widget(button_copy)
        button_paste = self.create_button(popover, _('Paste'), 'win.paste', shortcut=_('Ctrl') + '+V')
        popover.add_widget(button_paste)
        button_delete = self.create_button(popover, _('Delete'), 'win.delete-selection')
        popover.add_widget(button_delete)
        popover.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
        button_select_all = self.create_button(popover, _('Select All'), 'win.select-all', shortcut=_('Ctrl') + '+A')
        popover.add_widget(button_select_all)
        popover.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))

    def create_button(self, popover, label, action_name, shortcut=None):
        button = MenuBuilder.create_button(label, shortcut=shortcut)
        button.set_action_name(action_name)
        button.connect('clicked', self.on_menu_button_click)
        return button

    def popup_at_cursor(self, x, y):
        if self.document == None: return

        self.popover_pointer.unparent()
        self.popover_pointer.set_parent(self.document.view)
        rect = Gdk.Rectangle()
        rect.x = x
        rect.y = y
        rect.width = 1
        rect.height = 1
        self.popover_pointer.set_pointing_to(rect)
        self.popover_pointer.popup()

    def on_menu_button_click(self, button):
        self.popover_pointer.popdown()
        PopoverManager.popdown()



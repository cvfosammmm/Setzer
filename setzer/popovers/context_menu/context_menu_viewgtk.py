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
from gi.repository import Gtk

from setzer.popovers.helpers.popover_menu_builder import MenuBuilder
from setzer.popovers.helpers.popover import Popover


class ContextMenuView(Popover):

    def __init__(self, popover_manager):
        Popover.__init__(self, popover_manager)

        self.set_width(288)

        self.add_action_button('main', _('Undo'), 'win.undo', shortcut=_('Ctrl') + '+Z')
        self.add_action_button('main', _('Redo'), 'win.redo', shortcut=_('Shift') + '+' + _('Ctrl') + '+Z')
        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
        self.add_action_button('main', _('Cut'), 'win.cut', shortcut=_('Ctrl') + '+X')
        self.add_action_button('main', _('Copy'), 'win.copy', shortcut=_('Ctrl') + '+C')
        self.add_action_button('main', _('Paste'), 'win.paste', shortcut=_('Ctrl') + '+V')
        self.add_action_button('main', _('Delete'), 'win.delete-selection')
        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
        self.add_action_button('main', _('Select All'), 'win.select-all', shortcut=_('Ctrl') + '+A')
        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
        self.comment_button = self.add_action_button('main', _('Toggle Comment'), 'win.toggle-comment', shortcut=_('Ctrl') + '+K')
        self.sync_button = self.add_action_button('main', _('Show in Preview'), 'win.forward-sync')
        self.latex_buttons_separator = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        self.add_widget(self.latex_buttons_separator)

        box = Gtk.CenterBox()
        box.set_orientation(Gtk.Orientation.HORIZONTAL)
        zoom_label = Gtk.Label.new(_('Zoom'))
        zoom_label.set_margin_start(10)
        box.set_start_widget(zoom_label)
        inner_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)

        button_zoom_out = MenuBuilder.create_button('', shortcut=None)
        button_zoom_out.set_icon_name('value-decrease-symbolic')
        button_zoom_out.set_action_name('win.zoom-out')
        self.register_button_for_keyboard_navigation(button_zoom_out, pagename='main')
        inner_box.append(button_zoom_out)
        self.reset_zoom_button = MenuBuilder.create_button('', shortcut=None)
        self.reset_zoom_button.set_label('100%')
        self.reset_zoom_button.set_action_name('win.reset-zoom')
        self.reset_zoom_button.set_size_request(53, -1)
        self.register_button_for_keyboard_navigation(self.reset_zoom_button, pagename='main')
        inner_box.append(self.reset_zoom_button)
        button_zoom_in = MenuBuilder.create_button('', shortcut=None)
        button_zoom_in.set_icon_name('value-increase-symbolic')
        button_zoom_in.set_action_name('win.zoom-in')
        self.register_button_for_keyboard_navigation(button_zoom_in, pagename='main')
        inner_box.append(button_zoom_in)
        box.set_end_widget(inner_box)
        self.add_widget(box)



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
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class ContextMenuView(Gtk.Box):
    
    def __init__(self, document):
        Gtk.Box.__init__(self, orientation = Gtk.Orientation.VERTICAL)

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_left(0)
        self.set_margin_right(0)

        self.model_button_undo = self.get_button(_('Undo'), keyboard_shortcut=_('Ctrl') + '+Z')
        self.model_button_redo = self.get_button(_('Redo'), keyboard_shortcut=_('Shift') + '+' + _('Ctrl') + '+Z')
        self.model_button_cut = self.get_button(_('Cut'), keyboard_shortcut=_('Ctrl') + '+X')
        self.model_button_copy = self.get_button(_('Copy'), keyboard_shortcut=_('Ctrl') + '+C')
        self.model_button_paste = self.get_button(_('Paste'), keyboard_shortcut=_('Ctrl') + '+V')
        self.model_button_delete = self.get_button(_('Delete'), keyboard_shortcut=None)
        self.model_button_select_all = self.get_button(_('Select All'), keyboard_shortcut=_('Ctrl') + '+A')

        box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        box.set_margin_left(10)
        box.set_margin_right(10)
        box.pack_start(self.model_button_undo, False, False, 0)
        box.pack_start(self.model_button_redo, False, False, 0)
        box.pack_start(Gtk.SeparatorMenuItem(), False, False, 0)
        box.pack_start(self.model_button_cut, False, False, 0)
        box.pack_start(self.model_button_copy, False, False, 0)
        box.pack_start(self.model_button_paste, False, False, 0)
        box.pack_start(self.model_button_delete, False, False, 0)
        box.pack_start(Gtk.SeparatorMenuItem(), False, False, 0)
        box.pack_start(self.model_button_select_all, False, False, 0)
        box.pack_start(Gtk.SeparatorMenuItem(), False, False, 0)
        self.pack_start(box, False, False, 0)

        if document.is_latex_document():
            box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
            box.set_margin_left(10)
            box.set_margin_right(10)
            self.model_button_toggle_comment = self.get_button(_('Toggle Comment'), keyboard_shortcut=_('Ctrl') + '+K')
            self.model_button_show_in_preview = self.get_button(_('Show in Preview'), keyboard_shortcut=None)

            box.pack_start(self.model_button_toggle_comment, False, False, 0)
            box.pack_start(self.model_button_show_in_preview, False, False, 0)
            box.pack_start(Gtk.SeparatorMenuItem(), False, False, 0)
            self.pack_start(box, False, False, 0)

        box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        box.set_margin_left(15)
        box.set_margin_right(7)
        zoom_label = Gtk.Label(_('Zoom'))
        zoom_label.set_xalign(0)
        zoom_label.set_margin_right(36)
        box.pack_start(zoom_label, True, True, 0)
        self.model_button_zoom_out = Gtk.ModelButton()
        self.model_button_zoom_out.set_image(Gtk.Image.new_from_icon_name('value-decrease-symbolic', Gtk.IconSize.MENU))
        self.model_button_zoom_out.set_action_name('win.zoom-out')
        box.pack_start(self.model_button_zoom_out, False, False, 0)
        self.model_button_reset_zoom = self.get_button('', keyboard_shortcut=None)
        self.model_button_reset_zoom.set_label('100%')
        self.model_button_reset_zoom.set_action_name('win.reset-zoom')
        self.model_button_reset_zoom.set_size_request(53, -1)
        box.pack_start(self.model_button_reset_zoom, False, False, 0)
        self.model_button_zoom_in = Gtk.ModelButton()
        self.model_button_zoom_in.set_image(Gtk.Image.new_from_icon_name('value-increase-symbolic', Gtk.IconSize.MENU))
        self.model_button_zoom_in.set_action_name('win.zoom-in')
        box.pack_start(self.model_button_zoom_in, False, False, 0)
        self.pack_start(box, False, False, 0)

        self.show_all()

    def get_button(self, label, keyboard_shortcut=None):
        model_button = Gtk.ModelButton()
        button_box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        if keyboard_shortcut != None:
            shortcut = Gtk.Label(keyboard_shortcut)
            shortcut.get_style_context().add_class('keyboard-shortcut')
            button_box.pack_end(shortcut, False, False, 0)
            description = Gtk.Label(label)
            description.set_halign(Gtk.Align.START)
            button_box.pack_start(description, True, True, 0)
            model_button.remove(model_button.get_child())
            model_button.add(button_box)
        else:
            model_button.set_label(label)
            model_button.get_child().set_halign(Gtk.Align.START)
        return model_button


class RCMenuView(object):
    
    def __init__(self):
        self.menu_item_cut = Gtk.MenuItem.new_with_label(_('Cut'))
        self.menu_item_copy = Gtk.MenuItem.new_with_label(_('Copy'))
        self.menu_item_paste = Gtk.MenuItem.new_with_label(_('Paste'))
        self.menu_item_delete = Gtk.MenuItem.new_with_label(_('Delete'))
        self.menu_item_select_all = Gtk.MenuItem.new_with_label(_('Select All'))
        self.menu_item_comment = Gtk.MenuItem.new_with_label(_('Toggle Comment'))
        self.menu_item_show_in_preview = Gtk.MenuItem.new_with_label(_('Show in Preview'))
        self.separator_menu_item1 = Gtk.SeparatorMenuItem()
        self.separator_menu_item2 = Gtk.SeparatorMenuItem()



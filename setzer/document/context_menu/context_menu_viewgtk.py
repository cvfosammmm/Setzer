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


class ContextMenuView(Gtk.VBox):
    
    def __init__(self, document):
        Gtk.VBox.__init__(self)

        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_left(10)
        self.set_margin_right(10)

        self.model_button_undo = self.get_button(_('Undo'), keyboard_shortcut=_('Ctrl') + '+Z')
        self.model_button_redo = self.get_button(_('Redo'), keyboard_shortcut=_('Shift') + '+' + _('Ctrl') + '+Z')
        self.model_button_cut = self.get_button(_('Cut'), keyboard_shortcut=_('Ctrl') + '+X')
        self.model_button_copy = self.get_button(_('Copy'), keyboard_shortcut=_('Ctrl') + '+C')
        self.model_button_paste = self.get_button(_('Paste'), keyboard_shortcut=_('Ctrl') + '+V')
        self.model_button_delete = self.get_button(_('Delete'), keyboard_shortcut=None)
        self.model_button_select_all = self.get_button(_('Select All'), keyboard_shortcut=_('Ctrl') + '+A')

        self.pack_start(self.model_button_undo, False, False, 0)
        self.pack_start(self.model_button_redo, False, False, 0)
        self.pack_start(Gtk.SeparatorMenuItem(), False, False, 0)
        self.pack_start(self.model_button_cut, False, False, 0)
        self.pack_start(self.model_button_copy, False, False, 0)
        self.pack_start(self.model_button_paste, False, False, 0)
        self.pack_start(self.model_button_delete, False, False, 0)
        self.pack_start(Gtk.SeparatorMenuItem(), False, False, 0)
        self.pack_start(self.model_button_select_all, False, False, 0)
        self.pack_start(Gtk.SeparatorMenuItem(), False, False, 0)

        zoom_box = Gtk.HBox()
        zoom_label = Gtk.Label(_('Zoom'))
        zoom_label.set_xalign(0)
        zoom_label.set_margin_left(5)
        zoom_box.pack_start(zoom_label, True, True, 0)
        self.model_button_zoom_out = self.get_button('-', keyboard_shortcut=None)
        self.model_button_zoom_out.set_action_name('win.zoom-out')
        zoom_box.pack_start(self.model_button_zoom_out, False, False, 0)
        self.model_button_reset_zoom = self.get_button('', keyboard_shortcut=None)
        self.model_button_reset_zoom.set_label('100%')
        self.model_button_reset_zoom.set_action_name('win.reset-zoom')
        self.model_button_reset_zoom.set_size_request(53, -1)
        zoom_box.pack_start(self.model_button_reset_zoom, False, False, 0)
        self.model_button_zoom_in = self.get_button('+', keyboard_shortcut=None)
        self.model_button_zoom_in.set_action_name('win.zoom-in')
        zoom_box.pack_start(self.model_button_zoom_in, False, False, 0)
        self.pack_start(zoom_box, False, False, 0)

        if document.is_latex_document():
            self.model_button_toggle_comment = self.get_button(_('Toggle Comment'), keyboard_shortcut=_('Ctrl') + '+K')
            self.model_button_show_in_preview = self.get_button(_('Show in Preview'), keyboard_shortcut=None)

            self.pack_start(Gtk.SeparatorMenuItem(), False, False, 0)
            self.pack_start(self.model_button_toggle_comment, False, False, 0)
            self.pack_start(self.model_button_show_in_preview, False, False, 0)

        self.show_all()

    def get_button(self, label, keyboard_shortcut=None):
        model_button = Gtk.ModelButton()
        button_box = Gtk.HBox()
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



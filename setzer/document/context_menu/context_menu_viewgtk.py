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

        self.model_button_undo = Gtk.ModelButton()
        self.model_button_undo.set_label(_('Undo'))
        self.model_button_undo.get_child().set_halign(Gtk.Align.START)

        self.model_button_redo = Gtk.ModelButton()
        self.model_button_redo.set_label(_('Redo'))
        self.model_button_redo.get_child().set_halign(Gtk.Align.START)

        self.model_button_cut = Gtk.ModelButton()
        self.model_button_cut.set_label(_('Cut'))
        self.model_button_cut.get_child().set_halign(Gtk.Align.START)

        self.model_button_copy = Gtk.ModelButton()
        self.model_button_copy.set_label(_('Copy'))
        self.model_button_copy.get_child().set_halign(Gtk.Align.START)

        self.model_button_paste = Gtk.ModelButton()
        self.model_button_paste.set_label(_('Paste'))
        self.model_button_paste.get_child().set_halign(Gtk.Align.START)

        self.model_button_delete = Gtk.ModelButton()
        self.model_button_delete.set_label(_('Delete'))
        self.model_button_delete.get_child().set_halign(Gtk.Align.START)

        self.model_button_select_all = Gtk.ModelButton()
        self.model_button_select_all.set_label(_('Select All'))
        self.model_button_select_all.get_child().set_halign(Gtk.Align.START)

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

        if document.is_latex_document():
            self.model_button_toggle_comment = Gtk.ModelButton()
            self.model_button_toggle_comment.set_label(_('Toggle Comment'))
            self.model_button_toggle_comment.get_child().set_halign(Gtk.Align.START)
            self.model_button_show_in_preview = Gtk.ModelButton()
            self.model_button_show_in_preview.set_label(_('Show in Preview'))
            self.model_button_show_in_preview.get_child().set_halign(Gtk.Align.START)
            self.pack_start(self.model_button_toggle_comment, False, False, 0)
            self.pack_start(self.model_button_show_in_preview, False, False, 0)

        self.show_all()



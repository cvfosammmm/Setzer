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
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import Pango


class OpenDocsPopover(Gtk.Popover):
    ''' Shows open documents. '''
    
    def __init__(self):
        Gtk.Popover.__init__(self)
        self.get_style_context().add_class('open-docs-popover')

        self.vbox = Gtk.VBox()
        
        self.document_list = Gtk.ListBox()
        self.document_list.set_sort_func(self.sort_function)

        self.in_selection_mode = False

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.add(self.document_list)
        self.scrolled_window.set_max_content_height(395)
        self.scrolled_window.set_max_content_width(398)
        self.scrolled_window.set_propagate_natural_height(True)
        self.scrolled_window.set_propagate_natural_width(True)
        self.scrolled_window.set_shadow_type(Gtk.ShadowType.NONE)

        self.mbox = Gtk.HBox()
        self.mbox.get_style_context().add_class('mbox')
        self.set_master_document_button = Gtk.Button()
        self.set_master_document_button.set_label('Set one Document as Master')
        self.set_master_document_button.set_halign(Gtk.Align.START)
        self.set_master_document_button.get_style_context().add_class('small')
        self.unset_master_document_button = Gtk.Button()
        self.unset_master_document_button.set_label('Unset Master Document')
        self.unset_master_document_button.set_halign(Gtk.Align.START)
        self.unset_master_document_button.get_style_context().add_class('flat')
        self.mbox.pack_start(self.set_master_document_button, True, True, 0)
        self.mbox.pack_end(self.unset_master_document_button, True, True, 0)

        self.master_explaination1 = Gtk.Label('Click on a document in the list below to set it as master.')
        self.master_explaination1.set_margin_top(9)
        self.master_explaination1.set_xalign(0)
        self.master_explaination1.get_style_context().add_class('explaination-header')
        self.master_explaination2 = Gtk.Label('The master document will get built, no matter which document you \nare currently editing, and it will always display in the .pdf preview. \nThe build log will also refer to the master document. \nThis is often useful for working on large projects where typically a \ntop level document (the master) will contain multiple lower level \nfiles via include statements.')
        self.master_explaination2.set_xalign(0)
        self.master_explaination2.get_style_context().add_class('explaination')
        self.master_explaination2.set_margin_top(14)
        self.master_explaination_box = Gtk.VBox()
        self.master_explaination_box.pack_start(self.master_explaination1, False, False, 0)
        self.master_explaination_box.pack_start(self.master_explaination2, False, False, 0)
        self.master_explaination_revealer = Gtk.Revealer()
        self.master_explaination_revealer.add(self.master_explaination_box)
        self.master_explaination_revealer.set_reveal_child(False)
        self.master_explaination_revealer.set_margin_bottom(6)
        self.vbox.pack_start(self.master_explaination_revealer, False, False, 0)
        self.vbox.pack_start(self.scrolled_window, False, False, 0)
        self.vbox.pack_start(Gtk.Separator(), False, False, 0)
        self.vbox.pack_start(self.mbox, False, False, 0)
        self.vbox.show_all()
        self.add(self.vbox)
        
    def remove_document(self, list_item):
        self.document_list.remove(list_item)

    def sort_function(self, row1, row2, user_data=None):
        date1 = row1.document.get_last_activated()
        date2 = row2.document.get_last_activated()
        if date1 < date2:
            return 1
        elif date1 == date2:
            return 0
        else:
            return -1



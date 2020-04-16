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

from setzer.app.service_locator import ServiceLocator


class OpenDocsButton(Gtk.Stack):
    
    def __init__(self):
        Gtk.Stack.__init__(self)

        self.mod_binding = None
        self.document_mod_label = Gtk.Label()
        self.name_binding = None
        self.document_name_label = Gtk.Label()
        self.document_name_label.get_style_context().add_class('title')
        self.document_name_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.folder_binding = None
        self.document_folder_label = Gtk.Label()
        self.document_folder_label.get_style_context().add_class('subtitle')
        self.document_folder_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.document_arrow = Gtk.Image.new_from_icon_name('pan-down-symbolic', Gtk.IconSize.MENU)
        vbox = Gtk.VBox()
        vbox.pack_start(self.document_name_label, False, False, 0)
        vbox.pack_start(self.document_folder_label, False, False, 0)
        hbox = Gtk.HBox()
        hbox.pack_start(vbox, False, False, 0)
        hbox.pack_start(self.document_arrow, False, False, 0)
        hbox.set_valign(Gtk.Align.CENTER)
        
        self.open_docs_popover = OpenDocsPopover()
        self.center_button = Gtk.MenuButton()
        self.center_button.get_style_context().add_class('flat')
        self.center_button.get_style_context().add_class('open-docs-popover-button')
        self.center_button.set_tooltip_text(_('Show open documents') + ' (' + _('Ctrl') + '+T)')
        self.center_button.set_can_focus(False)
        self.center_button.add(hbox)
        self.center_button.set_use_popover(True)
        self.center_button.set_popover(self.open_docs_popover)
        self.center_label_welcome = Gtk.Label('Setzer')
        self.center_label_welcome.get_style_context().add_class('title')

        self.add_named(self.center_button, 'button')
        self.add_named(self.center_label_welcome, 'welcome')

        self.set_valign(Gtk.Align.FILL)
        self.center_button.set_valign(Gtk.Align.FILL)
        self.center_label_welcome.set_valign(Gtk.Align.FILL)

        self.set_size_request(-1, 46)

        self.show_all()


class OpenDocsPopover(Gtk.PopoverMenu):
    ''' Shows open documents. '''
    
    def __init__(self):
        Gtk.PopoverMenu.__init__(self)
        self.get_style_context().add_class('open-docs-popover')
        self.pmb = ServiceLocator.get_popover_menu_builder()
        self.stack = self.get_child()

        self.vbox = Gtk.VBox()
        self.vbox.set_margin_top(9)
        self.vbox.set_margin_bottom(10)
        self.vbox.set_margin_left(10)
        self.vbox.set_margin_right(10)

        self.document_list = Gtk.ListBox()
        self.document_list.set_sort_func(self.sort_function)

        self.document_list_selection = Gtk.ListBox()
        self.document_list_selection.set_sort_func(self.sort_function)

        self.in_selection_mode = False

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.add(self.document_list)
        self.scrolled_window.set_max_content_height(336)
        self.scrolled_window.set_max_content_width(398)
        self.scrolled_window.set_propagate_natural_height(True)
        self.scrolled_window.set_propagate_natural_width(True)
        self.scrolled_window.set_shadow_type(Gtk.ShadowType.NONE)

        self.mbox = Gtk.HBox()
        self.set_master_document_button = Gtk.Button()
        self.set_master_document_button.set_label(_('Set one Document as Master'))
        self.set_master_document_button.set_halign(Gtk.Align.START)
        self.set_master_document_button.get_style_context().add_class('flat')
        self.set_master_document_button.get_style_context().add_class('like-model')
        self.set_master_document_button.set_can_focus(False)
        self.unset_master_document_button = Gtk.Button()
        self.unset_master_document_button.set_margin_left(18)
        self.unset_master_document_button.set_label(_('Unset Master Document'))
        self.unset_master_document_button.set_halign(Gtk.Align.START)
        self.unset_master_document_button.get_style_context().add_class('flat')
        self.unset_master_document_button.get_style_context().add_class('like-model')
        self.unset_master_document_button.set_can_focus(False)
        self.mbox.pack_start(self.set_master_document_button, True, True, 0)
        self.mbox.pack_end(self.unset_master_document_button, True, True, 0)

        self.master_explaination1 = Gtk.Label(_('Click on a document in the list below to set it as master.'))
        self.master_explaination1.set_margin_top(6)
        self.master_explaination1.set_xalign(0)
        self.master_explaination1.get_style_context().add_class('explaination-header')
        self.master_explaination2 = Gtk.Label(_('The master document will get built, no matter which document\nyou are currently editing, and it will always display in the .pdf\npreview. The build log will also refer to the master document.\nThis is often useful for working on large projects where typically\na top level document (the master) will contain multiple lower\nlevel files via include statements.'))
        self.master_explaination2.set_xalign(0)
        self.master_explaination2.get_style_context().add_class('explaination')
        self.master_explaination2.set_margin_top(15)
        self.master_explaination2.set_margin_bottom(10)
        self.master_explaination_box = Gtk.VBox()
        self.master_explaination_box.pack_start(self.master_explaination1, False, False, 0)
        self.master_explaination_box.pack_start(self.master_explaination2, False, False, 0)
        self.master_explaination_revealer = Gtk.Revealer()
        self.master_explaination_revealer.add(self.master_explaination_box)
        self.master_explaination_revealer.set_reveal_child(False)
        self.vbox.pack_start(self.master_explaination_revealer, False, False, 0)
        self.vbox.pack_start(self.scrolled_window, False, False, 0)

        self.pmb.add_separator(self.vbox)

        self.vbox.pack_start(self.mbox, False, False, 0)

        self.vbox.show_all()
        self.stack.add_named(self.vbox, 'main')

    def sort_function(self, row1, row2, user_data=None):
        date1 = row1.document.get_last_activated()
        date2 = row2.document.get_last_activated()
        if date1 < date2:
            return 1
        elif date1 == date2:
            return 0
        else:
            return -1



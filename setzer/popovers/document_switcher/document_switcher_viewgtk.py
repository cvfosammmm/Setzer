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


class DocumentSwitcherView(Popover):

    def __init__(self, popover_manager):
        Popover.__init__(self, popover_manager)

        self.set_width(414)

        self.document_list = Gtk.ListBox()
        self.document_list.set_sort_func(self.sort_function)

        self.document_list_selection = Gtk.ListBox()
        self.document_list_selection.set_sort_func(self.sort_function)

        self.in_selection_mode = False

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_child(self.document_list)
        self.scrolled_window.set_max_content_height(336)
        self.scrolled_window.set_max_content_width(398)
        self.scrolled_window.set_propagate_natural_height(True)
        self.scrolled_window.set_propagate_natural_width(True)

        self.set_root_document_button = MenuBuilder.create_button(_('Set one Document as Root'))
        self.unset_root_document_button = MenuBuilder.create_button(_('Unset Root Document'))

        self.root_explaination1 = Gtk.Label.new(_('Click on a document in the list below to set it as root.'))
        self.root_explaination1.set_margin_top(6)
        self.root_explaination1.set_xalign(0)
        self.root_explaination1.get_style_context().add_class('explaination-header')
        self.root_explaination2 = Gtk.Label.new(_('The root document will get built, no matter which document\nyou are currently editing, and it will always display in the .pdf\npreview. The build log will also refer to the root document.\nThis is often useful for working on large projects where typically\na top level document (the root) will contain multiple lower\nlevel files via include statements.'))
        self.root_explaination2.set_xalign(0)
        self.root_explaination2.get_style_context().add_class('explaination')
        self.root_explaination2.set_margin_top(15)
        self.root_explaination2.set_margin_bottom(10)
        self.root_explaination_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.root_explaination_box.append(self.root_explaination1)
        self.root_explaination_box.append(self.root_explaination2)
        self.root_explaination_revealer = Gtk.Revealer()
        self.root_explaination_revealer.set_child(self.root_explaination_box)
        self.root_explaination_revealer.set_reveal_child(False)

        self.box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.box.get_style_context().add_class('open-docs-popover')
        self.box.append(self.root_explaination_revealer)
        self.box.append(self.scrolled_window)
        self.box.append(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
        self.box.append(self.set_root_document_button)
        self.box.append(self.unset_root_document_button)

        self.add_widget(self.box)

    def sort_function(self, row1, row2, user_data=None):
        date1 = row1.document.get_last_activated()
        date2 = row2.document.get_last_activated()
        if date1 < date2:
            return 1
        elif date1 == date2:
            return 0
        else:
            return -1



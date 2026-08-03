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

from setzer.dialogs.helpers.dialog_viewgtk import DialogView


class GitCommitView(DialogView):

    def __init__(self, main_window):
        DialogView.__init__(self, main_window)

        self.set_default_size(500, 500)
        self.get_style_context().add_class('git-commit-dialog')
        self.headerbar.set_show_title_buttons(False)
        self.headerbar.set_title_widget(Gtk.Label.new(_('Commit and Push')))

        self.cancel_button = Gtk.Button.new_with_mnemonic(_('_Cancel'))
        self.cancel_button.set_can_focus(False)
        self.headerbar.pack_start(self.cancel_button)

        self.commit_button = Gtk.Button.new_with_mnemonic(_('C_ommit & Push'))
        self.commit_button.set_can_focus(False)
        self.commit_button.get_style_context().add_class('suggested-action')
        self.headerbar.pack_end(self.commit_button)

        self.content = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.content.set_vexpand(True)
        self.content.set_margin_start(18)
        self.content.set_margin_end(18)
        self.content.set_margin_bottom(18)
        self.topbox.append(self.content)

        label = Gtk.Label.new(_('Commit message'))
        label.set_xalign(0)
        label.set_margin_bottom(3)
        label.set_margin_top(18)
        self.content.append(label)

        self.message_entry = Gtk.Entry()
        self.message_entry.set_placeholder_text(_('Describe your changes'))
        self.content.append(self.message_entry)

        label = Gtk.Label.new(_('Files to include in the commit'))
        label.set_xalign(0)
        label.set_margin_bottom(3)
        label.set_margin_top(18)
        self.content.append(label)

        self.files_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.files_box.get_style_context().add_class('files')

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_child(self.files_box)
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.get_style_context().add_class('frame')
        self.content.append(self.scrolled_window)

        self.select_all_button = Gtk.Button.new_with_label(_('Select All'))
        self.select_all_button.set_can_focus(False)
        self.select_none_button = Gtk.Button.new_with_label(_('Select None'))
        self.select_none_button.set_can_focus(False)

        select_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
        select_box.set_margin_top(6)
        select_box.append(self.select_all_button)
        select_box.append(self.select_none_button)
        self.content.append(select_box)

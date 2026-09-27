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
from gi.repository import Gtk, Pango


class GitSectionView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('git-section')

        self.label_branch = Gtk.Label()
        self.label_branch.set_xalign(0)
        self.label_branch.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        self.label_branch.get_style_context().add_class('branch')
        self.append(self.label_branch)

        self.label_commit = Gtk.Label()
        self.label_commit.set_xalign(0)
        self.label_commit.set_wrap(True)
        self.label_commit.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.label_commit.set_lines(2)
        self.label_commit.set_ellipsize(Pango.EllipsizeMode.END)
        self.label_commit.get_style_context().add_class('commit')
        self.append(self.label_commit)

        self.label_status = Gtk.Label()
        self.label_status.set_xalign(0)
        self.label_status.set_wrap(True)
        self.label_status.get_style_context().add_class('description')
        self.append(self.label_status)

        self.buttons_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
        self.buttons_box.get_style_context().add_class('buttons')

        self.button_pull = Gtk.Button.new_with_label(_('Pull'))
        self.button_pull.set_tooltip_text(_('Fetch and fast forward to the remote branch'))
        self.button_pull.set_hexpand(True)
        self.button_pull.set_can_focus(False)
        self.buttons_box.append(self.button_pull)

        self.button_push = Gtk.Button.new_with_label(_('Commit & Push'))
        self.button_push.set_tooltip_text(_('Commit your changes and push them to the remote branch'))
        self.button_push.set_hexpand(True)
        self.button_push.set_can_focus(False)
        self.buttons_box.append(self.button_push)

        self.append(self.buttons_box)

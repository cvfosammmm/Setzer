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


class GitCredentialsView(DialogView):

    def __init__(self, main_window, host):
        DialogView.__init__(self, main_window)

        self.set_default_size(400, -1)
        self.get_style_context().add_class('git-credentials-dialog')
        self.headerbar.set_show_title_buttons(False)
        self.headerbar.set_title_widget(Gtk.Label.new(_('Sign In')))
        self.topbox.set_size_request(400, -1)

        self.cancel_button = Gtk.Button.new_with_mnemonic(_('_Cancel'))
        self.cancel_button.set_can_focus(False)
        self.headerbar.pack_start(self.cancel_button)

        self.login_button = Gtk.Button.new_with_mnemonic(_('_Sign In'))
        self.login_button.set_can_focus(False)
        self.login_button.get_style_context().add_class('suggested-action')
        self.headerbar.pack_end(self.login_button)

        self.content = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.content.set_vexpand(True)
        self.content.set_margin_start(18)
        self.content.set_margin_end(18)
        self.content.set_margin_bottom(18)
        self.topbox.append(self.content)

        description = Gtk.Label.new(_('The remote repository at “{host}” requires you to sign in.').format(host=host))
        description.set_wrap(True)
        description.set_xalign(0)
        description.set_margin_top(18)
        self.content.append(description)

        label = Gtk.Label.new(_('Username'))
        label.set_xalign(0)
        label.set_margin_bottom(3)
        label.set_margin_top(18)
        self.content.append(label)

        self.username_entry = Gtk.Entry()
        self.content.append(self.username_entry)

        label = Gtk.Label.new(_('Password or access token'))
        label.set_xalign(0)
        label.set_margin_bottom(3)
        label.set_margin_top(18)
        self.content.append(label)

        self.password_entry = Gtk.PasswordEntry()
        self.password_entry.set_show_peek_icon(True)
        self.content.append(self.password_entry)

        self.remember_button = Gtk.CheckButton.new_with_label(_('Remember these credentials'))
        self.remember_button.set_margin_top(18)
        self.content.append(self.remember_button)

        hint = Gtk.Label.new(_('Setzer never stores your credentials itself, it hands them to git, which saves them with the credential helper configured on your system. Without this option they are only kept in memory for 15 minutes.'))
        hint.set_wrap(True)
        hint.set_xalign(0)
        hint.set_margin_top(6)
        hint.get_style_context().add_class('description')
        self.content.append(hint)

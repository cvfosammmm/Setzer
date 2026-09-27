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

import setzer.dialogs.git_credentials.git_credentials_viewgtk as view


class GitCredentialsDialog(object):

    def __init__(self, main_window):
        self.main_window = main_window
        self.callback = None
        self.has_responded = True

    def run(self, description, callback):
        self.callback = callback
        self.has_responded = False

        self.view = view.GitCredentialsView(self.main_window, description['host'])
        self.view.username_entry.set_text(description.get('username', ''))
        self.view.remember_button.set_active(True)

        self.view.cancel_button.connect('clicked', self.on_cancel_button_clicked)
        self.view.login_button.connect('clicked', self.on_login_button_clicked)
        self.view.username_entry.connect('changed', self.on_state_changed)
        self.view.username_entry.connect('activate', self.on_entry_activated)
        self.view.password_entry.connect('changed', self.on_state_changed)
        self.view.password_entry.connect('activate', self.on_entry_activated)
        self.view.connect('close-request', self.on_close_request)

        self.update_login_button()
        self.view.present()
        if self.view.username_entry.get_text() == '':
            self.view.username_entry.grab_focus()
        else:
            self.view.password_entry.grab_focus()

    def on_state_changed(self, widget):
        self.update_login_button()

    def update_login_button(self):
        has_username = self.view.username_entry.get_text().strip() != ''
        has_password = self.view.password_entry.get_text() != ''
        self.view.login_button.set_sensitive(has_username and has_password)

    def on_entry_activated(self, entry):
        if self.view.login_button.get_sensitive():
            self.on_login_button_clicked(self.view.login_button)

    def on_cancel_button_clicked(self, button):
        self.finish(None)

    def on_login_button_clicked(self, button):
        self.finish({'username': self.view.username_entry.get_text().strip(),
                     'password': self.view.password_entry.get_text(),
                     'remember': self.view.remember_button.get_active()})

    def on_close_request(self, window):
        self.finish(None)
        return False

    def finish(self, response):
        if self.has_responded: return
        self.has_responded = True

        self.view.password_entry.set_text('')
        self.view.close()
        if self.callback != None:
            self.callback(response)

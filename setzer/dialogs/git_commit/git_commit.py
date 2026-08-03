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

import setzer.dialogs.git_commit.git_commit_viewgtk as view


class GitCommitDialog(object):

    def __init__(self, main_window):
        self.main_window = main_window
        self.callback = None
        self.has_responded = True
        self.check_buttons = list()

    def run(self, changed_files, callback):
        self.callback = callback
        self.has_responded = False
        self.check_buttons = list()

        self.view = view.GitCommitView(self.main_window)
        self.populate_files(changed_files)

        self.view.cancel_button.connect('clicked', self.on_cancel_button_clicked)
        self.view.commit_button.connect('clicked', self.on_commit_button_clicked)
        self.view.select_all_button.connect('clicked', self.on_select_all_button_clicked)
        self.view.select_none_button.connect('clicked', self.on_select_none_button_clicked)
        self.view.message_entry.connect('changed', self.on_state_changed)
        self.view.message_entry.connect('activate', self.on_message_entry_activated)
        self.view.connect('close-request', self.on_close_request)

        self.update_commit_button()
        self.view.present()
        self.view.message_entry.grab_focus()

    def populate_files(self, changed_files):
        for item in changed_files:
            check_button = Gtk.CheckButton()
            check_button.set_label(item['path'])
            check_button.set_tooltip_text(get_status_description(item['status']) + ': ' + item['path'])

            # untracked files are unchecked by default, so build artifacts
            # don't end up in the repository by accident
            check_button.set_active(item['status'] != '??')
            check_button.connect('toggled', self.on_state_changed)

            box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
            box.get_style_context().add_class('file-row')
            box.append(check_button)

            status_label = Gtk.Label.new(get_status_description(item['status']))
            status_label.set_halign(Gtk.Align.END)
            status_label.set_hexpand(True)
            status_label.get_style_context().add_class('description')
            box.append(status_label)

            self.view.files_box.append(box)
            self.check_buttons.append((check_button, item))

    def get_selected_paths(self):
        paths = list()
        for check_button, item in self.check_buttons:
            if not check_button.get_active(): continue
            paths.append(item['path'])

            # a rename only becomes one if the original path is committed too
            if item.get('old_path') != None:
                paths.append(item['old_path'])
        return paths

    def on_state_changed(self, widget):
        self.update_commit_button()

    def update_commit_button(self):
        has_message = self.view.message_entry.get_text().strip() != ''
        has_files = len(self.get_selected_paths()) > 0
        self.view.commit_button.set_sensitive(has_message and has_files)

    def on_select_all_button_clicked(self, button):
        for check_button, item in self.check_buttons:
            check_button.set_active(True)

    def on_select_none_button_clicked(self, button):
        for check_button, item in self.check_buttons:
            check_button.set_active(False)

    def on_message_entry_activated(self, entry):
        if self.view.commit_button.get_sensitive():
            self.on_commit_button_clicked(self.view.commit_button)

    def on_cancel_button_clicked(self, button):
        self.finish(None)

    def on_commit_button_clicked(self, button):
        self.finish({'message': self.view.message_entry.get_text().strip(), 'paths': self.get_selected_paths()})

    def on_close_request(self, window):
        self.finish(None)
        return False

    def finish(self, response):
        if self.has_responded: return
        self.has_responded = True

        self.view.close()
        if self.callback != None:
            self.callback(response)


def get_status_description(status):
    if status == '??': return _('New')
    if 'D' in status: return _('Deleted')
    if 'R' in status: return _('Renamed')
    if 'A' in status: return _('Added')
    if 'U' in status: return _('Conflicted')
    return _('Modified')

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
from gi.repository import Gtk, GLib

import time

from setzer.app.service_locator import ServiceLocator


class GitSectionPresenter(object):

    def __init__(self, git_section):
        self.git_section = git_section
        self.view = git_section.view

        self.git_section.connect('git_state_changed', self.on_git_state_changed)
        self.git_section.connect('git_error', self.on_git_error)
        self.git_section.connect('git_info', self.on_git_info)

    def on_git_state_changed(self, git_section):
        self.update()

    def update(self):
        is_visible = self.git_section.is_available() and self.git_section.repo_path != None
        self.set_section_visible(is_visible)
        if not is_visible: return

        self.view.label_branch.set_markup(self.get_branch_markup())
        self.view.label_commit.set_markup(self.get_commit_markup())
        self.view.label_status.set_text(self.get_status_text())

        is_idle = (self.git_section.busy == None)
        self.view.button_pull.set_sensitive(is_idle)
        self.view.button_push.set_sensitive(is_idle)

        if self.git_section.busy == 'pull':
            self.view.button_pull.set_label(_('Pulling…'))
        else:
            self.view.button_pull.set_label(_('Pull'))

        if self.git_section.busy == 'push':
            self.view.button_push.set_label(_('Pushing…'))
        else:
            self.view.button_push.set_label(_('Commit & Push'))

    def set_section_visible(self, is_visible):
        self.view.set_visible(is_visible)
        self.git_section.headline_labels['inline'].set_visible(is_visible)
        if not is_visible:
            self.git_section.headline_labels['overlay'].set_visible(False)

    def get_branch_markup(self):
        if self.git_section.branch == None:
            markup = '<b>' + GLib.markup_escape_text(_('Detached HEAD')) + '</b>'
        else:
            markup = '<b>' + GLib.markup_escape_text(self.git_section.branch) + '</b>'

        divergence = list()
        if self.git_section.ahead > 0:
            divergence.append('↑' + str(self.git_section.ahead))
        if self.git_section.behind > 0:
            divergence.append('↓' + str(self.git_section.behind))
        if len(divergence) > 0:
            markup += '  ' + ' '.join(divergence)

        return markup

    def get_commit_markup(self):
        if self.git_section.last_commit == None:
            return '<i>' + GLib.markup_escape_text(_('No commits yet.')) + '</i>'
        return GLib.markup_escape_text(self.git_section.last_commit['subject'])

    def get_status_text(self):
        parts = list()

        if self.git_section.last_commit != None:
            parts.append(format_date(self.git_section.last_commit['timestamp']))
            parts.append(self.git_section.last_commit['author'])

        count = len(self.git_section.changed_files)
        if count == 0:
            parts.append(_('no local changes'))
        else:
            parts.append(ngettext('{amount} changed file', '{amount} changed files', count).format(amount=count))

        return ' · '.join(parts)

    def on_git_error(self, git_section, error):
        dialog = Gtk.AlertDialog()
        dialog.set_modal(True)
        dialog.set_message(error['title'])
        dialog.set_detail(error['message'])
        dialog.set_buttons([_('_OK')])
        dialog.show(ServiceLocator.get_main_window())

    def on_git_info(self, git_section, message):
        dialog = Gtk.AlertDialog()
        dialog.set_modal(True)
        dialog.set_message(message)
        dialog.set_buttons([_('_OK')])
        dialog.show(ServiceLocator.get_main_window())


def format_date(timestamp):
    seconds = max(0, int(time.time()) - timestamp)

    if seconds < 60:
        return _('just now')
    if seconds < 3600:
        amount = seconds // 60
        return ngettext('{amount} minute ago', '{amount} minutes ago', amount).format(amount=amount)
    if seconds < 86400:
        amount = seconds // 3600
        return ngettext('{amount} hour ago', '{amount} hours ago', amount).format(amount=amount)
    if seconds < 604800:
        amount = seconds // 86400
        return ngettext('{amount} day ago', '{amount} days ago', amount).format(amount=amount)

    return GLib.DateTime.new_from_unix_local(timestamp).format('%x')

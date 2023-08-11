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

import os.path


class InterpreterMissingDialog(object):

    def __init__(self, main_window, preferences_dialog):
        self.main_window = main_window
        self.preferences_dialog = preferences_dialog

    def run(self, interpreter_name):
        self.setup(interpreter_name)
        self.view.show()
        self.signal_connection_id = self.view.connect('response', self.process_response)

    def process_response(self, view, response_id):
        if response_id == Gtk.ResponseType.YES:
            self.preferences_dialog.run()
        self.close()

    def close(self):
        self.view.hide()
        self.view.disconnect(self.signal_connection_id)
        del(self.view)

    def setup(self, interpreter_name):
        self.view = Gtk.MessageDialog()
        self.view.set_transient_for(self.main_window)
        self.view.set_modal(True)
        self.view.set_property('message-type', Gtk.MessageType.QUESTION)

        self.view.set_property('text', _('LateX Interpreter is missing.'))
        self.view.set_property('secondary-text', _('''Setzer is configured to use »{interpreter}« which seems to be missing on this system.

To choose a different interpreter go to Preferences.

For instructions on installing LaTeX see <a href="https://en.wikibooks.org/wiki/LaTeX/Installation">https://en.wikibooks.org/wiki/LaTeX/Installation</a>''').format(interpreter=interpreter_name))
        self.view.set_property('secondary-use-markup', True)

        self.view.add_buttons(_('_Cancel'), Gtk.ResponseType.CANCEL, _('_Go to Preferences'), Gtk.ResponseType.YES)
        self.view.set_default_response(Gtk.ResponseType.YES)



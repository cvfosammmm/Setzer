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


class BuildingFailedDialog(object):

    def __init__(self, main_window, preferences_dialog):
        self.main_window = main_window
        self.preferences_dialog = preferences_dialog

    def run(self, error_message):
        self.setup(error_message)
        self.view.choose(self.main_window, None, self.dialog_process_response)

    def setup(self, error_message):
        self.view = Gtk.AlertDialog()
        self.view.set_modal(True)
        self.view.set_message(_('Something went wrong.'))
        self.view.set_detail(_('''The build process ended unexpectedly returning "{error_message}".

To configure your build system go to Preferences.''').format(error_message=error_message))
        self.view.set_buttons([_('_Cancel'), _('_Go to Preferences')])
        self.view.set_cancel_button(0)
        self.view.set_default_button(1)

    def dialog_process_response(self, dialog, result):
        index = dialog.choose_finish(result)
        if index == 1:
            self.preferences_dialog.run()



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


class CloseConfirmationDialog(object):

    def __init__(self, main_window, workspace):
        self.main_window = main_window
        self.workspace = workspace
        self.parameters = None

    def run(self, parameters, callback):
        if parameters['unsaved_document'] == None: return

        self.parameters = parameters
        self.callback = callback

        self.setup(self.parameters['unsaved_document'])
        self.view.choose(self.main_window, None, self.dialog_process_response)

    def setup(self, document):
        self.view = Gtk.AlertDialog()
        self.view.set_modal(True)
        self.view.set_message(_('Document »{document}« has unsaved changes.').format(document=document.get_displayname()))
        self.view.set_detail(_('If you close without saving, these changes will be lost.'))
        self.view.set_buttons([_('Close _without Saving'), _('_Cancel'), _('_Save')])
        self.view.set_cancel_button(1)
        self.view.set_default_button(2)

    def dialog_process_response(self, dialog, result):
        self.parameters['response'] = dialog.choose_finish(result)
        self.callback(self.parameters)



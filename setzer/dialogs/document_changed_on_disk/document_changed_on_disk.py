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


class DocumentChangedOnDiskDialog(object):

    def __init__(self, main_window):
        self.main_window = main_window
        self.parameters = None
        self.callback = None

    def run(self, parameters, callback):
        if parameters['document'] == None: return

        self.parameters = parameters
        self.callback = callback

        self.setup(self.parameters['document'])
        self.view.choose(self.main_window, None, self.dialog_process_response)

    def setup(self, document):
        self.view = Gtk.AlertDialog()
        self.view.set_modal(True)
        self.view.set_message(_('Document »{document}« has changed on disk.').format(document=document.get_displayname()))
        self.view.set_detail(_('Should Setzer reload it now?'))
        self.view.set_buttons([_('_Keep the current Version'), _('_Reload from Disk')])
        self.view.set_cancel_button(0)
        self.view.set_default_button(1)

    def dialog_process_response(self, dialog, result):
        index = dialog.choose_finish(result)
        self.callback(index == 1)



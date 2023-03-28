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
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from setzer.dialogs.dialog import Dialog

import os.path


class DocumentChangedOnDiskDialog(Dialog):
    ''' This dialog is asking whether a file that changed on disk should be reloaded. '''

    def __init__(self, main_window):
        self.main_window = main_window

    def run(self, document):
        view = self.setup(document)

        response = view.run()
        if response == Gtk.ResponseType.YES:
            value = True
        else:
            value = False

        view.hide()
        return value

    def setup(self, document):
        view = Gtk.MessageDialog(self.main_window, 0, Gtk.MessageType.QUESTION)

        view.set_property('text', _('Document »{document}« has changed on disk.').format(document=document.get_displayname()))
        view.format_secondary_markup(_('Should Setzer reload it now?'))

        view.add_buttons(_('_Keep the current Version'), Gtk.ResponseType.CANCEL, _('_Reload from Disk'), Gtk.ResponseType.YES)
        view.set_default_response(Gtk.ResponseType.YES)
        return view



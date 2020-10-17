#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017, 2018 Robert Griesel
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


class DocumentDeletedOnDiskDialog(Dialog):
    ''' This dialog is warning the user that a file was deleted. '''

    def __init__(self, main_window):
        self.main_window = main_window

    def run(self, document):
        self.setup(document)

        self.view.run()
        self.close()

    def setup(self, document):
        self.view = Gtk.MessageDialog(self.main_window, 0, Gtk.MessageType.WARNING)

        self.view.set_property('text', _('Document »{document}« was deleted from disk or moved.').format(document=document.get_displayname()))
        self.view.format_secondary_markup(_('If you close it or close Setzer without saving, this document will be lost.'))

        self.view.add_buttons(_('Ok'), Gtk.ResponseType.YES)
        self.view.set_default_response(Gtk.ResponseType.YES)
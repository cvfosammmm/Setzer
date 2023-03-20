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


class ReplaceConfirmationDialog(Dialog):
    ''' This dialog is asking users if they really want to do a replace all. '''

    def __init__(self, main_window):
        self.main_window = main_window

    def run(self, original, replacement, number_of_occurrences):
        self.setup(original, replacement, number_of_occurrences)
        response = self.view.run()
        if response == Gtk.ResponseType.YES:
            return_value = True
        else:
            return_value = False
        self.close()
        return return_value

    def setup(self, original, replacement, number_of_occurrences):
        self.view = Gtk.MessageDialog(self.main_window, 0, Gtk.MessageType.QUESTION)

        str_occurrences = ngettext('Replacing {amount} occurence of »{original}« with »{replacement}«.', 'Replacing {amount} occurrences of »{original}« with »{replacement}«.', number_of_occurrences)
        self.view.set_property('text', str_occurrences.format(amount=str(number_of_occurrences), original=original, replacement=replacement))
        self.view.format_secondary_markup(_('Do you really want to do this?'))

        self.view.add_buttons(_('_Cancel'), Gtk.ResponseType.CANCEL, _('_Yes, replace all occurrences'), Gtk.ResponseType.YES)
        self.view.set_default_response(Gtk.ResponseType.YES)



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
gi.require_version('Gspell', '1')
from gi.repository import Gtk
from gi.repository import Gspell

from dialogs.dialog import Dialog

import pickle
import os


class SpellcheckingLanguageDialog(Dialog):

    def __init__(self, main_window, workspace):
        self.main_window = main_window
        self.workspace = workspace
        self.current_values = dict()

    def run(self):
        self.setup()

        response = self.view.run()
        if response == Gtk.ResponseType.OK:
            self.set_language()

        self.view.hide()
        del(self.view)
    
    def setup(self):
        self.view = Gspell.LanguageChooserDialog()
        self.view.set_language_code(self.workspace.spellchecking_language_code)

    def set_language(self):
        self.workspace.set_spellchecking_language(self.view.get_language_code())



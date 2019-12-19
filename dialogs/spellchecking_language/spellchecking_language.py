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
        self.view.set_modal(True)
        self.view.set_transient_for(self.main_window)

        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_title('Spellchecking Language')
        self.headerbar.show_all()
        action_area = self.view.get_action_area()
        cancel_button = action_area.get_children()[0]
        select_button = action_area.get_children()[1]
        action_area.remove(cancel_button)
        action_area.remove(select_button)
        self.headerbar.pack_start(cancel_button)
        self.headerbar.pack_end(select_button)
        select_button.get_style_context().add_class('suggested-action')
        action_area.hide()
        self.view.set_titlebar(self.headerbar)

    def set_language(self):
        self.workspace.set_spellchecking_language(self.view.get_language_code())



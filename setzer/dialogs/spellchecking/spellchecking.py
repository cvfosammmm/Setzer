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
gi.require_version('Gspell', '1')
from gi.repository import Gspell

from setzer.dialogs.dialog import Dialog


class SpellcheckingDialog(Dialog):

    def __init__(self, main_window, workspace):
        self.main_window = main_window
        self.workspace = workspace
        self.current_values = dict()

    def run(self):
        try:
            navigator = self.workspace.get_active_document().spellchecker.spell_navigator
        except AttributeError:
            pass
        else:
            self.setup(navigator)

            response = self.view.run()
            self.view.hide()
            del(self.view)
    
    def setup(self, navigator):
        self.view = Gspell.CheckerDialog.new(self.main_window, navigator)



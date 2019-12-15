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


class Spellchecker(object):

    def __init__(self, source_view):
        self.source_view = source_view
        self.spell_view = Gspell.TextView.get_from_gtk_text_view(self.source_view)
        self.spell_view.basic_setup()
        self.spell_view.set_enable_language_menu(False)

    def set_enabled(self, value):
        self.spell_view.set_inline_spell_checking(value)

    def set_language(self, language):
        pass



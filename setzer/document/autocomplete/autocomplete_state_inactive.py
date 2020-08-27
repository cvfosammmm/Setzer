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


class AutocompleteStateInactive(object):

    def __init__(self, autocomplete):
        self.autocomplete = autocomplete

    def init(self):
        self.autocomplete.view.hide()

    def on_return_press(self):
        return False

    def on_escape_press(self):
        return False

    def on_up_press(self):
        return False

    def on_down_press(self):
        return False

    def on_tab_press(self):
        if self.autocomplete.cursor_inside_word_or_at_end():
            if self.autocomplete.cursor_at_word_end():
                return self.autocomplete.update_autocomplete_position(can_show=True)
            else:
                self.autocomplete.update_autocomplete_position(can_show=True)
                return True
        return False

    def show(self):
        self.autocomplete.change_state('active_visible')

    def hide(self):
        pass

    def focus_show(self):
        pass

    def focus_hide(self):
        pass



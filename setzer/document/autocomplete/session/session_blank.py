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


class SessionBlank(object):

    def __init__(self, autocomplete):
        self.autocomplete = autocomplete
        self.will_show = False

    def on_insert_text(self, buffer, location_iter, text, text_length):
        pass

    def on_delete_range(self, buffer, start_iter, end_iter):
        pass

    def on_tab_press(self):
        if self.autocomplete.document.cursor_inside_latex_command_or_at_end():
            self.autocomplete.update(True)
            if self.autocomplete.document.cursor_at_latex_command_end():
                return self.autocomplete.is_active()
            else:
                return True
        return False

    def update(self, can_show=False):
        self.autocomplete.update_visibility()

    def get_offset(self):
        return 0

    def submit(self):
        pass

    def cancel(self):
        pass

    def is_active(self):
        return False



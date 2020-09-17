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


class StateActiveVisible(object):

    def __init__(self, autocomplete):
        self.autocomplete = autocomplete

    def init(self):
        self.autocomplete.view.show_all()

    def on_return_press(self):
        self.autocomplete.submit()
        return True

    def on_escape_press(self):
        self.hide()
        return True

    def on_up_press(self):
        self.autocomplete.view.select_previous()
        return True

    def on_down_press(self):
        self.autocomplete.view.select_next()
        return True

    def on_tab_press(self):
        if len(self.autocomplete.items) == 1:
            self.autocomplete.submit()
            return True
        else:
            i = self.get_number_of_matching_letters_on_tabpress(self.autocomplete.current_word, 0)

            row = self.autocomplete.view.list.get_selected_row()
            if len('\\' + row.get_child().command['command']) == len(self.autocomplete.current_word) + i:
                self.autocomplete.last_tabbed_command = None
                self.autocomplete.submit()
                return True
            else:
                if i >= 1:
                    text = ('\\' + row.get_child().command['command'])[:len(self.autocomplete.current_word) + i]
                    self.autocomplete.last_tabbed_command = row.get_child().command['command']
                    self.autocomplete.add_text_to_current_word(text)
                    return True
                else:
                    current_word = ('\\' + row.get_child().command['command'])[:len(self.autocomplete.current_word) + 1]
                    i = self.get_number_of_matching_letters_on_tabpress(current_word, 0)

                    if len('\\' + row.get_child().command['command']) == len(current_word) + i:
                        self.autocomplete.last_tabbed_command = None
                        self.autocomplete.submit()
                        return True
                    else:
                        text = ('\\' + row.get_child().command['command'])[:len(current_word) + i]
                        self.autocomplete.last_tabbed_command = row.get_child().command['command']
                        self.autocomplete.add_text_to_current_word(text)
                        return True

    def get_number_of_matching_letters_on_tabpress(self, current_word, offset):
        items = self.autocomplete.provider.get_items(current_word)
        i = offset
        letter_ok = True
        while letter_ok and i < 100:
            testletter = None
            for item in items:
                letter = item['command'][len(current_word) - 1 + i:len(current_word) + i].lower()
                if testletter == None:
                    testletter = letter
                if testletter != letter or len(letter) == 0:
                    letter_ok = False
                    i -= 1
                    break
            i += 1
        return i

    def show(self):
        pass

    def hide(self):
        self.autocomplete.change_state('inactive')

    def focus_show(self):
        pass

    def focus_hide(self):
        self.autocomplete.change_state('active_invisible')



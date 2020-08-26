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


class AutocompleteStateActiveVisible(object):

    def __init__(self, autocomplete):
        self.autocomplete = autocomplete

    def init(self):
        self.autocomplete.view.show_all()

    def on_return_press(self):
        self.autocomplete.autocomplete_submit()
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
        if self.autocomplete.number_of_matches == 1:
            self.autocomplete.autocomplete_submit()
            return True
        else:
            items = self.autocomplete.get_items(self.autocomplete.current_word)

            i = 0
            letter_ok = True
            while letter_ok and i < 100:
                testletter = None
                for item in items:
                    letter = item['command'][len(self.autocomplete.current_word) - 1 + i:len(self.autocomplete.current_word) + i].lower()
                    if testletter == None:
                        testletter = letter
                    if testletter != letter or len(letter) == 0:
                        letter_ok = False
                        i -= 1
                        break
                i += 1

            row = self.autocomplete.view.list.get_selected_row()
            if len(row.get_child().label.get_text()) == len(self.autocomplete.current_word) + i:
                self.autocomplete.autocomplete_submit()
                return True
            else:
                if i >= 1:
                    text = row.get_child().label.get_text()[:len(self.autocomplete.current_word) + i]
                    self.autocomplete.autocomplete_insert(text, select_dot=False)
                    return True
                else:
                    current_word = row.get_child().label.get_text()[:len(self.autocomplete.current_word) + 1]
                    items = self.autocomplete.get_items(current_word)

                    i = 1
                    letter_ok = True
                    while letter_ok and i < 100:
                        testletter = None
                        for item in items:
                            letter = item['command'][len(current_word) - 2 + i:len(current_word) - 1 + i].lower()
                            if testletter == None:
                                testletter = letter
                            if testletter != letter or len(letter) == 0:
                                letter_ok = False
                                i -= 1
                                break
                        i += 1

                    if len(row.get_child().label.get_text()) == len(current_word) - 1 + i:
                        self.autocomplete.autocomplete_submit()
                        return True
                    else:
                        text = row.get_child().label.get_text()[:len(current_word) - 1 + i]
                        self.autocomplete.autocomplete_insert(text, select_dot=False)
                        return True

    def show(self):
        pass

    def hide(self):
        self.autocomplete.change_state('inactive')

    def focus_show(self):
        pass

    def focus_hide(self):
        self.autocomplete.change_state('active_invisible')



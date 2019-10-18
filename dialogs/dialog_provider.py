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


import dialogs.about.about as about_dialog
import dialogs.close_confirmation.close_confirmation as close_confirmation_dialog
import dialogs.preferences.preferences as preferences_dialog


class DialogProvider(object):

    def __init__(self, main_window, workspace, settings):
        self.main_window = main_window
        self.workspace = workspace
        self.settings = settings

        self.dialogs = dict()
        self.dialogs['about'] = about_dialog.AboutDialog(self.main_window, self.settings)
        self.dialogs['close_confirmation'] = close_confirmation_dialog.CloseConfirmationDialog(self.main_window, self.workspace)
        self.dialogs['preferences'] = preferences_dialog.PreferencesDialog(self.main_window, self.settings)

    def get_dialog(self, dialog_type):
        return self.dialogs[dialog_type]



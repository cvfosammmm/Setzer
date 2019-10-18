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
import dialogs.build_save.build_save as build_save_dialog
import dialogs.building_failed.building_failed as building_failed_dialog
import dialogs.close_confirmation.close_confirmation as close_confirmation_dialog
import dialogs.document_wizard.document_wizard as document_wizard
import dialogs.interpreter_missing.interpreter_missing as interpreter_missing_dialog
import dialogs.preferences.preferences as preferences_dialog
import dialogs.open_document.open_document as open_document_dialog
import dialogs.replace_confirmation.replace_confirmation as replace_confirmation_dialog
import dialogs.save_document.save_document as save_document_dialog


class DialogProvider(object):

    def __init__(self, main_window, workspace, settings):
        self.main_window = main_window
        self.workspace = workspace
        self.settings = settings

        self.dialogs = dict()
        self.dialogs['about'] = about_dialog.AboutDialog(self.main_window, self.settings)
        self.dialogs['building_failed'] = building_failed_dialog.BuildingFailedDialog(self.main_window)
        self.dialogs['build_save'] = build_save_dialog.BuildSaveDialog(self.main_window)
        self.dialogs['close_confirmation'] = close_confirmation_dialog.CloseConfirmationDialog(self.main_window, self.workspace, self)
        self.dialogs['document_wizard'] = document_wizard.DocumentWizard(self.main_window, self.workspace, self.settings)
        self.dialogs['interpreter_missing'] = interpreter_missing_dialog.InterpreterMissingDialog(self.main_window)
        self.dialogs['preferences'] = preferences_dialog.PreferencesDialog(self.main_window, self.settings)
        self.dialogs['open_document'] = open_document_dialog.OpenDocumentDialog(self.main_window, self.workspace)
        self.dialogs['replace_confirmation'] = replace_confirmation_dialog.ReplaceConfirmationDialog(self.main_window)
        self.dialogs['save_document'] = save_document_dialog.SaveDocumentDialog(self.main_window, self.workspace)

    def get_dialog(self, dialog_type):
        return self.dialogs[dialog_type]



#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017-present Robert Griesel
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

import setzer.dialogs.about.about as about_dialog
import setzer.dialogs.add_remove_packages.add_remove_packages as add_remove_packages
import setzer.dialogs.build_save.build_save as build_save_dialog
import setzer.dialogs.building_failed.building_failed as building_failed_dialog
import setzer.dialogs.close_confirmation.close_confirmation as close_confirmation_dialog
import setzer.dialogs.document_changed_on_disk.document_changed_on_disk as document_changed_on_disk_dialog
import setzer.dialogs.document_deleted_on_disk.document_deleted_on_disk as document_deleted_on_disk_dialog
import setzer.dialogs.interpreter_missing.interpreter_missing as interpreter_missing_dialog
import setzer.dialogs.open_document.open_document as open_document_dialog
import setzer.dialogs.open_session.open_session as open_session_dialog
import setzer.dialogs.preferences.preferences as preferences_dialog
import setzer.dialogs.replace_confirmation.replace_confirmation as replace_confirmation_dialog
import setzer.dialogs.save_document.save_document as save_document_dialog
import setzer.dialogs.save_session.save_session as save_session_dialog


class DialogLocator(object):

    dialogs = dict()

    def init_dialogs(main_window, workspace):
        dialogs = dict()
        dialogs['about'] = about_dialog.AboutDialog(main_window)
        dialogs['add_remove_packages'] = add_remove_packages.AddRemovePackagesDialog(main_window)
        dialogs['build_save'] = build_save_dialog.BuildSaveDialog(main_window)
        dialogs['document_changed_on_disk'] = document_changed_on_disk_dialog.DocumentChangedOnDiskDialog(main_window)
        dialogs['document_deleted_on_disk'] = document_deleted_on_disk_dialog.DocumentDeletedOnDiskDialog(main_window)
        dialogs['open_document'] = open_document_dialog.OpenDocumentDialog(main_window, workspace)
        dialogs['open_session'] = open_session_dialog.OpenSessionDialog(main_window, workspace)
        dialogs['preferences'] = preferences_dialog.PreferencesDialog(main_window)
        dialogs['replace_confirmation'] = replace_confirmation_dialog.ReplaceConfirmationDialog(main_window)
        dialogs['save_document'] = save_document_dialog.SaveDocumentDialog(main_window, workspace)
        dialogs['save_session'] = save_session_dialog.SaveSessionDialog(main_window, workspace)
        dialogs['close_confirmation'] = close_confirmation_dialog.CloseConfirmationDialog(main_window, workspace, dialogs['save_document'])
        dialogs['building_failed'] = building_failed_dialog.BuildingFailedDialog(main_window, dialogs['preferences'])
        dialogs['interpreter_missing'] = interpreter_missing_dialog.InterpreterMissingDialog(main_window, dialogs['preferences'])
        DialogLocator.dialogs = dialogs
    
    def get_dialog(dialog_type):
        return DialogLocator.dialogs[dialog_type]



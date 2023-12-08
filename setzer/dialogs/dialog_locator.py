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

from setzer.dialogs.about.about import AboutDialog
from setzer.dialogs.add_remove_packages.add_remove_packages import AddRemovePackagesDialog
from setzer.dialogs.build_save.build_save import BuildSaveDialog
from setzer.dialogs.building_failed.building_failed import BuildingFailedDialog
from setzer.dialogs.close_confirmation.close_confirmation import CloseConfirmationDialog
from setzer.dialogs.document_changed_on_disk.document_changed_on_disk import DocumentChangedOnDiskDialog
from setzer.dialogs.document_deleted_on_disk.document_deleted_on_disk import DocumentDeletedOnDiskDialog
from setzer.dialogs.document_wizard.document_wizard import DocumentWizard
from setzer.dialogs.include_bibtex_file.include_bibtex_file import IncludeBibTeXFile
from setzer.dialogs.include_latex_file.include_latex_file import IncludeLaTeXFile
from setzer.dialogs.interpreter_missing.interpreter_missing import InterpreterMissingDialog
from setzer.dialogs.keyboard_shortcuts.keyboard_shortcuts import KeyboardShortcutsDialog
from setzer.dialogs.open_document.open_document import OpenDocumentDialog
from setzer.dialogs.open_session.open_session import OpenSessionDialog
from setzer.dialogs.preferences.preferences import PreferencesDialog
from setzer.dialogs.replace_confirmation.replace_confirmation import ReplaceConfirmationDialog
from setzer.dialogs.save_document.save_document import SaveDocumentDialog
from setzer.dialogs.save_session.save_session import SaveSessionDialog


class DialogLocator():

    dialogs = dict()

    def init_dialogs(main_window, workspace):
        dialogs = dict()
        dialogs['about'] = AboutDialog(main_window)
        dialogs['add_remove_packages'] = AddRemovePackagesDialog(main_window)
        dialogs['build_save'] = BuildSaveDialog(main_window, workspace)
        dialogs['document_changed_on_disk'] = DocumentChangedOnDiskDialog(main_window)
        dialogs['document_deleted_on_disk'] = DocumentDeletedOnDiskDialog(main_window)
        dialogs['document_wizard'] = DocumentWizard(main_window)
        dialogs['include_bibtex_file'] = IncludeBibTeXFile(main_window)
        dialogs['include_latex_file'] = IncludeLaTeXFile(main_window)
        dialogs['keyboard_shortcuts'] = KeyboardShortcutsDialog(main_window)
        dialogs['open_document'] = OpenDocumentDialog(main_window, workspace)
        dialogs['open_session'] = OpenSessionDialog(main_window, workspace)
        dialogs['preferences'] = PreferencesDialog(main_window)
        dialogs['replace_confirmation'] = ReplaceConfirmationDialog(main_window)
        dialogs['save_document'] = SaveDocumentDialog(main_window, workspace)
        dialogs['save_session'] = SaveSessionDialog(main_window, workspace)
        dialogs['close_confirmation'] = CloseConfirmationDialog(main_window, workspace)
        dialogs['building_failed'] = BuildingFailedDialog(main_window, dialogs['preferences'])
        dialogs['interpreter_missing'] = InterpreterMissingDialog(main_window, dialogs['preferences'])
        DialogLocator.dialogs = dialogs
    
    def get_dialog(dialog_type):
        return DialogLocator.dialogs[dialog_type]



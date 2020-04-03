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

import setzer.dialogs.about.about as about_dialog
import setzer.dialogs.add_remove_packages.add_remove_packages as add_remove_packages_dialog
import setzer.dialogs.bibtex_wizard.bibtex_wizard as bibtex_wizard
import setzer.dialogs.build_save.build_save as build_save_dialog
import setzer.dialogs.building_failed.building_failed as building_failed_dialog
import setzer.dialogs.close_confirmation.close_confirmation as close_confirmation_dialog
import setzer.dialogs.document_wizard.document_wizard as document_wizard
import setzer.dialogs.document_changed_on_disk.document_changed_on_disk as document_changed_on_disk_dialog
import setzer.dialogs.include_bibtex_file.include_bibtex_file as include_bibtex_file_dialog
import setzer.dialogs.include_latex_file.include_latex_file as include_latex_file_dialog
import setzer.dialogs.interpreter_missing.interpreter_missing as interpreter_missing_dialog
import setzer.dialogs.preferences.preferences as preferences_dialog
import setzer.dialogs.open_document.open_document as open_document_dialog
import setzer.dialogs.replace_confirmation.replace_confirmation as replace_confirmation_dialog
import setzer.dialogs.save_document.save_document as save_document_dialog
import setzer.dialogs.keyboard_shortcuts.keyboard_shortcuts as keyboard_shortcuts_dialog
import setzer.dialogs.spellchecking_language.spellchecking_language as spellchecking_language_dialog
import setzer.dialogs.spellchecking.spellchecking as spellchecking_dialog


class DialogLocator(object):

    dialogs = dict()

    def init_dialogs(main_window, workspace):
        dialogs = dict()
        dialogs['about'] = about_dialog.AboutDialog(main_window)
        dialogs['add_remove_packages'] = add_remove_packages_dialog.AddRemovePackagesDialog(main_window, workspace)
        dialogs['bibtex_wizard'] = bibtex_wizard.BibTeXWizard(main_window, workspace)
        dialogs['building_failed'] = building_failed_dialog.BuildingFailedDialog(main_window)
        dialogs['build_save'] = build_save_dialog.BuildSaveDialog(main_window)
        dialogs['document_wizard'] = document_wizard.DocumentWizard(main_window, workspace)
        dialogs['document_changed_on_disk'] = document_changed_on_disk_dialog.DocumentChangedOnDiskDialog(main_window)
        dialogs['include_bibtex_file'] = include_bibtex_file_dialog.IncludeBibTeXFile(main_window)
        dialogs['include_latex_file'] = include_latex_file_dialog.IncludeLaTeXFile(main_window)
        dialogs['interpreter_missing'] = interpreter_missing_dialog.InterpreterMissingDialog(main_window)
        dialogs['preferences'] = preferences_dialog.PreferencesDialog(main_window)
        dialogs['open_document'] = open_document_dialog.OpenDocumentDialog(main_window)
        dialogs['replace_confirmation'] = replace_confirmation_dialog.ReplaceConfirmationDialog(main_window)
        dialogs['save_document'] = save_document_dialog.SaveDocumentDialog(main_window, workspace)
        dialogs['keyboard_shortcuts'] = keyboard_shortcuts_dialog.KeyboardShortcutsDialog(main_window)
        dialogs['spellchecking'] = spellchecking_dialog.SpellcheckingDialog(main_window, workspace)
        dialogs['spellchecking_language'] = spellchecking_language_dialog.SpellcheckingLanguageDialog(main_window, workspace)
        dialogs['close_confirmation'] = close_confirmation_dialog.CloseConfirmationDialog(main_window, workspace, dialogs['save_document'])
        DialogLocator.dialogs = dialogs
    
    def get_dialog(dialog_type):
        return DialogLocator.dialogs[dialog_type]



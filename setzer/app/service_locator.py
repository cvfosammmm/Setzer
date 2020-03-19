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

import re
import os.path

import setzer.app.settings as settingscontroller
import setzer.helpers.popover_menu_builder as popover_menu_builder

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


class ServiceLocator(object):

    dialogs = dict()
    settings = None
    popover_menu_builder = None
    build_log_doc_regex = re.compile('( *\((.*\.tex))')
    build_log_item_regex = re.compile('((?:Overfull \\\\hbox|Underfull \\\\hbox|No file .*\.|File .* does not exist\.|! I can\'t find file\.|! File .* not found\.|(?:LaTeX|pdfTeX|LuaTeX|Package|Class) .*Warning.*:|LaTeX Font Warning:|! Undefined control sequence\.|! Missing (?:.*) inserted.|! Package .* Error:|! (?:LaTeX|LuaTeX) Error:|No file .*\.bbl.).*\\n)')
    build_log_badbox_line_number_regex = re.compile('lines ([0-9]+)--([0-9]+)')
    build_log_other_line_number_regex = re.compile('(l.| input line \n| input line )([0-9]+)( |.)')
    bibtex_log_item_regex = re.compile('Warning--(.*)\n--line ([0-9]+) of file (.*)|I couldn\'t open style file (.*).bst\n---line ([0-9]+) of file (.*)')
    symbols_regex = re.compile('\\\\(label|include|input|bibliography)\{((?:\s|\w|\:|,)*)\}|\\\\(usepackage)(?:\[.*\]){0,1}\{((?:\s|\w|\:|,)*)\}')
    blocks_regex = re.compile('\n.*\\\\(begin|end)\{((?:\w)*(?:\*){0,1})\}|\n.*\\\\(part|chapter|section|subsection|subsubsection)(?:\*){0,1}\{')
    def init_dialogs(main_window, workspace):
        settings = ServiceLocator.get_settings()
        ServiceLocator.dialogs['about'] = about_dialog.AboutDialog(main_window)
        ServiceLocator.dialogs['add_remove_packages'] = add_remove_packages_dialog.AddRemovePackagesDialog(main_window, workspace)
        ServiceLocator.dialogs['bibtex_wizard'] = bibtex_wizard.BibTeXWizard(main_window, workspace, settings)
        ServiceLocator.dialogs['building_failed'] = building_failed_dialog.BuildingFailedDialog(main_window)
        ServiceLocator.dialogs['build_save'] = build_save_dialog.BuildSaveDialog(main_window)
        ServiceLocator.dialogs['document_wizard'] = document_wizard.DocumentWizard(main_window, workspace, settings)
        ServiceLocator.dialogs['document_changed_on_disk'] = document_changed_on_disk_dialog.DocumentChangedOnDiskDialog(main_window)
        ServiceLocator.dialogs['include_bibtex_file'] = include_bibtex_file_dialog.IncludeBibTeXFile(main_window, settings)
        ServiceLocator.dialogs['include_latex_file'] = include_latex_file_dialog.IncludeLaTeXFile(main_window)
        ServiceLocator.dialogs['interpreter_missing'] = interpreter_missing_dialog.InterpreterMissingDialog(main_window)
        ServiceLocator.dialogs['preferences'] = preferences_dialog.PreferencesDialog(main_window, settings)
        ServiceLocator.dialogs['open_document'] = open_document_dialog.OpenDocumentDialog(main_window)
        ServiceLocator.dialogs['replace_confirmation'] = replace_confirmation_dialog.ReplaceConfirmationDialog(main_window)
        ServiceLocator.dialogs['save_document'] = save_document_dialog.SaveDocumentDialog(main_window, workspace)
        ServiceLocator.dialogs['keyboard_shortcuts'] = keyboard_shortcuts_dialog.KeyboardShortcutsDialog(main_window)
        ServiceLocator.dialogs['spellchecking'] = spellchecking_dialog.SpellcheckingDialog(main_window, workspace)
        ServiceLocator.dialogs['spellchecking_language'] = spellchecking_language_dialog.SpellcheckingLanguageDialog(main_window, workspace)
        ServiceLocator.dialogs['close_confirmation'] = close_confirmation_dialog.CloseConfirmationDialog(main_window, workspace, ServiceLocator.dialogs['save_document'])
    
    def get_dialog(dialog_type):
        return ServiceLocator.dialogs[dialog_type]

    def init_main_window(main_window):
        ServiceLocator.main_window = main_window

    def get_main_window():
        return ServiceLocator.main_window
    
    def get_build_log_doc_regex():
        return ServiceLocator.build_log_doc_regex
    
    def get_build_log_item_regex():
        return ServiceLocator.build_log_item_regex
    
    def get_build_log_badbox_line_number_regex():
        return ServiceLocator.build_log_badbox_line_number_regex
    
    def get_build_log_other_line_number_regex():
        return ServiceLocator.build_log_other_line_number_regex

    def get_bibtex_log_item_regex():
        return ServiceLocator.bibtex_log_item_regex

    def get_symbols_regex():
        return ServiceLocator.symbols_regex

    def get_blocks_regex():
        return ServiceLocator.blocks_regex

    def get_settings():
        if ServiceLocator.settings == None:
            ServiceLocator.settings = settingscontroller.Settings()
        return ServiceLocator.settings

    def get_popover_menu_builder():
        if ServiceLocator.popover_menu_builder == None:
            ServiceLocator.popover_menu_builder = popover_menu_builder.PopoverMenuBuilder()
        return ServiceLocator.popover_menu_builder

    def get_dot_folder():
        return os.path.expanduser('~') + '/.setzer'



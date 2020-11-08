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

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gspell', '1')
from gi.repository import Gspell
from gi.repository import GLib, Gio

from setzer.app.service_locator import ServiceLocator
from setzer.dialogs.dialog_locator import DialogLocator


class Actions(object):

    def __init__(self, workspace):
        self.workspace = workspace
        main_window = ServiceLocator.get_main_window()
        settings = ServiceLocator.get_settings()

        self.new_latex_document_action = Gio.SimpleAction.new('new-latex-document', None)
        self.new_bibtex_document_action = Gio.SimpleAction.new('new-bibtex-document', None)
        self.build_action = Gio.SimpleAction.new('build', None)
        self.save_and_build_action = Gio.SimpleAction.new('save-and-build', None)
        self.save_action = Gio.SimpleAction.new('save', None)
        self.save_as_action = Gio.SimpleAction.new('save-as', None)
        self.save_all_action = Gio.SimpleAction.new('save-all', None)
        self.save_session_action = Gio.SimpleAction.new('save-session', None)
        self.restore_session_action = Gio.SimpleAction.new('restore-session', GLib.VariantType('as'))
        self.find_action = Gio.SimpleAction.new('find', None)
        self.find_next_action = Gio.SimpleAction.new('find-next', None)
        self.find_prev_action = Gio.SimpleAction.new('find-prev', None)
        self.find_replace_action = Gio.SimpleAction.new('find-replace', None)
        self.close_all_action = Gio.SimpleAction.new('close-all-documents', None)
        self.close_document_action = Gio.SimpleAction.new('close-active-document', None)
        self.insert_before_after_action = Gio.SimpleAction.new('insert-before-after', GLib.VariantType('as'))
        self.insert_symbol_action = Gio.SimpleAction.new('insert-symbol', GLib.VariantType('as'))
        self.insert_before_document_end_action = Gio.SimpleAction.new('insert-before-document-end', GLib.VariantType('as'))
        self.document_wizard_action = Gio.SimpleAction.new('show-document-wizard', None)
        self.create_new_bibtex_entry_action = Gio.SimpleAction.new('create-new-bibtex-entry', None)
        self.show_previous_bibtex_entries_action = Gio.SimpleAction.new('show-previous-bibtex-entries', None)
        self.search_online_for_bibtex_entries_action = Gio.SimpleAction.new('search-online-for-bibtex-entries', None)
        self.include_bibtex_file_action = Gio.SimpleAction.new('include-bibtex-file', None)
        self.include_latex_file_action = Gio.SimpleAction.new('include-latex-file', None)
        self.add_remove_packages_dialog_action = Gio.SimpleAction.new('add-remove-packages-dialog', None)
        self.add_packages_action = Gio.SimpleAction.new('add-packages', GLib.VariantType('as'))
        self.comment_uncomment_action = Gio.SimpleAction.new('comment-uncomment', None)
        self.shortcuts_window_action = Gio.SimpleAction.new('show-shortcuts-window', None)
        self.show_preferences_action = Gio.SimpleAction.new('show-preferences-dialog', None)
        self.show_about_action = Gio.SimpleAction.new('show-about-dialog', None)
        self.quit_action = Gio.SimpleAction.new('quit', None)
        self.close_build_log_action = Gio.SimpleAction.new('close-build-log', None)
        sc_default = GLib.Variant.new_boolean(settings.get_value('preferences', 'inline_spellchecking'))
        self.toggle_spellchecking_action = Gio.SimpleAction.new_stateful('toggle-spellchecking', None, sc_default)
        self.set_spellchecking_language_action = Gio.SimpleAction.new('set-spellchecking-language', None)
        self.spellchecking_action = Gio.SimpleAction.new('spellchecking', None)
        dm_default = GLib.Variant.new_boolean(settings.get_value('preferences', 'prefer_dark_mode'))
        self.toggle_dark_mode_action = Gio.SimpleAction.new_stateful('toggle-dark-mode', None, dm_default)
        settings.gtksettings.get_default().set_property('gtk-application-prefer-dark-theme', dm_default)
        ip_default = GLib.Variant.new_boolean(settings.get_value('preferences', 'invert_pdf'))
        self.toggle_invert_pdf_action = Gio.SimpleAction.new_stateful('toggle-invert-pdf', None, ip_default)
        self.zoom_out_action = Gio.SimpleAction.new('zoom-out', None)
        self.zoom_in_action = Gio.SimpleAction.new('zoom-in', None)
        self.reset_zoom_action = Gio.SimpleAction.new('reset-zoom', None)

        main_window.add_action(self.new_latex_document_action)
        main_window.add_action(self.new_bibtex_document_action)
        main_window.add_action(self.build_action)
        main_window.add_action(self.save_and_build_action)
        main_window.add_action(self.save_action)
        main_window.add_action(self.save_as_action)
        main_window.add_action(self.save_all_action)
        main_window.add_action(self.save_session_action)
        main_window.add_action(self.restore_session_action)
        main_window.add_action(self.find_action)
        main_window.add_action(self.find_next_action)
        main_window.add_action(self.find_prev_action)
        main_window.add_action(self.find_replace_action)
        main_window.add_action(self.close_all_action)
        main_window.add_action(self.close_document_action)
        main_window.add_action(self.insert_before_after_action)
        main_window.add_action(self.insert_symbol_action)
        main_window.add_action(self.insert_before_document_end_action)
        main_window.add_action(self.document_wizard_action)
        main_window.add_action(self.create_new_bibtex_entry_action)
        main_window.add_action(self.show_previous_bibtex_entries_action)
        main_window.add_action(self.search_online_for_bibtex_entries_action)
        main_window.add_action(self.include_bibtex_file_action)
        main_window.add_action(self.include_latex_file_action)
        main_window.add_action(self.add_remove_packages_dialog_action)
        main_window.add_action(self.add_packages_action)
        main_window.add_action(self.comment_uncomment_action)
        main_window.add_action(self.shortcuts_window_action)
        main_window.add_action(self.show_preferences_action)
        main_window.add_action(self.show_about_action)
        main_window.add_action(self.quit_action)
        main_window.add_action(self.close_build_log_action)
        main_window.add_action(self.toggle_spellchecking_action)
        main_window.add_action(self.set_spellchecking_language_action)
        main_window.add_action(self.spellchecking_action)
        main_window.add_action(self.toggle_dark_mode_action)
        main_window.add_action(self.toggle_invert_pdf_action)
        main_window.add_action(self.zoom_out_action)
        main_window.add_action(self.zoom_in_action)
        main_window.add_action(self.reset_zoom_action)

        self.new_latex_document_action.connect('activate', self.on_new_latex_document_action_activated)
        self.new_bibtex_document_action.connect('activate', self.on_new_bibtex_document_action_activated)
        self.build_action.connect('activate', self.on_build_action_activated)
        self.save_and_build_action.connect('activate', self.on_save_and_build_action_activated)
        self.save_action.connect('activate', self.on_save_button_click)
        self.save_as_action.connect('activate', self.on_save_as_clicked)
        self.save_all_action.connect('activate', self.on_save_all_clicked)
        self.save_session_action.connect('activate', self.on_save_session_clicked)
        self.restore_session_action.connect('activate', self.on_restore_session_clicked)
        self.find_action.connect('activate', self.on_menu_find_clicked)
        self.find_next_action.connect('activate', self.find_next)
        self.find_prev_action.connect('activate', self.find_prev)
        self.find_replace_action.connect('activate', self.on_menu_find_replace_clicked)
        self.close_all_action.connect('activate', self.on_close_all_clicked)
        self.close_document_action.connect('activate', self.on_close_document_clicked)
        self.insert_before_after_action.connect('activate', self.insert_before_after)
        self.insert_symbol_action.connect('activate', self.insert_symbol)
        self.insert_before_document_end_action.connect('activate', self.insert_before_document_end)
        self.document_wizard_action.connect('activate', self.start_wizard)
        self.include_bibtex_file_action.connect('activate', self.start_include_bibtex_file_dialog)
        self.include_latex_file_action.connect('activate', self.start_include_latex_file_dialog)
        self.add_remove_packages_dialog_action.connect('activate', self.start_add_remove_packages_dialog)
        self.add_packages_action.connect('activate', self.add_packages)
        self.comment_uncomment_action.connect('activate', self.comment_uncomment)
        self.create_new_bibtex_entry_action.connect('activate', self.start_create_new_bibtex_entry_dialog)
        self.show_previous_bibtex_entries_action.connect('activate', self.start_show_previous_bibtex_entries_dialog)
        self.search_online_for_bibtex_entries_action.connect('activate', self.start_search_online_for_bibtex_entries_dialog)
        self.shortcuts_window_action.connect('activate', self.show_shortcuts_window)
        self.show_preferences_action.connect('activate', self.show_preferences_dialog)
        self.show_about_action.connect('activate', self.show_about_dialog)
        self.close_build_log_action.connect('activate', self.close_build_log)
        self.toggle_spellchecking_action.connect('activate', self.on_spellchecking_toggle_toggled)
        self.set_spellchecking_language_action.connect('activate', self.start_spellchecking_language_dialog)
        self.spellchecking_action.connect('activate', self.start_spellchecking_dialog)
        self.toggle_dark_mode_action.connect('activate', self.on_dark_mode_toggle_toggled)
        self.toggle_invert_pdf_action.connect('activate', self.on_invert_pdf_toggle_toggled)
        self.zoom_out_action.connect('activate', self.on_zoom_out)
        self.zoom_in_action.connect('activate', self.on_zoom_in)
        self.reset_zoom_action.connect('activate', self.on_reset_zoom)

        self.font_manager = ServiceLocator.get_font_manager()
        self.update_zoom_actions()
        self.workspace.register_observer(self)
        self.font_manager.register_observer(self)

    '''
    *** decorators
    '''

    def _assert_has_active_document(original_function):
        def new_function(self, *args, **kwargs):
            if self.workspace.get_active_document() != None:
                return original_function(self, *args, **kwargs)
        return new_function    

    '''
    *** notification handlers, get called by observed workspace
    '''

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'document_removed':
            if self.workspace.active_document == None:
                self.activate_blank_slate_mode()
                self.update_save_actions(None)

        if change_code == 'new_inactive_document':
            document = parameter
            document.unregister_observer(self)

        if change_code == 'new_active_document':
            document = parameter
            self.activate_document_mode()
            self.update_save_actions(document)
            document.register_observer(self)

        if change_code == 'modified_changed':
            document = notifying_object
            self.update_save_actions(document)

        if change_code == 'font_string_changed':
            self.update_zoom_actions()

    def activate_blank_slate_mode(self):
        self.save_all_action.set_enabled(False)
        self.spellchecking_action.set_enabled(False)
        self.add_remove_packages_dialog_action.set_enabled(False)
        self.set_document_actions_active(False)

    def activate_document_mode(self):
        self.set_document_actions_active(True)
        self.enable_spellchecking_action()
        active_document = self.workspace.get_active_document()
        if active_document.is_latex_document():
            self.add_remove_packages_dialog_action.set_enabled(True)

    def enable_spellchecking_action(self):
        default_language = Gspell.Language.get_default()
        if default_language != None:
            self.spellchecking_action.set_enabled(True)

    def update_zoom_actions(self):
        normal_font_size = self.font_manager.get_normal_font_size_in_points()
        current_font_size = self.font_manager.get_font_size_in_points()
        self.zoom_out_action.set_enabled(current_font_size / 1.1 > 6)
        self.zoom_in_action.set_enabled(current_font_size * 1.1 < 24)
        self.reset_zoom_action.set_enabled(current_font_size != normal_font_size)

    def update_save_actions(self, document):
        if document == None:
            self.save_action.set_enabled(False)
            self.save_all_action.set_enabled(False)
        else:
            if document.get_modified():
                self.save_action.set_enabled(True)
            elif document.get_filename() == None:
                self.save_action.set_enabled(True)
            else:
                self.save_action.set_enabled(False)

        if self.workspace.get_unsaved_documents() != None:
            self.save_all_action.set_enabled(True)
        else:
            self.save_all_action.set_enabled(False)

    def set_document_actions_active(self, value):
        self.save_as_action.set_enabled(value)
        self.find_action.set_enabled(value)
        self.find_next_action.set_enabled(value)
        self.find_prev_action.set_enabled(value)
        self.find_replace_action.set_enabled(value)
        self.close_document_action.set_enabled(value)
        self.close_all_action.set_enabled(value)
        self.save_session_action.set_enabled(value)
        self.insert_before_after_action.set_enabled(value)
        self.insert_symbol_action.set_enabled(value)
        self.insert_before_document_end_action.set_enabled(value)
        self.include_bibtex_file_action.set_enabled(value)
        self.include_latex_file_action.set_enabled(value)
        self.add_packages_action.set_enabled(value)
        self.comment_uncomment_action.set_enabled(value)
        self.document_wizard_action.set_enabled(value)

    def on_new_latex_document_action_activated(self, action=None, parameter=None):
        self.workspace.create_latex_document(activate=True)

    def on_new_bibtex_document_action_activated(self, action=None, parameter=None):
        self.workspace.create_bibtex_document(activate=True)

    @_assert_has_active_document
    def on_save_and_build_action_activated(self, action=None, parameter=None):
        self.on_save_button_click()
        self.on_build_action_activated()

    @_assert_has_active_document
    def on_build_action_activated(self, action=None, parameter=None):
        if self.workspace.master_document != None:
            document = self.workspace.master_document
        else:
            document = self.workspace.active_document
        try:
            document.build_widget.build_document_request()
        except AttributeError:
            pass

    @_assert_has_active_document
    def on_save_button_click(self, action=None, parameter=None):
        active_document = self.workspace.get_active_document()
        if active_document.filename == None:
            self.on_save_as_clicked()
        else:
            active_document.save_to_disk()

    @_assert_has_active_document
    def on_save_as_clicked(self, action=None, parameter=None):
        document = self.workspace.get_active_document()
        DialogLocator.get_dialog('save_document').run(document)
        
    @_assert_has_active_document
    def on_save_all_clicked(self, action=None, parameter=None):
        active_document = self.workspace.get_active_document()
        return_to_active_document = False
        documents = self.workspace.get_unsaved_documents()
        if documents != None: 
            for document in documents:
                if document.get_filename() == None:
                    self.workspace.set_active_document(document)
                    return_to_active_document = True
                    DialogLocator.get_dialog('save_document').run(document)
                else:
                    document.save_to_disk()
            if return_to_active_document == True:
                self.workspace.set_active_document(document)

    @_assert_has_active_document
    def on_save_session_clicked(self, action=None, parameter=None):
        DialogLocator.get_dialog('save_session').run()

    def on_restore_session_clicked(self, action=None, parameter=None):
        parameter = parameter.unpack()[0]
        if parameter == '':
            filename = DialogLocator.get_dialog('open_session').run()
            if filename == None: return
        else:
            filename = parameter

        active_document = self.workspace.get_active_document()
        documents = self.workspace.get_all_documents()
        unsaved_documents = self.workspace.get_unsaved_documents()
        dialog = DialogLocator.get_dialog('close_confirmation')
        not_save_to_close_documents = dialog.run(unsaved_documents)['not_save_to_close_documents']

        if len(not_save_to_close_documents) == 0:
            if documents != None:
                for document in documents:
                    self.workspace.remove_document(document)
            self.workspace.load_documents_from_session_file(filename)

    @_assert_has_active_document
    def on_menu_find_clicked(self, action=None, parameter=None):
        active_document = self.workspace.get_active_document()
        if active_document.view.shortcuts_bar_bottom.button_find.get_active():
            GLib.idle_add(active_document.search.search_entry_grab_focus, None)
        else:
            active_document.view.shortcuts_bar_bottom.button_find.set_active(True)

    @_assert_has_active_document
    def find_next(self, action=None, parameter=None):
        active_document = self.workspace.get_active_document()
        if active_document.view.source_view.has_focus() or active_document.view.search_bar.entry.has_focus() or active_document.view.search_bar.replace_entry.has_focus():
            active_document.view.search_bar.entry.emit('next-match')

    @_assert_has_active_document
    def find_prev(self, action=None, parameter=None):
        active_document = self.workspace.get_active_document()
        if active_document.view.source_view.has_focus() or active_document.view.search_bar.entry.has_focus() or active_document.view.search_bar.replace_entry.has_focus():
            active_document.view.search_bar.entry.emit('previous-match')

    @_assert_has_active_document
    def on_menu_find_replace_clicked(self, action=None, parameter=None):
        active_document = self.workspace.get_active_document()
        if active_document.view.shortcuts_bar_bottom.button_find_and_replace.get_active():
            GLib.idle_add(active_document.search.search_entry_grab_focus, None)
        else:
            active_document.view.shortcuts_bar_bottom.button_find_and_replace.set_active(True)

    @_assert_has_active_document
    def on_close_all_clicked(self, action=None, parameter=None):
        active_document = self.workspace.get_active_document()
        documents = self.workspace.get_all_documents()
        unsaved_documents = self.workspace.get_unsaved_documents()
        dialog = DialogLocator.get_dialog('close_confirmation')
        not_save_to_close_documents = dialog.run(unsaved_documents)['not_save_to_close_documents']

        for document in documents:
            if document not in not_save_to_close_documents:
                self.workspace.remove_document(document)

    def on_close_document_clicked(self, action=None, parameter=None):
        document = self.workspace.get_active_document()
        if document.get_modified():
            dialog = DialogLocator.get_dialog('close_confirmation')
            not_save_to_close = dialog.run([document])['not_save_to_close_documents']
            if document not in not_save_to_close:
                self.workspace.remove_document(document)
        else:
            self.workspace.remove_document(document)

    @_assert_has_active_document
    def insert_before_after(self, action, parameter):
        active_document = self.workspace.get_active_document().insert_before_after(parameter[0], parameter[1])

    @_assert_has_active_document
    def insert_symbol(self, action, parameter):
        self.workspace.get_active_document().insert_text_at_cursor(parameter[0])

    @_assert_has_active_document
    def insert_before_document_end(self, action, parameter):
        document = self.workspace.get_active_document()
        document.insert_before_document_end(parameter[0])

    @_assert_has_active_document
    def start_wizard(self, action, parameter=None):
        document = self.workspace.get_active_document()
        DialogLocator.get_dialog('document_wizard').run(document)

    @_assert_has_active_document
    def start_include_bibtex_file_dialog(self, action, parameter=None):
        document = self.workspace.get_active_document()
        DialogLocator.get_dialog('include_bibtex_file').run(document)

    @_assert_has_active_document
    def start_include_latex_file_dialog(self, action, parameter=None):
        document = self.workspace.get_active_document()
        DialogLocator.get_dialog('include_latex_file').run(document)

    @_assert_has_active_document
    def start_add_remove_packages_dialog(self, action, parameter=None):
        document = self.workspace.get_active_document()
        DialogLocator.get_dialog('add_remove_packages').run(document)

    @_assert_has_active_document
    def add_packages(self, action, parameter):
        if parameter == None: return
        document = self.workspace.get_active_document()
        if document.is_latex_document():
            document.add_packages(parameter)

    @_assert_has_active_document
    def comment_uncomment(self, action, parameter=None):
        document = self.workspace.get_active_document()
        document.comment_uncomment()

    @_assert_has_active_document
    def start_create_new_bibtex_entry_dialog(self, action, parameter=None):
        document = self.workspace.get_active_document()
        DialogLocator.get_dialog('bibtex_wizard').run('new_entry', document)

    @_assert_has_active_document
    def start_show_previous_bibtex_entries_dialog(self, action, parameter=None):
        document = self.workspace.get_active_document()
        DialogLocator.get_dialog('bibtex_wizard').run('previous_entries', document)

    @_assert_has_active_document
    def start_search_online_for_bibtex_entries_dialog(self, action, parameter=None):
        document = self.workspace.get_active_document()
        DialogLocator.get_dialog('bibtex_wizard').run('search_online', document)

    def show_shortcuts_window(self, action, parameter=''):
        DialogLocator.get_dialog('keyboard_shortcuts').run()

    def show_preferences_dialog(self, action=None, parameter=''):
        DialogLocator.get_dialog('preferences').run()

    def show_about_dialog(self, action, parameter=''):
        DialogLocator.get_dialog('about').run()

    def close_build_log(self, action, parameter=''):
        self.workspace.set_show_build_log(False)
        
    def on_spellchecking_toggle_toggled(self, action, parameter=None):
        new_state = not action.get_state().get_boolean()
        action.set_state(GLib.Variant.new_boolean(new_state))
        self.workspace.set_inline_spellchecking(new_state)

    def start_spellchecking_language_dialog(self, action, parameter=None):
        DialogLocator.get_dialog('spellchecking_language').run()

    def start_spellchecking_dialog(self, action, parameter=None):
        DialogLocator.get_dialog('spellchecking').run()

    def on_dark_mode_toggle_toggled(self, action, parameter=None):
        new_state = not action.get_state().get_boolean()
        action.set_state(GLib.Variant.new_boolean(new_state))
        self.workspace.set_dark_mode(new_state)

    def on_invert_pdf_toggle_toggled(self, action, parameter=None):
        new_state = not action.get_state().get_boolean()
        action.set_state(GLib.Variant.new_boolean(new_state))
        self.workspace.set_invert_pdf(new_state)

    def on_zoom_out(self, widget=None, event=None):
        ServiceLocator.get_font_manager().zoom_out()

    def on_zoom_in(self, widget=None, event=None):
        ServiceLocator.get_font_manager().zoom_in()

    def on_reset_zoom(self, widget=None, event=None):
        ServiceLocator.get_font_manager().reset_zoom()



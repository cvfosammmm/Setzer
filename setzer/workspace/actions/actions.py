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

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GLib, Gio, Gtk, Gdk, Pango

from setzer.app.service_locator import ServiceLocator
from setzer.dialogs.dialog_locator import DialogLocator
from setzer.app.font_manager import FontManager
from setzer.popovers.popover_manager import PopoverManager


class Actions(object):

    def __init__(self, workspace):
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()
        self.settings = ServiceLocator.get_settings()

        self.actions = dict()
        self.add_action('new-latex-document', self.new_latex_document)
        self.add_action('new-bibtex-document', self.new_bibtex_document)
        self.add_action('open-document-dialog', self.open_document_dialog)
        self.add_action('build', self.build)
        self.add_action('save-and-build', self.save_and_build)
        self.add_action('show-build-log', self.show_build_log)
        self.add_action('close-build-log', self.close_build_log)
        self.add_action('save', self.save)
        self.add_action('save-as', self.save_as)
        self.add_action('save-all', self.save_all)
        self.add_action('save-session', self.save_session)
        self.add_action('close-all-documents', self.close_all)
        self.add_action('close-active-document', self.close_active_document)

        self.add_action('show-document-wizard', self.start_wizard, None)
        self.add_action('insert-before-after', self.insert_before_after, GLib.VariantType('as'))
        self.add_action('insert-symbol', self.insert_symbol, GLib.VariantType('as'))
        self.add_action('insert-after-packages', self.insert_after_packages, GLib.VariantType('as'))
        self.add_action('insert-before-document-end', self.insert_before_document_end, GLib.VariantType('as'))
        self.add_action('add-packages', self.add_packages, GLib.VariantType('as'))
        self.add_action('include-bibtex-file', self.start_include_bibtex_file_dialog, None)
        self.add_action('include-latex-file', self.start_include_latex_file_dialog, None)
        self.add_action('add-remove-packages-dialog', self.start_add_remove_packages_dialog, None)
        self.add_action('toggle-comment', self.toggle_comment)
        self.add_action('forward-sync', self.forward_sync)

        self.add_action('start-search', self.start_search)
        self.add_action('start-search-and-replace', self.start_search_and_replace)
        self.add_action('find-next', self.find_next)
        self.add_action('find-previous', self.find_previous)
        self.add_action('stop-search', self.stop_search)

        self.add_action('cut', self.cut)
        self.add_action('copy', self.copy)
        self.add_action('paste', self.paste)
        self.add_action('delete-selection', self.delete_selection)
        self.add_action('select-all', self.select_all)
        self.add_action('undo', self.undo)
        self.add_action('redo', self.redo)

        self.add_action('zoom-in', self.zoom_in)
        self.add_action('zoom-out', self.zoom_out)
        self.add_action('reset-zoom', self.reset_zoom)

        self.add_action('show-preferences-dialog', self.show_preferences_dialog)
        self.add_action('show-shortcuts-dialog', self.show_shortcuts_dialog)
        self.add_action('show-about-dialog', self.show_about_dialog)
        self.add_action('show-context-menu', self.show_context_menu)

        self.actions['quit'] = Gio.SimpleAction.new('quit', None)
        self.main_window.add_action(self.actions['quit'])

        self.workspace.connect('new_document', self.on_new_document)
        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('new_inactive_document', self.on_new_inactive_document)
        self.workspace.connect('new_active_document', self.on_new_active_document)

        self.update_actions()

    def add_action(self, name, callback, parameter=None):
        self.actions[name] = Gio.SimpleAction.new(name, parameter)
        self.main_window.add_action(self.actions[name])
        self.actions[name].connect('activate', callback)

    def on_new_document(self, workspace, document):
        if document.is_latex_document():
            document.build_system.connect('can_sync_changed', self.on_can_sync_changed)
        self.update_actions()

    def on_document_removed(self, workspace, document):
        if document.is_latex_document():
            document.build_system.disconnect('can_sync_changed', self.on_can_sync_changed)
        self.update_actions()

    def on_new_inactive_document(self, workspace, document):
        document.disconnect('modified_changed', self.on_modified_changed)
        document.source_buffer.disconnect_by_func(self.on_undo_changed)
        document.source_buffer.disconnect_by_func(self.on_has_selection_changed)
        document.view.scrolled_window.get_vadjustment().disconnect_by_func(self.on_adjustment_changed)

    def on_new_active_document(self, workspace, document):
        self.update_actions()
        document.connect('modified_changed', self.on_modified_changed)
        document.source_buffer.connect('notify::can-undo', self.on_undo_changed)
        document.source_buffer.connect('notify::has-selection', self.on_has_selection_changed)
        document.view.scrolled_window.get_vadjustment().connect('changed', self.on_adjustment_changed)

    def on_modified_changed(self, document):
        self.update_actions()

    def on_can_sync_changed(self, document, can_sync):
        self.update_actions()

    def on_undo_changed(self, buffer, can_undo):
        self.update_actions()

    def on_redo_changed(self, buffer, can_redo):
        self.update_actions()

    def on_has_selection_changed(self, buffer, has_selection):
        self.update_actions()

    def on_adjustment_changed(self, adjustment):
        self.update_actions()

    def update_actions(self):
        document = self.workspace.get_active_document()
        document_active = document != None
        document_active_is_latex = document_active and document.is_latex_document()
        enable_save = document_active and (document.source_buffer.get_modified() or document.get_filename() == None)
        has_selection = document_active and document.source_buffer.get_has_selection()
        if self.workspace.root_document != None: sync_document = self.workspace.root_document
        else: sync_document = document
        can_sync = sync_document != None and sync_document.is_latex_document() and sync_document.build_system.can_sync
        can_build = (self.workspace.get_root_or_active_latex_document() != None)
        can_reset_zoom = (round(FontManager.zoom_level * 100) != 100)
        can_zoom_in = (FontManager.get_font_desc().get_size() * 1.1 <= 24 * Pango.SCALE)
        can_zoom_out = (FontManager.get_font_desc().get_size() / 1.1 >= 6 * Pango.SCALE)

        self.actions['close-active-document'].set_enabled(document_active)
        self.actions['close-all-documents'].set_enabled(document_active)
        self.actions['save-session'].set_enabled(document_active)
        self.actions['save'].set_enabled(enable_save)
        self.actions['save-as'].set_enabled(document_active)
        self.actions['save-all'].set_enabled(len(self.workspace.get_unsaved_documents()) > 0)
        self.actions['add-remove-packages-dialog'].set_enabled(document_active_is_latex)
        self.actions['redo'].set_enabled(document_active and document.source_buffer.get_can_redo())
        self.actions['undo'].set_enabled(document_active and document.source_buffer.get_can_undo())
        self.actions['cut'].set_enabled(has_selection)
        self.actions['copy'].set_enabled(has_selection)
        self.actions['delete-selection'].set_enabled(has_selection)
        self.actions['start-search'].set_enabled(document_active)
        self.actions['start-search-and-replace'].set_enabled(document_active)
        self.actions['find-next'].set_enabled(document_active)
        self.actions['find-previous'].set_enabled(document_active)
        self.actions['insert-before-after'].set_enabled(document_active_is_latex)
        self.actions['insert-symbol'].set_enabled(document_active_is_latex)
        self.actions['insert-before-document-end'].set_enabled(document_active_is_latex)
        self.actions['insert-after-packages'].set_enabled(document_active_is_latex)
        self.actions['add-packages'].set_enabled(document_active_is_latex)
        self.actions['show-document-wizard'].set_enabled(document_active_is_latex)
        self.actions['include-bibtex-file'].set_enabled(document_active_is_latex)
        self.actions['include-latex-file'].set_enabled(document_active_is_latex)
        self.actions['add-remove-packages-dialog'].set_enabled(document_active_is_latex)
        self.actions['toggle-comment'].set_enabled(document_active_is_latex)
        self.actions['forward-sync'].set_enabled(can_sync)
        self.actions['build'].set_enabled(can_build)
        self.actions['save-and-build'].set_enabled(can_build)
        self.actions['show-build-log'].set_enabled(document_active_is_latex)
        self.actions['close-build-log'].set_enabled(document_active_is_latex)
        self.actions['reset-zoom'].set_enabled(can_reset_zoom)
        self.actions['zoom-in'].set_enabled(can_zoom_in)
        self.actions['zoom-out'].set_enabled(can_zoom_out)

    def new_latex_document(self, action=None, parameter=None):
        document = self.workspace.create_latex_document()
        self.workspace.add_document(document)
        self.workspace.set_active_document(document)

    def new_bibtex_document(self, action=None, parameter=None):
        document = self.workspace.create_bibtex_document()
        self.workspace.add_document(document)
        self.workspace.set_active_document(document)

    def open_document_dialog(self, action=None, parameter=None):
        DialogLocator.get_dialog('open_document').run()

    def save_and_build(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        document = self.workspace.get_root_or_active_latex_document()
        active_document = ServiceLocator.get_workspace().get_active_document()
        if document == None or active_document == None: return

        if document.filename == None:
            DialogLocator.get_dialog('build_save').run(document)
        else:
            self.save()
            document.build_system.build_and_forward_sync(active_document)

    def build(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        document = self.workspace.get_root_or_active_latex_document()
        active_document = ServiceLocator.get_workspace().get_active_document()
        if document == None or active_document == None: return

        if document.filename == None:
            DialogLocator.get_dialog('build_save').run(document)
        else:
            document.build_system.build_and_forward_sync(active_document)

    def forward_sync(self, action=None, parameter=''):
        active_document = self.workspace.get_active_document()
        if active_document == None: return

        if self.workspace.root_document != None: sync_document = self.workspace.root_document
        else: sync_document = active_document
        if not sync_document.is_latex_document(): return
        if not sync_document.build_system.can_sync: return

        sync_document.build_system.forward_sync(active_document)

    def show_build_log(self, action=None, parameter=''):
        self.workspace.set_show_build_log(True)

    def close_build_log(self, action=None, parameter=''):
        self.workspace.set_show_build_log(False)

    def save(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        active_document = self.workspace.get_active_document()
        if active_document.filename == None:
            self.save_as()
        else:
            active_document.save_to_disk()

    def save_as(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        document = self.workspace.get_active_document()
        DialogLocator.get_dialog('save_document').run(document)

    def save_all(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        active_document = self.workspace.get_active_document()
        return_to_active_document = False
        documents = self.workspace.get_unsaved_documents()
        if len(documents) > 0: 
            for document in documents:
                if document.get_filename() == None:
                    self.workspace.set_active_document(document)
                    return_to_active_document = True
                    DialogLocator.get_dialog('save_document').run(document)
                else:
                    document.save_to_disk()
            if return_to_active_document == True:
                self.workspace.set_active_document(document)

    def save_session(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        DialogLocator.get_dialog('save_session').run()

    def close_all(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        unsaved_documents = self.workspace.get_unsaved_documents()
        if len(unsaved_documents) > 0:
            self.workspace.set_active_document(unsaved_documents[0])
            dialog = DialogLocator.get_dialog('close_confirmation')
            dialog.run({'unsaved_document': unsaved_documents[0]}, self.close_all_callback)
        else:
            documents = self.workspace.get_all_documents()
            for document in documents:
                self.workspace.remove_document(document)

    def close_all_callback(self, parameters):
        document = parameters['unsaved_document']

        if parameters['response'] == 0:
            self.workspace.remove_document(document)
            self.close_all()
        elif parameters['response'] == 2:
            if document.get_filename() == None:
                DialogLocator.get_dialog('save_document').run(document, self.close_all)
            else:
                document.save_to_disk()
                self.close_all()

    def close_active_document(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        document = self.workspace.get_active_document()
        if document.source_buffer.get_modified():
            dialog = DialogLocator.get_dialog('close_confirmation')
            dialog.run({'unsaved_document': document}, self.close_document_callback)
        else:
            self.workspace.remove_document(document)

    def close_document_callback(self, parameters):
        if parameters['response'] == 0:
            self.workspace.remove_document(parameters['unsaved_document'])
        elif parameters['response'] == 2:
            document = parameters['unsaved_document']
            if document.get_filename() == None:
                DialogLocator.get_dialog('save_document').run(document)
            else:
                document.save_to_disk()
                self.workspace.remove_document(parameters['unsaved_document'])

    def start_wizard(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        document = self.workspace.get_active_document()
        DialogLocator.get_dialog('document_wizard').run(document)

    def insert_before_after(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return
        if parameter == None: return

        document = self.workspace.get_active_document()
        document.source_buffer.begin_user_action()

        before, after = parameter[0], parameter[1]
        bounds = document.source_buffer.get_selection_bounds()
        if len(bounds) > 1:
            text = before + document.source_buffer.get_text(*bounds, False) + after
            text = document.replace_tabs_with_spaces_if_set(text)

            document.source_buffer.delete_selection(False, False)

            insert_iter = document.source_buffer.get_iter_at_mark(document.source_buffer.get_insert())
            text = document.indent_text_with_whitespace_at_iter(text, insert_iter)

            document.source_buffer.insert_at_cursor(text)
        else:
            text = before + '•' + after
            text = document.replace_tabs_with_spaces_if_set(text)
            insert_iter = document.source_buffer.get_iter_at_mark(document.source_buffer.get_insert())
            text = document.indent_text_with_whitespace_at_iter(text, insert_iter)
            document.source_buffer.insert_at_cursor(text)

        document.select_first_dot_around_cursor(offset_before=len(text), offset_after=0)
        document.source_buffer.end_user_action()

    def insert_symbol(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return
        if parameter == None: return

        document = self.workspace.get_active_document()
        document.source_buffer.begin_user_action()

        text = parameter[0]
        text = document.replace_tabs_with_spaces_if_set(text)
        insert_iter = document.source_buffer.get_iter_at_mark(document.source_buffer.get_insert())
        text = document.indent_text_with_whitespace_at_iter(text, insert_iter)

        bounds = document.source_buffer.get_selection_bounds()

        if len(bounds) > 1:
            document.source_buffer.delete_selection(False, False)

        document.source_buffer.insert_at_cursor(text)
        document.select_first_dot_around_cursor(offset_before=len(text), offset_after=0)
        document.source_buffer.end_user_action()

    def insert_after_packages(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        document = self.workspace.get_active_document()
        document.insert_text_after_packages_if_possible(parameter[0])
        document.select_first_dot_around_cursor(offset_before=len(parameter[0]), offset_after=0)
        document.scroll_cursor_onscreen()

    def insert_before_document_end(self, action, parameter):
        if self.workspace.get_active_document() == None: return

        document = self.workspace.get_active_document()
        document.insert_before_document_end(parameter[0])
        document.scroll_cursor_onscreen()

    def add_packages(self, action, parameter):
        if self.workspace.get_active_document() == None: return
        if parameter == None: return

        document = self.workspace.get_active_document()
        if document.is_latex_document():
            document.add_packages(parameter)
            document.scroll_cursor_onscreen()

    def start_include_bibtex_file_dialog(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        document = self.workspace.get_active_document()
        DialogLocator.get_dialog('include_bibtex_file').run(document)

    def start_include_latex_file_dialog(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        document = self.workspace.get_active_document()
        DialogLocator.get_dialog('include_latex_file').run(document)

    def start_add_remove_packages_dialog(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        document = self.workspace.get_active_document()
        DialogLocator.get_dialog('add_remove_packages').run(document)

    def toggle_comment(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        document = self.workspace.get_active_document()
        document.source_buffer.begin_user_action()

        bounds = document.source_buffer.get_selection_bounds()

        if len(bounds) > 1:
            end = (bounds[1].get_line() + 1) if (bounds[1].get_line_index() > 0) else bounds[1].get_line()
            line_numbers = list(range(bounds[0].get_line(), end))
        else:
            line_numbers = [document.source_buffer.get_iter_at_mark(document.source_buffer.get_insert()).get_line()]

        do_comment = False
        for line_number in line_numbers:
            line = document.get_line(line_number)
            if not line.lstrip().startswith('%'):
                do_comment = True

        if do_comment:
            for line_number in line_numbers:
                found, line_iter = document.source_buffer.get_iter_at_line(line_number)
                document.source_buffer.insert(line_iter, '%')
        else:
            for line_number in line_numbers:
                line = document.get_line(line_number)
                offset = len(line) - len(line.lstrip())
                found, start = document.source_buffer.get_iter_at_line(line_number)
                start.forward_chars(offset)
                end = start.copy()
                end.forward_char()
                document.source_buffer.delete(start, end)

        document.source_buffer.end_user_action()

    def start_search(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        self.workspace.get_active_document().search.set_mode_search()

    def start_search_and_replace(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        self.workspace.get_active_document().search.set_mode_replace()

    def find_next(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        self.workspace.get_active_document().search.on_search_next_match()

    def find_previous(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        self.workspace.get_active_document().search.on_search_previous_match()

    def stop_search(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        self.workspace.get_active_document().search.hide_search_bar()

    def cut(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        self.copy()
        self.workspace.get_active_document().delete_selection()

    def copy(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        document = self.workspace.get_active_document()
        text = document.get_selected_text()
        if text != None:
            clipboard = document.source_view.get_clipboard()
            clipboard.set(text)

    def paste(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        self.workspace.get_active_document().source_view.emit('paste-clipboard')

    def delete_selection(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        self.workspace.get_active_document().delete_selection()

    def select_all(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        self.workspace.get_active_document().select_all()

    def undo(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        self.workspace.get_active_document().source_buffer.undo()

    def redo(self, action=None, parameter=None):
        if self.workspace.get_active_document() == None: return

        self.workspace.get_active_document().source_buffer.redo()

    def zoom_in(self, action=None, parameter=''):
        font_desc = Pango.FontDescription.from_string(FontManager.font_string)
        font_desc.set_size(min(font_desc.get_size() * 1.1, 24 * Pango.SCALE))
        FontManager.font_string = font_desc.to_string()
        FontManager.propagate_font_setting()
        self.workspace.context_menu.popover_more.view.reset_zoom_button.set_label("{:.0%}".format(FontManager.zoom_level))
        self.workspace.context_menu.reset_zoom_button_pointer.set_label("{:.0%}".format(FontManager.zoom_level))

    def zoom_out(self, action=None, parameter=''):
        font_desc = Pango.FontDescription.from_string(FontManager.font_string)
        font_desc.set_size(max(font_desc.get_size() / 1.1, 6 * Pango.SCALE))
        FontManager.font_string = font_desc.to_string()
        FontManager.propagate_font_setting()
        self.workspace.context_menu.popover_more.view.reset_zoom_button.set_label("{:.0%}".format(FontManager.zoom_level))
        self.workspace.context_menu.reset_zoom_button_pointer.set_label("{:.0%}".format(FontManager.zoom_level))

    def reset_zoom(self, action=None, parameter=''):
        if self.settings.get_value('preferences', 'use_system_font'):
            FontManager.font_string = FontManager.default_font_string
        else:
            FontManager.font_string = self.settings.get_value('preferences', 'font_string')
        FontManager.propagate_font_setting()
        self.workspace.context_menu.popover_more.view.reset_zoom_button.set_label("{:.0%}".format(FontManager.zoom_level))
        self.workspace.context_menu.reset_zoom_button_pointer.set_label("{:.0%}".format(FontManager.zoom_level))

    def show_preferences_dialog(self, action=None, parameter=''):
        DialogLocator.get_dialog('preferences').run()

    def show_shortcuts_dialog(self, action=None, parameter=''):
        DialogLocator.get_dialog('keyboard_shortcuts').run()

    def show_about_dialog(self, action=None, parameter=''):
        DialogLocator.get_dialog('about').run()

    def show_context_menu(self, action=None, parameter=''):
        PopoverManager.popup_at_button('context_menu')



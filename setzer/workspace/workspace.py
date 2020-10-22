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

import os.path
import time
import pickle

from setzer.document.document import Document, LaTeXDocument, BibTeXDocument
from setzer.helpers.observable import Observable
import setzer.workspace.workspace_presenter as workspace_presenter
import setzer.workspace.workspace_controller as workspace_controller
import setzer.workspace.preview_panel.preview_panel_presenter as preview_panel_presenter
import setzer.workspace.help_panel.help_panel as help_panel
import setzer.workspace.sidebar.sidebar as sidebar
import setzer.workspace.build_log.build_log as build_log
import setzer.workspace.headerbar.headerbar_presenter as headerbar_presenter
import setzer.workspace.document_chooser.document_chooser_presenter as document_chooser_presenter
import setzer.workspace.keyboard_shortcuts.shortcuts as shortcuts
import setzer.workspace.document_switcher.document_switcher as document_switcher
from setzer.app.service_locator import ServiceLocator


class Workspace(Observable):
    ''' A workspace contains a user's open documents. '''

    def __init__(self):
        Observable.__init__(self)
        self.pathname = ServiceLocator.get_config_folder()

        self.open_documents = list()
        self.open_latex_documents = list()
        self.master_document = None
        self.recently_opened_documents = dict()
        self.untitled_documents_no = 0

        self.active_document = None

        self.recently_opened_session_files = dict()
        self.session_file_opened = None

        self.settings = ServiceLocator.get_settings()
        self.inline_spellchecking = self.settings.get_value('preferences', 'inline_spellchecking')
        self.spellchecking_language_code = self.settings.get_value('preferences', 'spellchecking_language_code')
        self.dark_mode = self.settings.get_value('preferences', 'prefer_dark_mode')
        self.invert_pdf = self.settings.get_value('preferences', 'invert_pdf')

        self.sidebar = sidebar.Sidebar()
        self.show_sidebar = self.settings.get_value('window_state', 'show_sidebar')
        self.sidebar_position = self.settings.get_value('window_state', 'sidebar_paned_position')
        self.show_help = self.settings.get_value('window_state', 'show_help')
        self.show_preview = self.settings.get_value('window_state', 'show_preview')
        self.preview_position = self.settings.get_value('window_state', 'preview_paned_position')
        self.build_log = build_log.BuildLog(self)
        self.show_build_log = self.settings.get_value('window_state', 'show_build_log')
        self.build_log_position = self.settings.get_value('window_state', 'build_log_paned_position')
        self.shortcuts = shortcuts.Shortcuts(self)

    def init_workspace_controller(self):
        self.presenter = workspace_presenter.WorkspacePresenter(self)
        self.headerbar = headerbar_presenter.HeaderbarPresenter(self)
        self.document_chooser = document_chooser_presenter.DocumentChooserPresenter(self)
        self.preview_panel = preview_panel_presenter.PreviewPanelPresenter(self)
        self.help_panel = help_panel.HelpPanel(self)
        self.document_switcher = document_switcher.DocumentSwitcher(self)
        self.controller = workspace_controller.WorkspaceController(self)

    def open_document_by_filename(self, filename):
        if filename != None:
            document_candidate = self.get_document_by_filename(filename)
            if document_candidate != None:
                self.set_active_document(document_candidate)
            else:
                self.create_document_from_filename(filename, activate=True)

    def switch_to_earliest_open_document(self):
        document = self.get_earliest_active_document()
        if document != None:
            self.set_active_document(document)
    
    def add_document(self, document):
        if document in self.open_documents: return False
        if document.get_filename() == None:
            document.set_displayname(_('Untitled Document {number}').format(number=str(self.untitled_documents_no + 1)))
            self.untitled_documents_no += 1
        self.open_documents.append(document)
        if document.is_latex_document():
            self.open_latex_documents.append(document)
            document.set_invert_pdf(self.invert_pdf)
        document.spellchecker.set_enabled(self.inline_spellchecking)
        document.spellchecker.set_language(self.spellchecking_language_code)
        document.state_manager.load_document_state()
        self.add_change_code('new_document', document)
        self.update_recently_opened_document(document.get_filename(), notify=True)

    def remove_document(self, document):
        if document == self.master_document:
            self.unset_master_document()
        document.state_manager.save_document_state()
        self.open_documents.remove(document)
        if document.is_latex_document():
            self.open_latex_documents.remove(document)
        if self.active_document == document:
            candidate = self.get_last_active_document()
            if candidate == None:
                self.set_active_document(None)
            else:
                self.set_active_document(candidate)
        self.add_change_code('document_removed', document)

    def create_latex_document(self, activate=False):
        document = LaTeXDocument()
        self.add_document(document)

        if activate:
            self.set_active_document(document)

    def create_bibtex_document(self, activate=False):
        document = BibTeXDocument()
        self.add_document(document)

        if activate:
            self.set_active_document(document)

    def create_document_from_filename(self, filename, activate=False):
        if filename[-4:] == '.tex':
            document = LaTeXDocument()
        elif filename[-4:] == '.bib':
            document = BibTeXDocument()
        else:
            return None
        document.set_filename(os.path.realpath(filename))
        response = document.populate_from_filename()
        if response != False:
            self.add_document(document)
            if activate:
                self.set_active_document(document)
            if document.is_latex_document():
                document.preview.set_pdf_filename_from_tex_filename(filename)
            return document
        else:
            return None

    def get_document_by_filename(self, filename):
        for document in self.open_documents:
            if filename == document.get_filename():
                return document
        return None

    def get_active_document(self):
        return self.active_document
        
    def set_active_document(self, document):
        if self.active_document != None:
            self.add_change_code('new_inactive_document', self.active_document)
            previously_active_document = self.active_document
            self.active_document = document
            self.set_has_visible_build_system(previously_active_document)
        else:
            self.active_document = document

        if self.active_document != None:
            self.active_document.set_last_activated(time.time())
            self.set_has_visible_build_system(self.active_document)
            self.add_change_code('new_active_document', document)
            if self.active_document.is_latex_document():
                self.shortcuts.activate_latex_documents_mode()
            elif self.active_document.is_bibtex_document():
                self.shortcuts.activate_bibtex_documents_mode()
            self.set_build_log()

    def set_build_log(self):
        if self.get_active_document() != None:
            if self.master_document != None:
                document = self.master_document
            else:
                document = self.active_document
            if document.is_latex_document():
                self.build_log.set_document(document)

    def get_last_active_document(self):
        for document in sorted(self.open_documents, key=lambda val: -val.last_activated):
            return document
        return None

    def get_earliest_active_document(self):
        for document in sorted(self.open_documents, key=lambda val: val.last_activated):
            return document
        return None

    def get_open_documents_filenames(self):
        pathnames = list()
        for document in self.open_documents:
            pathnames.append(document.get_filename())
        return pathnames

    def update_recently_opened_document(self, filename, date=None, notify=True):
        if not isinstance(filename, str) or not os.path.isfile(filename):
            self.remove_recently_opened_document(filename)
        else:
            if date == None: date = time.time()
            if len(self.recently_opened_documents) >= 1000: 
                del(self.recently_opened_documents[sorted(self.recently_opened_documents.values(), key=lambda val: val['date'])[0]['filename']])
            self.recently_opened_documents[filename] = {'filename': filename, 'date': date}
        if notify:
            self.add_change_code('update_recently_opened_documents', self.recently_opened_documents)

    def remove_recently_opened_document(self, filename):
        try:
            del(self.recently_opened_documents[filename])
        except KeyError:
            pass

    def update_recently_opened_session_file(self, filename, date=None, notify=True):
        if not isinstance(filename, str) or not os.path.isfile(filename):
            self.remove_recently_opened_session_file(filename)
        else:
            if date == None: date = time.time()
            self.recently_opened_session_files[filename] = {'filename': filename, 'date': date}
            if len(self.recently_opened_session_files) > 5: 
                del(self.recently_opened_session_files[sorted(self.recently_opened_session_files.values(), key=lambda val: val['date'])[0]['filename']])
        if notify:
            self.add_change_code('update_recently_opened_session_files', self.recently_opened_session_files)

    def remove_recently_opened_session_file(self, filename):
        try:
            del(self.recently_opened_session_files[filename])
        except KeyError:
            pass

    def populate_from_disk(self):
        try: filehandle = open(os.path.join(self.pathname, 'workspace.pickle'), 'rb')
        except IOError: pass
        else:
            try: data = pickle.load(filehandle)
            except EOFError:
                return
            else:
                try:
                    master_document_filename = data['master_document_filename']
                except KeyError:
                    master_document_filename = None
                for item in sorted(data['open_documents'].values(), key=lambda val: val['last_activated']):
                    document = self.create_document_from_filename(item['filename'])
                    if item['filename'] == master_document_filename and document != None:
                        self.set_one_document_master(document)
                for item in data['recently_opened_documents'].values():
                    self.update_recently_opened_document(item['filename'], item['date'], notify=False)
                try:
                    self.help_panel.search_results_blank = data['recently_help_searches']
                except KeyError:
                    pass
                try:
                    recently_opened_session_files = data['recently_opened_session_files'].values()
                except KeyError:
                    recently_opened_session_files = []
                for item in recently_opened_session_files:
                    self.update_recently_opened_session_file(item['filename'], item['date'], notify=False)
        self.add_change_code('update_recently_opened_documents', self.recently_opened_documents)
        self.add_change_code('update_recently_opened_session_files', self.recently_opened_session_files)

    def load_documents_from_session_file(self, filename):
        try: filehandle = open(filename, 'rb')
        except IOError: pass
        else:
            try: data = pickle.load(filehandle)
            except EOFError:
                return
            else:
                try:
                    master_document_filename = data['master_document_filename']
                except KeyError:
                    master_document_filename = None
                for item in sorted(data['open_documents'].values(), key=lambda val: val['last_activated']):
                    document = self.create_document_from_filename(item['filename'])
                    if item['filename'] == master_document_filename and document != None:
                        self.set_one_document_master(document)        
            if len(self.open_documents) > 0:
                self.set_active_document(self.open_documents[-1])
            self.session_file_opened = filename
            self.update_recently_opened_session_file(filename, notify=True)

    def save_to_disk(self):
        try: filehandle = open(os.path.join(self.pathname, 'workspace.pickle'), 'wb')
        except IOError: pass
        else:
            open_documents = dict()
            for document in self.open_documents:
                filename = document.get_filename()
                if filename != None:
                    open_documents[filename] = {
                        'filename': filename,
                        'last_activated': document.get_last_activated()
                    }
            data = {
                'open_documents': open_documents,
                'recently_opened_documents': self.recently_opened_documents,
                'recently_opened_session_files': self.recently_opened_session_files,
                'recently_help_searches': self.help_panel.search_results_blank
            }
            if self.master_document != None:
                data['master_document_filename'] = self.master_document.get_filename()
            pickle.dump(data, filehandle)
            
    def save_session(self, session_filename):
        try: filehandle = open(session_filename, 'wb')
        except IOError: pass
        else:
            open_documents = dict()
            for document in self.open_documents:
                filename = document.get_filename()
                if filename != None:
                    open_documents[filename] = {
                        'filename': filename,
                        'last_activated': document.get_last_activated()
                    }
            data = {'open_documents': open_documents}
            if self.master_document != None:
                data['master_document_filename'] = self.master_document.get_filename()
            pickle.dump(data, filehandle)
            self.session_file_opened = session_filename
            self.update_recently_opened_session_file(session_filename, notify=True)

    def get_unsaved_documents(self):
        unsaved_documents = list()
        for document in self.open_documents:
            if document.get_modified():
                unsaved_documents.append(document)

        return unsaved_documents if len(unsaved_documents) >= 1 else None
        
    def get_all_documents(self):
        return self.open_documents.copy() if len(self.open_documents) >= 1 else None

    def set_one_document_master(self, master_document):
        if master_document.is_latex_document():
            self.master_document = master_document
            for document in self.open_latex_documents:
                if document == master_document:
                    document.set_is_master(True)
                else:
                    document.set_is_master(False)
                self.set_has_visible_build_system(document)
            self.add_change_code('master_state_change', 'one_document')
            self.set_build_log()

    def unset_master_document(self):
        for document in self.open_latex_documents:
            document.set_is_master(False)
            self.set_has_visible_build_system(document)
        self.master_document = None
        self.set_has_visible_build_system(self.active_document)
        self.add_change_code('master_state_change', 'no_master_document')
        self.set_build_log()

    def get_master_document(self):
        return self.master_document

    def set_has_visible_build_system(self, document):
        if document != None and document.is_latex_document():
            if document == self.master_document:
                document.set_has_visible_build_system(True)
            elif document == self.active_document and self.master_document == None:
                document.set_has_visible_build_system(True)
            else:
                document.set_has_visible_build_system(False)

    def set_show_sidebar(self, show_sidebar):
        if show_sidebar != self.show_sidebar:
            self.show_sidebar = show_sidebar
            self.add_change_code('set_show_sidebar', show_sidebar)

    def set_sidebar_position(self, sidebar_position):
        self.sidebar_position = sidebar_position

    def set_show_preview_or_help(self, show_preview, show_help):
        if show_preview != self.show_preview or show_help != self.show_help:
            self.show_preview = show_preview
            self.show_help = show_help
            self.add_change_code('set_show_preview_or_help')

    def set_preview_position(self, preview_position):
        self.preview_position = preview_position

    def set_show_build_log(self, show_build_log):
        if show_build_log != self.show_build_log:
            self.show_build_log = show_build_log
            self.add_change_code('show_build_log_state_change', show_build_log)

    def set_build_log_position(self, build_log_position):
        self.build_log_position = build_log_position

    def get_show_build_log(self):
        if self.show_build_log != None:
            return self.show_build_log
        else:
            return False

    def set_dark_mode(self, value):
        if self.dark_mode != value:
            self.dark_mode = value
            self.settings.set_value('preferences', 'prefer_dark_mode', self.dark_mode)
            self.add_change_code('set_dark_mode', value)

    def set_invert_pdf(self, value):
        if self.invert_pdf != value:
            self.invert_pdf = value
            self.settings.set_value('preferences', 'invert_pdf', self.invert_pdf)
            for document in self.open_latex_documents:
                document.set_invert_pdf(self.invert_pdf)

    def set_inline_spellchecking(self, value):
        if self.inline_spellchecking != value:
            self.inline_spellchecking = value
            self.settings.set_value('preferences', 'inline_spellchecking', self.inline_spellchecking)
            for document in self.open_documents:
                document.spellchecker.set_enabled(value)

    def set_spellchecking_language(self, language_code):
        if self.spellchecking_language_code != language_code:
            self.spellchecking_language_code = language_code
            self.settings.set_value('preferences', 'spellchecking_language_code', self.spellchecking_language_code)
            for document in self.open_documents:
                document.spellchecker.set_language(language_code)



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
import os.path
import time
import pickle

from setzer.document.document import Document
import setzer.document.build_system.build_system as build_system
import setzer.document.build_widget.build_widget as build_widget
import setzer.document.preview.preview as preview
from setzer.helpers.observable import Observable
import setzer.workspace.workspace_presenter as workspace_presenter
import setzer.workspace.workspace_controller as workspace_controller
import setzer.workspace.preview_panel.preview_panel as preview_panel
import setzer.workspace.help_panel.help_panel as help_panel
import setzer.workspace.welcome_screen.welcome_screen as welcome_screen
import setzer.workspace.headerbar.headerbar as headerbar
import setzer.workspace.sidebar.sidebar as sidebar
import setzer.workspace.shortcutsbar.shortcutsbar as shortcutsbar
import setzer.workspace.build_log.build_log as build_log
import setzer.workspace.actions.actions as actions
import setzer.workspace.context_menu.context_menu as context_menu
from setzer.app.service_locator import ServiceLocator
from setzer.settings.document_settings import DocumentSettings


class Workspace(Observable):
    ''' A workspace contains a user's open documents. '''

    def __init__(self):
        Observable.__init__(self)
        self.pathname = ServiceLocator.get_config_folder()

        self.open_documents = list()
        self.open_latex_documents = list()
        self.root_document = None
        self.recently_opened_documents = dict()

        self.active_document = None

        self.recently_opened_session_files = dict()
        self.session_file_opened = None

        self.settings = ServiceLocator.get_settings()

        self.show_build_log = self.settings.get_value('window_state', 'show_build_log')
        self.show_preview = self.settings.get_value('window_state', 'show_preview')
        self.show_help = self.settings.get_value('window_state', 'show_help')
        self.show_symbols = self.settings.get_value('window_state', 'show_symbols')
        self.show_document_structure = self.settings.get_value('window_state', 'show_document_structure')

    def init_workspace_controller(self):
        self.welcome_screen = welcome_screen.WelcomeScreen()
        self.sidebar = sidebar.Sidebar(self)
        self.actions = actions.Actions(self)
        self.shortcutsbar = shortcutsbar.Shortcutsbar(self)
        self.context_menu = context_menu.ContextMenu(self)
        self.presenter = workspace_presenter.WorkspacePresenter(self)
        self.headerbar = headerbar.Headerbar(self)
        self.preview_panel = preview_panel.PreviewPanel(self)
        self.help_panel = help_panel.HelpPanel(self)
        self.build_log = build_log.BuildLog(self)
        self.controller = workspace_controller.WorkspaceController(self)

    def open_document_by_filename(self, filename):
        if filename == None: return None

        document_candidate = self.get_document_by_filename(filename)
        if document_candidate != None:
            self.set_active_document(document_candidate)
            return document_candidate
        else:
            document = self.create_document_from_filename(filename)
            if document != None:
                self.set_active_document(document)
            return document

    def switch_to_earliest_open_document(self):
        document = self.get_earliest_active_document()
        if document != None:
            self.set_active_document(document)
    
    def add_document(self, document):
        if document in self.open_documents: return False

        if document.get_filename() == None:
            increment = ServiceLocator.get_increment('untitled_documents_added')
            document.set_displayname(_('Untitled Document {number}').format(number=str(increment)))

        self.open_documents.append(document)
        if document.is_latex_document():
            self.open_latex_documents.append(document)
        DocumentSettings.load_document_state(document)
        self.add_change_code('new_document', document)
        self.update_recently_opened_document(document.get_filename(), notify=True)

    def remove_document(self, document):
        if document == self.root_document:
            self.unset_root_document()
        DocumentSettings.save_document_state(document)
        document.controller.continue_save_date_loop = False
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

    def create_latex_document(self):
        document = Document('latex')
        document.preview = preview.Preview(document)
        document.build_system = build_system.BuildSystem(document)
        document.build_widget = build_widget.BuildWidget(document)
        return document

    def create_bibtex_document(self):
        document = Document('bibtex')
        return document

    def create_other_document(self):
        document = Document('other')
        return document

    def create_document_from_filename(self, filename):
        if filename[-4:] == '.tex':
            document = self.create_latex_document()
        elif filename[-4:] == '.bib':
            document = self.create_bibtex_document()
        elif filename[-4:] in ['.cls', '.sty']:
            document = self.create_other_document()
        else:
            return None
        document.set_filename(filename)
        response = document.populate_from_filename()
        if response != False:
            self.add_document(document)
            return document
        else:
            return None

    def get_document_by_filename(self, filename):
        for document in self.open_documents:
            if document.get_filename() != None:
                if os.path.normpath(filename) == os.path.normpath(document.get_filename()):
                    return document
        return None

    def get_active_document(self):
        return self.active_document

    def set_active_document(self, document):
        if self.active_document != None:
            self.add_change_code('new_inactive_document', self.active_document)
            previously_active_document = self.active_document
            self.active_document = document
            self.update_preview_visibility(previously_active_document)
        else:
            self.active_document = document

        if self.active_document != None:
            self.active_document.set_last_activated(time.time())
            self.update_preview_visibility(self.active_document)
            self.add_change_code('new_active_document', document)
            self.set_build_log()

    def set_build_log(self):
        document = self.get_root_or_active_latex_document()
        if document != None:
            self.build_log.set_document(document)

    def get_last_active_document(self):
        for document in sorted(self.open_documents, key=lambda val: -val.last_activated):
            return document
        return None

    def get_earliest_active_document(self):
        for document in sorted(self.open_documents, key=lambda val: val.last_activated):
            return document
        return None

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
                    root_document_filename = data['root_document_filename']
                except KeyError:
                    root_document_filename = None
                for item in sorted(data['open_documents'].values(), key=lambda val: val['last_activated']):
                    document = self.create_document_from_filename(item['filename'])
                    if document != None:
                        document.set_last_activated(item['last_activated'])
                        if item['filename'] == root_document_filename:
                            self.set_one_document_root(document)
                for item in data['recently_opened_documents'].values():
                    self.update_recently_opened_document(item['filename'], item['date'], notify=False)
                try:
                    self.help_panel.search_results_blank = data['recent_help_searches']
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
                    root_document_filename = data['root_document_filename']
                except KeyError:
                    root_document_filename = None
                for item in sorted(data['open_documents'].values(), key=lambda val: val['last_activated']):
                    document = self.create_document_from_filename(item['filename'])
                    document.set_last_activated(item['last_activated'])
                    if item['filename'] == root_document_filename and document != None:
                        self.set_one_document_root(document)        
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
                'recent_help_searches': self.help_panel.search_results_blank
            }
            if self.root_document != None:
                data['root_document_filename'] = self.root_document.get_filename()
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
            if self.root_document != None:
                data['root_document_filename'] = self.root_document.get_filename()
            pickle.dump(data, filehandle)
            self.session_file_opened = session_filename
            self.update_recently_opened_session_file(session_filename, notify=True)

    def get_unsaved_documents(self):
        unsaved_documents = list()
        for document in self.open_documents:
            if document.source_buffer.get_modified():
                unsaved_documents.append(document)
        return unsaved_documents

    def get_all_documents(self):
        return self.open_documents.copy()

    def set_one_document_root(self, root_document):
        if root_document.is_latex_document():
            self.root_document = root_document
            for document in self.open_latex_documents:
                if document == root_document:
                    document.set_root_state(True, True)
                else:
                    document.set_root_state(False, True)
                self.update_preview_visibility(document)
            self.add_change_code('root_state_change', 'one_document')
            self.set_build_log()

    def unset_root_document(self):
        for document in self.open_latex_documents:
            document.set_root_state(False, False)
            self.update_preview_visibility(document)
        self.root_document = None
        self.update_preview_visibility(self.active_document)
        self.add_change_code('root_state_change', 'no_root_document')
        self.set_build_log()

    def get_root_document(self):
        return self.root_document

    def get_active_latex_document(self):
        if self.get_active_document() == None:
            return None
        if self.active_document.is_latex_document():
            return self.active_document
        return None

    def get_root_or_active_latex_document(self):
        if self.get_active_document() == None:
            return None
        else:
            if self.root_document != None:
                return self.root_document
            elif self.active_document.is_latex_document():
                return self.active_document
            else:
                return None

    def update_preview_visibility(self, document):
        if document != None and document.is_latex_document():
            if document == self.root_document:
                document.preview.page_renderer.activate()
            elif document == self.active_document and self.root_document == None:
                document.preview.page_renderer.activate()
            else:
                document.preview.page_renderer.deactivate()

    def set_show_preview_or_help(self, show_preview, show_help):
        if show_preview != self.show_preview or show_help != self.show_help:
            self.show_preview = show_preview
            self.show_help = show_help
            self.add_change_code('set_show_preview_or_help')

    def set_show_symbols_or_document_structure(self, show_symbols, show_document_structure):
        if show_symbols != self.show_symbols or show_document_structure != self.show_document_structure:
            self.show_symbols = show_symbols
            self.show_document_structure = show_document_structure
            self.add_change_code('set_show_symbols_or_document_structure')

    def set_show_build_log(self, show_build_log):
        if show_build_log != self.show_build_log:
            self.show_build_log = show_build_log
            self.add_change_code('show_build_log_state_change', show_build_log)

    def get_show_build_log(self):
        if self.show_build_log != None:
            return self.show_build_log
        else:
            return False



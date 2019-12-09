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

from document.document import Document, LaTeXDocument, BibTeXDocument
from app.service_locator import ServiceLocator

import os.path


class HeaderbarPresenter(object):
    ''' Mediator between workspace and view. '''
    
    def __init__(self, workspace):
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()
        self.workspace.register_observer(self)
        self.activate_blank_slate_mode()

    '''
    *** notification handlers, get called by observed workspace
    '''

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'new_document': pass

        if change_code == 'document_removed':
            document = parameter
            if self.workspace.active_document == None:
                self.activate_blank_slate_mode()

        if change_code == 'new_active_document':
            document = parameter
            self.show_document_name(document)

            if document.get_modified():
                self.main_window.headerbar.save_document_button.set_sensitive(True)
            elif document.get_filename() == None:
                self.main_window.headerbar.save_document_button.set_sensitive(True)
            else:
                self.main_window.headerbar.save_document_button.set_sensitive(False)

            if isinstance(document, LaTeXDocument):
                self.activate_latex_documents_mode()
            elif isinstance(document, BibTeXDocument):
                self.activate_bibtex_documents_mode()

        if change_code == 'update_recently_opened_documents':
            items = list()
            data = parameter.values()
            for item in sorted(data, key=lambda val: -val['date']):
                items.append(os.path.split(item['filename']))
            self.main_window.headerbar.document_chooser.update_autosuggest(items)
            if len(data) > 0:
                self.main_window.headerbar.open_document_button.set_sensitive(True)
                self.main_window.headerbar.open_document_button.show_all()
                self.main_window.headerbar.open_document_blank_button.hide()
                self.main_window.headerbar.open_document_blank_button.set_sensitive(False)
            else:
                self.main_window.headerbar.open_document_button.hide()
                self.main_window.headerbar.open_document_button.set_sensitive(False)
                self.main_window.headerbar.open_document_blank_button.set_sensitive(True)
                self.main_window.headerbar.open_document_blank_button.show_all()

        if change_code == 'master_state_change':
            self.set_build_button_state()

    def activate_blank_slate_mode(self):
        self.set_build_button_state()
        self.show_document_name(None)
        self.main_window.headerbar.save_document_button.hide()
        self.main_window.headerbar.preview_toggle.hide()
        self.main_window.headerbar.preview_toggle.set_sensitive(False)
        self.main_window.headerbar.sidebar_toggle.hide()
        self.main_window.headerbar.sidebar_toggle.set_sensitive(False)

    def activate_latex_documents_mode(self):
        self.set_build_button_state()
        self.main_window.headerbar.save_document_button.show_all()
        self.main_window.headerbar.preview_toggle.show_all()
        self.main_window.headerbar.preview_toggle.set_sensitive(True)
        self.main_window.headerbar.sidebar_toggle.show_all()
        self.main_window.headerbar.sidebar_toggle.set_sensitive(True)

    def activate_bibtex_documents_mode(self):
        self.set_build_button_state()
        self.main_window.headerbar.save_document_button.show_all()
        self.main_window.headerbar.preview_toggle.hide()
        self.main_window.headerbar.preview_toggle.set_sensitive(False)
        self.main_window.headerbar.sidebar_toggle.hide()
        self.main_window.headerbar.sidebar_toggle.set_sensitive(False)

    def show_document_name(self, document):
        headerbar = self.main_window.headerbar
        if document == None:
            headerbar.center_button.hide()
            headerbar.center_button.set_sensitive(False)
            headerbar.center_label_welcome.show_all()
        else:
            doclist_item = document.view.doclist_item
            
            if headerbar.name_binding != None: headerbar.name_binding.unbind()
            headerbar.document_name_label.set_text(doclist_item.label.get_text())
            headerbar.name_binding = doclist_item.label.bind_property('label', headerbar.document_name_label, 'label', 0)
            
            if headerbar.folder_binding != None: headerbar.folder_binding.unbind()
            headerbar.folder_binding = doclist_item.flabel.bind_property('label', headerbar.document_folder_label, 'label', 0, self.folder_transform_func)

            if headerbar.mod_binding != None: headerbar.mod_binding.unbind()
            headerbar.document_mod_label.set_text(doclist_item.mlabel.get_text())
            headerbar.mod_binding = doclist_item.mlabel.bind_property('label', headerbar.document_mod_label, 'label', 0, self.modified_transform_func)

            headerbar.center_label_welcome.hide()
            headerbar.center_button.set_sensitive(True)
            headerbar.center_button.show_all()

            self.folder_transform_func(headerbar.folder_binding, doclist_item.folder)
            self.modified_transform_func(headerbar.mod_binding, doclist_item.mlabel.get_text())
            
    def modified_transform_func(self, binding, from_value, to_value=None):
        headerbar = self.main_window.headerbar

        if from_value == 'False' and headerbar.document_folder_label.get_text() != '':
            headerbar.save_document_button.set_sensitive(False)
        else:
            headerbar.save_document_button.set_sensitive(True)
        if self.workspace.get_unsaved_documents() != None:
            self.main_window.save_all_action.set_enabled(True)
        else:
            self.main_window.save_all_action.set_enabled(False)

    def folder_transform_func(self, binding, from_value, to_value=None):
        headerbar = self.main_window.headerbar
        headerbar.document_folder_label.set_text(from_value)
        if from_value == '':
            headerbar.document_folder_label.hide()
        else:
            headerbar.document_folder_label.show_all()

    def set_build_button_state(self):
        if self.workspace.master_document != None:
            document = self.workspace.master_document
        else:
            document = self.workspace.active_document

        headerbar = self.main_window.headerbar
        prev_widget = headerbar.build_wrapper.get_center_widget()
        if prev_widget != None:
            headerbar.build_wrapper.remove(prev_widget)
        if isinstance(document, LaTeXDocument):
            if document != None:
                headerbar.build_wrapper.set_center_widget(document.build_widget.view)
                if document.build_widget.view.has_result():
                    document.build_widget.view.hide_timer(4000)



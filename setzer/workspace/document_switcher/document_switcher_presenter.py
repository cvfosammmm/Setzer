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

from setzer.app.service_locator import ServiceLocator


class DocumentSwitcherPresenter(object):
    ''' Mediator between workspace and view. '''
    
    def __init__(self, document_switcher, workspace):
        self.document_switcher = document_switcher
        self.workspace = workspace
        self.button = ServiceLocator.get_main_window().headerbar.center_widget
        self.view = self.button.open_docs_popover

        self.workspace.register_observer(self)
        self.document_switcher.register_observer(self)

        self.show_document_name(None)

    '''
    *** notification handlers
    '''

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'new_document':
            document = parameter
            self.view.document_list.add(document.document_switcher_item.view)
            self.activate_mode(self.document_switcher.mode)

        if change_code == 'document_removed':
            document = parameter
            self.view.document_list.remove(document.document_switcher_item.view)
            self.activate_mode(self.document_switcher.mode)
            if self.workspace.active_document == None:
                self.show_document_name(None)

        if change_code == 'new_active_document':
            document = parameter
            self.show_document_name(document)
            self.view.document_list.invalidate_sort()

        if change_code == 'docswitcher_mode_change':
            self.activate_mode(parameter)

        if change_code == 'master_state_change':
            self.activate_mode(self.document_switcher.mode)

    def activate_mode(self, mode):
        if mode == 'normal':
            self.activate_normal_mode()
        elif mode == 'selection':
            self.activate_selection_mode()
    
    def activate_normal_mode(self):
        self.activate_set_master_document_button()
        if self.workspace.master_document != None:
            self.view.unset_master_document_button.set_sensitive(True)
        else:
            self.view.unset_master_document_button.set_sensitive(False)
        self.view.master_explaination_revealer.set_reveal_child(False)
        self.view.document_list.get_style_context().remove_class('selection-mode')
        self.view.document_list.get_style_context().add_class('normal-mode')
        for item in self.view.document_list.get_children():
            item.show()
            item.document_close_button.show()
            item.icon_box.show()
            item.radio_button_hover.hide()
        self.view.in_selection_mode = False

    def activate_selection_mode(self):
        self.view.set_master_document_button.set_sensitive(False)
        self.view.unset_master_document_button.set_sensitive(True)
        self.view.master_explaination_revealer.set_reveal_child(True)
        self.view.set_can_focus(False)
        self.view.document_list.get_style_context().remove_class('normal-mode')
        self.view.document_list.get_style_context().add_class('selection-mode')
        for item in self.view.document_list.get_children():
            item.document_close_button.hide()
            item.icon_box.hide()
            item.radio_button_hover.show()
            if not item.document.is_latex_document():
                item.hide()
        self.view.in_selection_mode = True

    def activate_set_master_document_button(self):
        if len(self.workspace.open_latex_documents) > 0:
            self.view.set_master_document_button.set_sensitive(True)
        else:
            self.view.set_master_document_button.set_sensitive(False)

    def show_document_name(self, document):
        if document == None:
            self.button.center_button.set_sensitive(False)
            self.button.set_visible_child_name('welcome')
        else:
            doclist_item = document.document_switcher_item.view
            
            if self.button.name_binding != None: self.button.name_binding.unbind()
            self.button.document_name_label.set_text(doclist_item.label.get_text())
            self.button.name_binding = doclist_item.label.bind_property('label', self.button.document_name_label, 'label', 0)
            
            if self.button.folder_binding != None: self.button.folder_binding.unbind()
            self.button.folder_binding = doclist_item.flabel.bind_property('label', self.button.document_folder_label, 'label', 0, self.folder_transform_func)

            if self.button.mod_binding != None: self.button.mod_binding.unbind()
            self.button.document_mod_label.set_text(doclist_item.mlabel.get_text())
            self.button.mod_binding = doclist_item.mlabel.bind_property('label', self.button.document_mod_label, 'label', 0)

            self.button.center_button.set_sensitive(True)
            self.button.set_visible_child_name('button')

            self.folder_transform_func(self.button.folder_binding, doclist_item.folder)

    def folder_transform_func(self, binding, from_value, to_value=None):
        self.button.document_folder_label.set_text(from_value)
        if from_value == '':
            self.button.document_folder_label.hide()
        else:
            self.button.document_folder_label.show_all()



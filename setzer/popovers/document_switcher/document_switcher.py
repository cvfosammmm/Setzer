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
from gi.repository import Gtk

from setzer.helpers.observable import Observable
import setzer.popovers.document_switcher.document_switcher_item as document_switcher_item
from setzer.popovers.document_switcher.document_switcher_viewgtk import DocumentSwitcherView
from setzer.dialogs.dialog_locator import DialogLocator


class DocumentSwitcher(Observable):

    def __init__(self, popover_manager, workspace):
        Observable.__init__(self)
        self.popover_manager = popover_manager
        self.workspace = workspace
        self.view = DocumentSwitcherView(popover_manager)

        self.items = dict()

        # can be normal or selection
        self.mode = 'normal'

        self.click_controller = Gtk.GestureClick()
        self.click_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.click_controller.set_button(2)
        self.click_controller.connect('released', self.on_doclist_row_button_release)
        self.view.document_list.add_controller(self.click_controller)

        self.view.document_list.connect('row-activated', self.on_doclist_row_activated)
        self.popover_manager.connect('popdown', self.on_popover_popdown)
        self.view.set_root_document_button.connect('clicked', self.set_selection_mode)
        self.view.unset_root_document_button.connect('clicked', self.unset_root_document)

        self.workspace.connect('new_document', self.on_new_document)
        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('root_state_change', self.on_root_state_changed)

    def set_mode(self, mode):
        self.mode = mode
        self.activate_mode(mode)

    def on_new_document(self, workspace, document):
        item = document_switcher_item.DocumentSwitcherItem(document)
        item.document_close_button.connect('clicked', self.on_close_clicked, document)
        item.set_is_root(document.get_is_root())
        self.items[document] = item
        self.view.document_list.append(item)
        self.activate_mode(self.mode)

        document.connect('filename_change', self.on_name_change)
        document.connect('displayname_change', self.on_name_change)
        document.connect('modified_changed', self.on_modified_changed)
        document.connect('is_root_changed', self.on_is_root_changed)

    def on_document_removed(self, workspace, document):
        item = self.items[document]
        del(self.items[document])
        self.view.document_list.remove(item)
        self.activate_mode(self.mode)

        document.disconnect('filename_change', self.on_name_change)
        document.disconnect('displayname_change', self.on_name_change)
        document.disconnect('modified_changed', self.on_modified_changed)
        document.disconnect('is_root_changed', self.on_is_root_changed)

    def on_new_active_document(self, workspace, document):
        self.view.document_list.invalidate_sort()

    def on_name_change(self, document, name=None):
        self.update_item(document)

    def on_is_root_changed(self, document, is_root):
        self.items[document].set_is_root(is_root)
        self.update_unset_root_button()

    def on_root_state_changed(self, workspace, state):
        self.update_unset_root_button()

    def on_modified_changed(self, document):
        self.update_item(document)

    def update_item(self, document):
        self.items[document].set_name(document.get_displayname(), document.source_buffer.get_modified())

    def on_doclist_row_activated(self, box, row, data=None):
        if self.view.in_selection_mode:
            self.set_mode('normal')
            self.workspace.set_one_document_root(row.document)
        else:
            self.popover_manager.popdown()
            self.workspace.set_active_document(row.document)

    def on_doclist_row_button_release(self, controller, n_press, x, y):
        if self.view.in_selection_mode: return False

        row = self.view.document_list.get_row_at_y(y)
        self.on_close_clicked(row.document_close_button, row.document)
        return True

    def on_popover_popdown(self, name):
        if name != 'document_switcher': return

        self.set_mode('normal')
        self.view.document_list.unselect_all()

    def set_selection_mode(self, action, parameter=None):
        self.set_mode('selection')
        return True

    def unset_root_document(self, action, parameter=None):
        self.set_mode('normal')
        self.workspace.unset_root_document()

    def on_close_clicked(self, button, document):
        if document.source_buffer.get_modified():
            active_document = self.workspace.get_active_document()
            if document != active_document:
                previously_active_document = active_document
                self.workspace.set_active_document(document)
            else:
                previously_active_document = None

            self.popover_manager.popdown()
            dialog = DialogLocator.get_dialog('close_confirmation')
            dialog.run({'unsaved_documents': [document], 'document': document, 'previously_active_document': previously_active_document}, self.on_close_document_callback)
            return True
        else:
            self.workspace.remove_document(document)

    def on_close_document_callback(self, parameters, response):
        not_save_to_close = response['not_save_to_close_documents']
        if parameters['document'] not in not_save_to_close:
            self.workspace.remove_document(parameters['document'])
        if parameters['previously_active_document'] != None:
            self.workspace.set_active_document(parameters['previously_active_document'])
            self.popover_manager.popup_at_button('document_switcher')

    def activate_mode(self, mode):
        if mode == 'normal':
            self.activate_normal_mode()
        elif mode == 'selection':
            self.activate_selection_mode()
    
    def activate_normal_mode(self):
        self.activate_set_root_document_button()
        self.update_unset_root_button()
        self.view.root_explaination_revealer.set_reveal_child(False)
        self.view.document_list.get_style_context().remove_class('selection-mode')
        self.view.document_list.get_style_context().add_class('normal-mode')

        for item in self.items.values():
            item.show()
            item.document_close_button.show()
            item.icon_box.show()
            item.radio_button_hover.hide()

        self.view.in_selection_mode = False

    def activate_selection_mode(self):
        self.view.set_root_document_button.set_sensitive(False)
        self.view.unset_root_document_button.set_sensitive(True)
        self.view.root_explaination_revealer.set_reveal_child(True)
        self.view.document_list.get_style_context().remove_class('normal-mode')
        self.view.document_list.get_style_context().add_class('selection-mode')

        for item in self.items.values():
            item.document_close_button.hide()
            item.icon_box.hide()
            item.radio_button_hover.show()
            if not item.document.is_latex_document():
                item.hide()

        self.view.in_selection_mode = True

    def activate_set_root_document_button(self):
        if len(self.workspace.open_latex_documents) > 0:
            self.view.set_root_document_button.set_sensitive(True)
        else:
            self.view.set_root_document_button.set_sensitive(False)

    def update_unset_root_button(self):
        if self.workspace.root_document != None:
            self.view.unset_root_document_button.set_sensitive(True)
        else:
            self.view.unset_root_document_button.set_sensitive(False)



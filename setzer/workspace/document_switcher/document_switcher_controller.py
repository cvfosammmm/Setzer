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

from setzer.app.service_locator import ServiceLocator
from setzer.dialogs.dialog_locator import DialogLocator


class DocumentSwitcherController(object):
    ''' Mediator between workspace and view. '''
    
    def __init__(self, document_switcher, workspace):
        self.document_switcher = document_switcher
        self.workspace = workspace
        self.button = ServiceLocator.get_main_window().headerbar.center_widget
        self.view = self.button.open_docs_widget

        self.click_controller = Gtk.GestureClick()
        self.click_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.click_controller.set_button(2)
        self.click_controller.connect('released', self.on_doclist_row_button_release)
        self.view.document_list.add_controller(self.click_controller)

        self.observe_document_switcher_view()

    def observe_document_switcher_view(self):
        self.view.document_list.connect('row-activated', self.on_doclist_row_activated)
        ServiceLocator.get_popover_manager().connect('popdown', self.on_popover_popdown)
        self.view.set_root_document_button.connect('clicked', self.set_selection_mode)
        self.view.unset_root_document_button.connect('clicked', self.unset_root_document)

    def on_doclist_row_activated(self, box, row, data=None):
        if self.view.in_selection_mode:
            self.document_switcher.set_mode('normal')
            self.workspace.set_one_document_root(row.document)
        else:
            ServiceLocator.get_popover_manager().popdown()
            self.workspace.set_active_document(row.document)

    def on_doclist_row_button_release(self, controller, n_press, x, y):
        if self.view.in_selection_mode: return False

        row = self.view.document_list.get_row_at_y(y)
        self.document_switcher.on_close_clicked(row.document_close_button, row.document)
        return True

    def on_popover_popdown(self, popover_manager, name):
        if name != 'document_switcher': return

        self.document_switcher.set_mode('normal')
        self.view.document_list.unselect_all()

    def set_selection_mode(self, action, parameter=None):
        self.document_switcher.set_mode('selection')
        return True

    def unset_root_document(self, action, parameter=None):
        self.document_switcher.set_mode('normal')
        self.workspace.unset_root_document()
        


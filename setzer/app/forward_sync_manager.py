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

from setzer.helpers.observable import Observable


class ForwardSyncManager(Observable):

    def __init__(self, workspace):
        Observable.__init__(self)

        self.workspace = workspace
        self.workspace.register_observer(self)
        self.document = None
        self.update_document()

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code in ['new_inactive_document', 'new_active_document', 'root_state_change']:
            self.update_document()
            self.set_can_sync()

        if change_code == 'can_sync_changed':
            self.set_can_sync()

        if change_code == 'is_root_changed':
            self.set_can_sync()

    def update_document(self):
        if self.workspace.root_document != None:
            self.set_document(self.workspace.root_document)
        elif self.workspace.active_document != None:
            self.set_document(self.workspace.active_document)
        elif self.document != None:
            self.document.unregister_observer(self)
            self.document = None

    def set_document(self, document):
        if document != self.document:
            if self.document != None:
                self.document.unregister_observer(self)
            self.document = document
            self.document.register_observer(self)

    def set_can_sync(self):
        can_sync = False
        if self.document != None:
            if self.document.is_latex_document():
                if self.document.can_sync:
                    can_sync = True
        self.can_sync = can_sync
        self.add_change_code('update_sync_state')

    def forward_sync(self, active_document):
        if self.workspace.root_document != None:
            self.workspace.root_document.forward_sync(active_document)
        else:
            active_document.forward_sync(active_document)



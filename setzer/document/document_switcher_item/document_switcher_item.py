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

import setzer.document.document_switcher_item.document_switcher_item_viewgtk as document_switcher_item_view


class DocumentSwitcherItem():

    def __init__(self, document):
        self.document = document
        self.view = document_switcher_item_view.OpenDocsPopoverItem(document)

        self.modified_state = document.get_modified()
        self.set_is_master()

        self.document.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'filename_change':
            self.view.set_name(self.document.get_displayname(), self.modified_state)

        if change_code == 'modified_changed':
            if self.document.get_modified() != self.modified_state:
                self.modified_state = self.document.get_modified()
                self.view.set_name(self.document.get_displayname(), self.modified_state)

        if change_code == 'displayname_change':
            self.view.set_name(self.document.get_displayname(), self.modified_state)

        if change_code == 'master_state_change':
            self.set_is_master()

    def set_is_master(self):
        if self.document.get_is_master() == True:
            self.view.icon.hide()
            self.view.master_icon.show_all()
            self.view.master_label.show_all()
        else:
            self.view.icon.show_all()
            self.view.master_icon.hide()
            self.view.master_label.hide()



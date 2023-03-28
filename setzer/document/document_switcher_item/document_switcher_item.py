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

import setzer.document.document_switcher_item.document_switcher_item_viewgtk as document_switcher_item_view


class DocumentSwitcherItem():

    def __init__(self, document):
        self.document = document
        self.view = document_switcher_item_view.OpenDocsPopoverItem(document)

        self.modified_state = document.content.get_modified()
        self.set_is_root()

        self.document.connect('filename_change', self.on_filename_change)
        self.document.connect('displayname_change', self.on_displayname_change)
        self.document.connect('is_root_changed', self.on_is_root_changed)
        self.document.content.connect('modified_changed', self.on_modified_changed)

    def on_filename_change(self, document, filename=None):
        self.view.set_name(self.document.get_displayname(), self.modified_state)

    def on_modified_changed(self, content):
        if self.document.content.get_modified() != self.modified_state:
            self.modified_state = self.document.content.get_modified()
            self.view.set_name(self.document.get_displayname(), self.modified_state)

    def on_displayname_change(self, document):
        self.view.set_name(self.document.get_displayname(), self.modified_state)

    def on_is_root_changed(self, document, is_root):
        self.set_is_root()

    def set_is_root(self):
        if self.document.get_is_root() == True:
            self.view.icon.hide()
            self.view.root_icon.show_all()
            self.view.root_label.show_all()
        else:
            self.view.icon.show_all()
            self.view.root_icon.hide()
            self.view.root_label.hide()



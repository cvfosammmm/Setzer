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


class ShortcutsbarPresenter(object):
    ''' Mediator between workspace and view. '''
    
    def __init__(self, document, view):
        self.document = document
        self.view = view
        self.document.content.connect('document_empty', self.on_document_empty)
        self.document.content.connect('document_not_empty', self.on_document_not_empty)
        self.width = None
        self.view.connect('size-allocate', self.on_size_allocate)
        
    def on_document_empty(self, document):
        self.update_wizard_button_visibility()

    def on_document_not_empty(self, document):
        self.update_wizard_button_visibility()

    def on_size_allocate(self, widget, allocation):
        if allocation.width != self.width:
            self.width = allocation.width
            self.update_wizard_button_visibility()

    def update_wizard_button_visibility(self):
        is_visible = (not self.document.is_empty()) and self.width > 675
        self.view.wizard_button.label_revealer.set_reveal_child(is_visible)



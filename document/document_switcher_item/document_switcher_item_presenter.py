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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import helpers.helpers as helpers
from app.service_locator import ServiceLocator


class DocumentSwitcherItemPresenter(object):
    
    def __init__(self, document, doclist_item):
        self.document = document
        self.settings = ServiceLocator.get_settings()
        self.doclist_item = doclist_item
        self.modified_state = document.get_modified()

        self.document.register_observer(self)
        self.document.get_buffer().connect('modified-changed', self.on_modified_change)

        self.set_is_master()

    '''
    *** notification handlers, get called by observed document
    '''

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'filename_change':
            self.doclist_item.set_name(self.document.get_displayname(), self.modified_state)

        if change_code == 'displayname_change':
            self.doclist_item.set_name(self.document.get_displayname(), self.modified_state)

        if change_code == 'master_state_change':
            self.set_is_master()

    def on_modified_change(self, buff):
        if buff.get_modified() != self.modified_state:
            self.modified_state = buff.get_modified()
            self.doclist_item.set_name(self.document.get_displayname(), self.modified_state)
            
    def set_is_master(self):
        if self.document.is_master == True:
            self.doclist_item.icon.hide()
            self.doclist_item.master_icon.show_all()
            self.doclist_item.master_label.show_all()
        else:
            self.doclist_item.icon.show_all()
            self.doclist_item.master_icon.hide()
            self.doclist_item.master_label.hide()



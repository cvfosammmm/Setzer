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


class DocumentPresenter(object):
    ''' Mediator between document and view. '''
    
    def __init__(self, document, document_view):
        self.document = document
        self.view = document_view
        self.settings = ServiceLocator.get_settings()
        self.doclist_item = self.view.doclist_item
        self.modified_state = document.get_modified()

        self.view.source_view.set_show_line_numbers(self.settings.get_value('preferences', 'show_line_numbers'))
        self.view.source_view.set_insert_spaces_instead_of_tabs(self.settings.get_value('preferences', 'spaces_instead_of_tabs'))
        self.view.source_view.set_tab_width(self.settings.get_value('preferences', 'tab_width'))
        self.view.source_view.set_highlight_current_line(self.settings.get_value('preferences', 'highlight_current_line'))
        if self.settings.get_value('preferences', 'enable_line_wrapping'):
            self.view.source_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        else:
            self.view.source_view.set_wrap_mode(Gtk.WrapMode.NONE)

        self.document.register_observer(self)
        self.document.get_buffer().connect('modified-changed', self.on_modified_change)
        self.settings.register_observer(self)

        self.set_is_master()

    '''
    *** notification handlers, get called by observed document
    '''

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'filename_change':
            self.doclist_item.set_name(self.document.get_displayname(), self.modified_state)

        if change_code == 'displayname_change':
            self.doclist_item.set_name(self.document.get_displayname(), self.modified_state)

        if change_code == 'settings_changed':
            section, item, value = parameter
            if (section, item) == ('preferences', 'show_line_numbers'):
                self.view.source_view.set_show_line_numbers(value)
            if (section, item) == ('preferences', 'spaces_instead_of_tabs'):
                self.view.source_view.set_insert_spaces_instead_of_tabs(value)
            if (section, item) == ('preferences', 'tab_width'):
                self.view.source_view.set_tab_width(value)
            if (section, item) == ('preferences', 'highlight_current_line'):
                self.view.source_view.set_highlight_current_line(value)
            if (section, item) == ('preferences', 'enable_line_wrapping'):
                if value == True:
                    self.view.source_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
                else:
                    self.view.source_view.set_wrap_mode(Gtk.WrapMode.NONE)

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



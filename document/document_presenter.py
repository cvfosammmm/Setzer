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

import time
import os.path


class DocumentPresenter(object):
    ''' Mediator between document and view. '''
    
    def __init__(self, document, document_view):
        self.document = document
        self.view = document_view
        self.settings = ServiceLocator.get_settings()
        self.doclist_item = self.view.doclist_item
        self.modified_state = document.get_modified()

        self.document.build_widget.view.build_button.show_all()
        self.document.build_widget.view.stop_button.hide()

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

        self.build_button_state = ('idle', int(time.time()*1000))
        self.set_clean_button_state()
        self.set_is_master()

    '''
    *** notification handlers, get called by observed document
    '''

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'filename_change':
            self.doclist_item.set_name(self.document.get_displayname(), self.modified_state)
            self.set_clean_button_state()

        if change_code == 'displayname_change':
            self.doclist_item.set_name(self.document.get_displayname(), self.modified_state)

        if change_code == 'document_state_change':
            error_count = 0
            for item in self.document.build_log_items:
                if item[0] == 'Error':
                    error_count += 1
            if error_count > 0:
                error_color = helpers.theme_color_to_css(self.document.view.get_style_context(), 'error_color')
                message = '<span color="' + error_color + '">Failed</span> (' + str(error_count) + ' error' + ('s' if error_count > 1 else '') + ')!'
            else:
                message = 'Success!'

            self.on_build_state_change(message)
            self.set_clean_button_state()

        if change_code == 'settings_changed':
            section, item, value = parameter
            if (section, item) == ('preferences', 'cleanup_build_files'):
                self.set_clean_button_state()
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

        if change_code == 'cleaned_up_build_files':
            self.set_clean_button_state()

        if change_code == 'master_state_change':
            self.set_is_master()

    def on_modified_change(self, buff):
        if buff.get_modified() != self.modified_state:
            self.modified_state = buff.get_modified()
            self.doclist_item.set_name(self.document.get_displayname(), self.modified_state)
            
    def on_build_state_change(self, message=''):
        document = self.document
        state = document.get_state()
        selfstate = self.build_button_state
        build_widget = self.document.build_widget.view
        if state == 'idle' or state == '':
            build_button_state = ('idle', int(time.time()*1000))
        else:
            build_button_state = ('building', int(time.time()*1000))

        build_widget.build_timer.show_all()
        if selfstate[0] != build_button_state[0]:
            self.build_button_state = build_button_state
            if build_button_state[0] == 'idle':
                build_widget.build_button.set_sensitive(True)
                build_widget.build_button.show_all()
                build_widget.stop_button.hide()
                build_widget.stop_timer()
                build_widget.show_result(message)
                if build_widget.get_parent() != None:
                    build_widget.hide_timer(4000)
            else:
                build_widget.build_button.set_sensitive(False)
                build_widget.build_button.hide()
                build_widget.stop_button.show_all()
                build_widget.reset_timer()
                build_widget.show_timer()
                build_widget.start_timer()

    def set_is_master(self):
        if self.document.is_master == True:
            self.doclist_item.icon.hide()
            self.doclist_item.master_icon.show_all()
            self.doclist_item.master_label.show_all()
        else:
            self.doclist_item.icon.show_all()
            self.doclist_item.master_icon.hide()
            self.doclist_item.master_label.hide()

    def set_clean_button_state(self):
        def get_clean_button_state(document):
            file_endings = ['.aux', '.blg', '.bbl', '.dvi', '.fdb_latexmk', '.fls', '.idx' ,'.ilg', '.ind', '.log', '.nav', '.out', '.snm', '.synctex.gz', '.toc']
            if document != None:
                if document.filename != None:
                    pathname = document.get_filename().rsplit('/', 1)
                    for ending in file_endings:
                        filename = pathname[0] + '/' + pathname[1].rsplit('.', 1)[0] + ending
                        if os.path.exists(filename): return True
            return False

        if self.settings.get_value('preferences', 'cleanup_build_files') == True:
            self.document.build_widget.view.clean_button.hide()
        else:
            self.document.build_widget.view.clean_button.show_all()
            self.document.build_widget.view.clean_button.set_sensitive(get_clean_button_state(self.document))
    


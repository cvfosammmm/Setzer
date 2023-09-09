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


class DocumentPresenter(object):
    ''' Mediator between document and view. '''
    
    def __init__(self, document, document_view):
        self.document = document
        self.view = document_view
        self.settings = ServiceLocator.get_settings()

        self.view.source_view.set_show_line_numbers(False)
        self.view.source_view.set_insert_spaces_instead_of_tabs(self.settings.get_value('preferences', 'spaces_instead_of_tabs'))
        self.view.source_view.set_tab_width(self.settings.get_value('preferences', 'tab_width'))
        self.view.source_view.set_highlight_current_line(self.settings.get_value('preferences', 'highlight_current_line'))
        self.document.source_buffer.set_highlight_matching_brackets(self.settings.get_value('preferences', 'highlight_matching_brackets'))
        if self.settings.get_value('preferences', 'enable_line_wrapping'):
            self.view.source_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        else:
            self.view.source_view.set_wrap_mode(Gtk.WrapMode.NONE)

        self.settings.connect('settings_changed', self.on_settings_changed)

    def on_settings_changed(self, settings, parameter):
        section, item, value = parameter
        if (section, item) == ('preferences', 'spaces_instead_of_tabs'):
            self.view.source_view.set_insert_spaces_instead_of_tabs(value)
        if (section, item) == ('preferences', 'tab_width'):
            self.view.source_view.set_tab_width(value)
        if (section, item) == ('preferences', 'highlight_current_line'):
            self.view.source_view.set_highlight_current_line(value)
        if (section, item) == ('preferences', 'highlight_matching_brackets'):
            self.document.source_buffer.set_highlight_matching_brackets(value)
        if (section, item) == ('preferences', 'enable_line_wrapping'):
            if value == True:
                self.view.source_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
            else:
                self.view.source_view.set_wrap_mode(Gtk.WrapMode.NONE)



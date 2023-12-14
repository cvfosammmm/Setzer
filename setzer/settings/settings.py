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
from gi.repository import Pango
import os.path
import pickle

from setzer.helpers.observable import Observable


class Settings(Observable):
    ''' Settings controller for saving application state. '''

    def __init__(self, pathname):
        Observable.__init__(self)

        self.pathname = pathname
    
        self.data = dict()
        self.defaults = dict()
        self.set_defaults()

        if not self.unpickle():
            self.data = self.defaults
            self.pickle()
            
    def set_defaults(self):
        self.defaults['window_state'] = dict()
        self.defaults['window_state']['width'] = 1020
        self.defaults['window_state']['height'] = 550
        self.defaults['window_state']['is_maximized'] = False
        self.defaults['window_state']['show_symbols'] = False
        self.defaults['window_state']['show_document_structure'] = False
        self.defaults['window_state']['sidebar_paned_position'] = -1
        self.defaults['window_state']['show_help'] = False
        self.defaults['window_state']['show_preview'] = False
        self.defaults['window_state']['show_build_log'] = False
        self.defaults['window_state']['preview_paned_position'] = -1
        self.defaults['window_state']['notebook_paned_position'] = -1
        self.defaults['window_state']['build_log_paned_position'] = -1
        
        self.defaults['app_document_wizard'] = dict()
        self.defaults['app_document_wizard']['presets'] = None
        
        self.defaults['app_bibtex_wizard'] = dict()
        self.defaults['app_bibtex_wizard']['presets'] = None
        
        self.defaults['app_include_bibtex_file_dialog'] = dict()
        self.defaults['app_include_bibtex_file_dialog']['presets'] = None

        self.defaults['app_recent_symbols'] = {'symbols': []}

        self.defaults['preferences'] = dict()
        self.defaults['preferences']['cleanup_build_files'] = True
        self.defaults['preferences']['autoshow_build_log'] = 'errors_warnings'
        self.defaults['preferences']['latex_interpreter'] = 'xelatex'
        self.defaults['preferences']['use_latexmk'] = False
        self.defaults['preferences']['color_scheme'] = 'default'
        self.defaults['preferences']['recolor_pdf'] = False
        self.defaults['preferences']['spaces_instead_of_tabs'] = True
        self.defaults['preferences']['tab_width'] = 4
        self.defaults['preferences']['show_line_numbers'] = True
        self.defaults['preferences']['enable_code_folding'] = True
        self.defaults['preferences']['enable_line_wrapping'] = True
        self.defaults['preferences']['highlight_current_line'] = False
        self.defaults['preferences']['highlight_matching_brackets'] = True
        self.defaults['preferences']['build_option_system_commands'] = 'disable'
        self.defaults['preferences']['enable_autocomplete'] = True
        self.defaults['preferences']['enable_bracket_completion'] = True
        self.defaults['preferences']['bracket_selection'] = True
        self.defaults['preferences']['tab_jump_brackets'] = True
        self.defaults['preferences']['update_matching_blocks'] = True

        self.defaults['preferences']['use_system_font'] = True
        textview = Gtk.TextView()
        textview.set_monospace(True)
        font_string = textview.get_pango_context().get_font_description().to_string()
        self.defaults['preferences']['font_string'] = font_string

    def get_value(self, section, item):
        try: value = self.data[section][item]
        except KeyError:
            value = self.defaults[section][item]
            self.set_value(section, item, value)
        return value

    def set_value(self, section, item, value):
        try: section_dict = self.data[section]
        except KeyError:
            section_dict = dict()
            self.data[section] = section_dict
        section_dict[item] = value
        self.add_change_code('settings_changed', (section, item, value))
        
    def unpickle(self):
        ''' Load settings from home folder. '''
        
        # create folder if it does not exist
        if not os.path.isdir(self.pathname):
            os.makedirs(self.pathname)
        
        try: filehandle = open(os.path.join(self.pathname, 'settings.pickle'), 'rb')
        except IOError: return False
        else:
            try: self.data = pickle.load(filehandle)
            except EOFError: False

        return True
        
    def pickle(self):
        ''' Save settings in home folder. '''
        
        try: filehandle = open(os.path.join(self.pathname, 'settings.pickle'), 'wb')
        except IOError: return False
        else: pickle.dump(self.data, filehandle)
        


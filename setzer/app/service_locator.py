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

import re
import os.path
from xdg.BaseDirectory import xdg_config_home

import setzer.app.settings as settingscontroller
import setzer.helpers.popover_menu_builder as popover_menu_builder


class ServiceLocator(object):

    settings = None
    setzer_version = None
    resources_path = None
    app_icons_path = None
    popover_menu_builder = None
    build_log_doc_regex = re.compile('( *\((.*\.tex))')
    build_log_item_regex = re.compile('((?:Overfull \\\\hbox|Underfull \\\\hbox|No file .*\.|File .* does not exist\.|! I can\'t find file\.|! File .* not found\.|(?:LaTeX|pdfTeX|LuaTeX|Package|Class) .*Warning.*:|LaTeX Font Warning:|! Undefined control sequence\.|! Missing (?:.*) inserted.|! Package .* Error:|! (?:LaTeX|LuaTeX) Error:|No file .*\.bbl.).*\\n)')
    build_log_badbox_line_number_regex = re.compile('lines ([0-9]+)--([0-9]+)')
    build_log_other_line_number_regex = re.compile('(l.| input line \n| input line )([0-9]+)( |.)')
    bibtex_log_item_regex = re.compile('Warning--(.*)\n--line ([0-9]+) of file (.*)|I couldn\'t open style file (.*).bst\n---line ([0-9]+) of file (.*)')
    symbols_regex = re.compile('\\\\(label|include|input|bibliography)\{((?:\s|\w|\:|,)*)\}|\\\\(usepackage)(?:\[.*\]){0,1}\{((?:\s|\w|\:|,)*)\}')
    blocks_regex = re.compile('\n.*\\\\(begin|end)\{((?:\w)*(?:\*){0,1})\}|\n.*\\\\(part|chapter|section|subsection|subsubsection)(?:\*){0,1}\{')
    forward_synctex_regex = re.compile('\nOutput:.*\nPage:([0-9]+)\nx:.*\ny:.*\nh:((?:[0-9]|\\.)+)\nv:((?:[0-9]|\\.)+)\nW:((?:[0-9]|\\.)+)\nH:((?:[0-9]|\\.)+)\nbefore:.*\noffset:.*\nmiddle:.*\nafter:.*')
    backward_synctex_regex = re.compile('\nOutput:.*\nInput:(.*\\.tex)\nLine:([0-9]+)\nColumn:((?:[0-9]|-)+)\nOffset:((?:[0-9]|-)+)\nContext:.*\n')

    def init_main_window(main_window):
        ServiceLocator.main_window = main_window

    def get_main_window():
        return ServiceLocator.main_window
    
    def get_build_log_doc_regex():
        return ServiceLocator.build_log_doc_regex
    
    def get_build_log_item_regex():
        return ServiceLocator.build_log_item_regex
    
    def get_build_log_badbox_line_number_regex():
        return ServiceLocator.build_log_badbox_line_number_regex
    
    def get_build_log_other_line_number_regex():
        return ServiceLocator.build_log_other_line_number_regex

    def get_bibtex_log_item_regex():
        return ServiceLocator.bibtex_log_item_regex

    def get_symbols_regex():
        return ServiceLocator.symbols_regex

    def get_blocks_regex():
        return ServiceLocator.blocks_regex

    def get_forward_synctex_regex():
        return ServiceLocator.forward_synctex_regex

    def get_backward_synctex_regex():
        return ServiceLocator.backward_synctex_regex

    def get_settings():
        if ServiceLocator.settings == None:
            ServiceLocator.settings = settingscontroller.Settings(ServiceLocator.get_config_folder())
        return ServiceLocator.settings

    def get_popover_menu_builder():
        if ServiceLocator.popover_menu_builder == None:
            ServiceLocator.popover_menu_builder = popover_menu_builder.PopoverMenuBuilder()
        return ServiceLocator.popover_menu_builder

    def get_config_folder():
        return os.path.join(xdg_config_home, 'setzer')

    def init_setzer_version(setzer_version):
        ServiceLocator.setzer_version = setzer_version

    def get_setzer_version():
        return ServiceLocator.setzer_version

    def init_resources_path(resources_path):
        ServiceLocator.resources_path = resources_path

    def get_resources_path():
        return ServiceLocator.resources_path

    def init_app_icons_path(app_icons_path):
        ServiceLocator.app_icons_path = app_icons_path

    def get_app_icons_path():
        return ServiceLocator.app_icons_path



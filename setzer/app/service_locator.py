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
import xml.etree.ElementTree as ET

import setzer.app.settings as settingscontroller
import setzer.app.autocomplete_provider.autocomplete_provider as autocomplete_provider
import setzer.helpers.popover_menu_builder as popover_menu_builder


class ServiceLocator(object):

    settings = None
    setzer_version = None
    resources_path = None
    app_icons_path = None
    regexes = dict()
    popover_menu_builder = None
    autocomplete_provider = None
    packages_dict = None

    def init_main_window(main_window):
        ServiceLocator.main_window = main_window

    def get_main_window():
        return ServiceLocator.main_window

    def get_theme_fg_color():
        return ServiceLocator.main_window.get_style_context().lookup_color('theme_fg_color')[1]

    def get_theme_bg_color():
        return ServiceLocator.main_window.get_style_context().lookup_color('theme_bg_color')[1]

    def get_error_color():
        return ServiceLocator.main_window.get_style_context().lookup_color('error_color')[1]

    def get_is_dark_mode():
        fg_color = ServiceLocator.get_theme_fg_color()
        bg_color = ServiceLocator.get_theme_bg_color()
        return (fg_color.red + fg_color.green + fg_color.blue) * fg_color.alpha > (bg_color.red + bg_color.green + bg_color.blue) * bg_color.alpha

    def get_regex_object(pattern):
        try:
            regex = ServiceLocator.regexes[pattern]
        except KeyError:
            regex = re.compile(pattern)
            ServiceLocator.regexes[pattern] = regex
        return regex

    def get_settings():
        if ServiceLocator.settings == None:
            ServiceLocator.settings = settingscontroller.Settings(ServiceLocator.get_config_folder())
        return ServiceLocator.settings

    def get_popover_menu_builder():
        if ServiceLocator.popover_menu_builder == None:
            ServiceLocator.popover_menu_builder = popover_menu_builder.PopoverMenuBuilder()
        return ServiceLocator.popover_menu_builder

    def init_autocomplete_provider(workspace):
        path = ServiceLocator.get_resources_path()
        latex_parser_regex = ServiceLocator.get_regex_object(r'\\(label|include|input|bibliography|addbibresource)\{((?:\s|\w|\:|\.|,)*)\}|\\(usepackage)(?:\[.*\]){0,1}\{((?:\s|\w|\:|,)*)\}|\\(bibitem)(?:\[.*\]){0,1}\{((?:\s|\w|\:)*)\}')
        bibtex_parser_regex = ServiceLocator.get_regex_object(r'@(\w+)\{(\w+)')
        ServiceLocator.autocomplete_provider = autocomplete_provider.AutocompleteProvider(path, workspace, latex_parser_regex, bibtex_parser_regex)

    def get_autocomplete_provider():
        return ServiceLocator.autocomplete_provider

    def get_packages_dict():
        if ServiceLocator.packages_dict == None:
            ServiceLocator.packages_dict = dict()

            resources_path = ServiceLocator.get_resources_path()
            tree = ET.parse(os.path.join(resources_path, 'latexdb', 'packages', 'general.xml'))
            root = tree.getroot()
            for child in root:
                attrib = child.attrib
                ServiceLocator.packages_dict[attrib['name']] = {'command': attrib['text'], 'description': attrib['description']}
        return ServiceLocator.packages_dict

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



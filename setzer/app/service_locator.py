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
gi.require_version('GtkSource', '4')
from gi.repository import GtkSource
from gi.repository import GLib

import re
import os, os.path
import xml.etree.ElementTree as ET

import setzer.app.settings as settingscontroller
import setzer.app.autocomplete_provider.autocomplete_provider as autocomplete_provider
import setzer.app.color_manager as color_manager
import setzer.app.font_manager as font_manager
import setzer.helpers.popover_menu_builder as popover_menu_builder


class ServiceLocator(object):

    main_window = None
    workspace = None
    settings = None
    setzer_version = None
    resources_path = None
    app_icons_path = None
    regexes = dict()
    popover_menu_builder = None
    autocomplete_provider = None
    packages_dict = None
    source_language_manager = None
    source_style_scheme_manager = None
    color_manager = None
    font_manager = None

    def init_main_window(main_window):
        ServiceLocator.main_window = main_window

    def get_main_window():
        return ServiceLocator.main_window

    def init_workspace(workspace):
        ServiceLocator.workspace = workspace

    def get_workspace():
        return ServiceLocator.workspace

    def get_is_dark_mode():
        fg_color = ServiceLocator.get_color_manager().get_theme_color('theme_fg_color')
        bg_color = ServiceLocator.get_color_manager().get_theme_color('theme_bg_color')
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

    def get_source_language_manager():
        if ServiceLocator.source_language_manager == None:
            ServiceLocator.source_language_manager = GtkSource.LanguageManager()
            path = os.path.join(ServiceLocator.get_resources_path(), 'gtksourceview', 'language-specs')
            ServiceLocator.source_language_manager.set_search_path((path,))
        return ServiceLocator.source_language_manager

    def get_source_style_scheme_manager():
        if ServiceLocator.source_style_scheme_manager == None:
            ServiceLocator.source_style_scheme_manager = GtkSource.StyleSchemeManager()
            path1 = os.path.join(ServiceLocator.get_resources_path(), 'gtksourceview', 'styles')
            if not os.path.isdir(os.path.join(ServiceLocator.get_config_folder(), 'syntax_schemes')):
                os.mkdir(os.path.join(ServiceLocator.get_config_folder(), 'syntax_schemes'))
            path2 = os.path.join(ServiceLocator.get_config_folder(), 'syntax_schemes')
            ServiceLocator.source_style_scheme_manager.set_search_path((path1, path2))
        return ServiceLocator.source_style_scheme_manager

    def get_font_manager():
        if ServiceLocator.font_manager == None:
            ServiceLocator.font_manager = font_manager.FontManager(ServiceLocator.get_main_window(), ServiceLocator.get_settings())
        return ServiceLocator.font_manager

    def get_color_manager():
        if ServiceLocator.color_manager == None:
            ServiceLocator.color_manager = color_manager.ColorManager(ServiceLocator.get_main_window(), ServiceLocator.get_settings(), ServiceLocator.get_source_style_scheme_manager())
        return ServiceLocator.color_manager

    def get_popover_menu_builder():
        if ServiceLocator.popover_menu_builder == None:
            ServiceLocator.popover_menu_builder = popover_menu_builder.PopoverMenuBuilder()
        return ServiceLocator.popover_menu_builder

    def init_autocomplete_provider(workspace):
        path = ServiceLocator.get_resources_path()
        latex_parser_regex = ServiceLocator.get_regex_object(r'\\(label|include|input|bibliography|addbibresource)\{((?:\s|\w|\:|\.|,)*)\}|\\(usepackage)(?:\[.*\]){0,1}\{((?:\s|\w|\:|,)*)\}|\\(bibitem)(?:\[.*\]){0,1}\{((?:\s|\w|\:)*)\}')
        bibtex_parser_regex = ServiceLocator.get_regex_object(r'@(\w+)\{(\w+)')
        ServiceLocator.autocomplete_provider = autocomplete_provider.AutocompleteProvider(path, workspace, latex_parser_regex, bibtex_parser_regex, ServiceLocator.get_packages_dict())

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
        return os.path.join(GLib.get_user_config_dir(), 'setzer')

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



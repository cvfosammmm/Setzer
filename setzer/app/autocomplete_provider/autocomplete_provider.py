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
from gi.repository import GObject

import os.path
import xml.etree.ElementTree as ET

import setzer.helpers.timer as timer


class AutocompleteProvider(object):

    def __init__(self, resources_path, workspace):
        self.workspace = workspace
        self.resources_path = resources_path

        self.static_proposals = dict()
        self.dynamic_word_beginnings = list()
        self.dynamic_proposals = dict()

        self.generate_static_proposals()
        self.generate_dynamic_word_beginnings()

    def get_items_for_completion_window(self, current_word, last_tabbed_command):
        items = list()

        items_all = self.get_items(current_word)
        items_all.reverse()

        if len(items_all) != 1 or current_word[1:].lower() != items_all[0]['command']:
            count = 0
            items_rest = list()
            for item in items_all:
                if last_tabbed_command != None and last_tabbed_command == item['command']:
                    items.insert(0, item)
                    count += 1
                elif item['command'][:len(current_word) - 1] == current_word[1:]:
                    items.append(item)
                    count += 1
                else:
                    items_rest.append(item)
            if count >= 5:
                items = items[:5]
            items.reverse()
            items = items_rest[:5 - count] + items

        return items

    def get_items(self, word):
        items = list()
        try: items = self.static_proposals[word[1:].lower()][::-1]
        except KeyError: pass
        dynamic_items = self.get_dynamic_items(word)[::-1]
        return items + dynamic_items

    def get_dynamic_items(self, word):
        dynamic_items = list()
        offset = word.find('{')
        if offset > 1:
            word_beginning = word[:offset + 1]
        else:
            word_beginning = word
        if word_beginning in self.dynamic_word_beginnings:
            dynamic_items += self.get_dynamic_reference_commands(word)
            dynamic_items += self.get_dynamic_bibliography_commands(word)
        return dynamic_items

    @timer.timer
    def get_dynamic_reference_commands(self, word):
        dynamic_items = list()
        for document in self.workspace.open_documents:
            if len(dynamic_items) >= 5: break

            labels_dict = document.parser.get_labels()
            if 'labels' in labels_dict:
                labels = labels_dict['labels']
                if labels != None:
                    ref_types = list()
                    ref_types.append(('ref', _('Reference to \'{label}\'')))
                    ref_types.append(('pageref', _('Reference to page of \'{label}\'')))
                    ref_types.append(('eqref', _('Reference to \'{label}\', with parantheses')))
                    for label in iter(labels):
                        if len(dynamic_items) >= 5: break

                        for ref_type in ref_types:
                            if len(dynamic_items) >= 5: break

                            command = {'command': ref_type[0] + '{' + label + '}', 'description': ref_type[1].format(label=label)}
                            if command['command'][:len(word) - 1] == word[1:].lower():
                                if command['command'] not in [item['command'] for item in dynamic_items]:
                                    dynamic_items.append(command)
        return dynamic_items

    @timer.timer
    def get_dynamic_bibliography_commands(self, word):
        dynamic_items = list()
        for document in self.workspace.open_documents:
            if len(dynamic_items) >= 5: break

            labels_dict = document.parser.get_labels()
            if 'bibitems' in labels_dict:
                bibitems = labels_dict['bibitems']
                if bibitems != None:
                    ref_types = list()
                    ref_types.append(('cite', _('Cite \'{bibitem}\'')))
                    ref_types.append(('citet', _('Cite \'{bibitem}\' (abbreviated)')))
                    ref_types.append(('citep', _('Cite \'{bibitem}\' (abbreviated with brackets)')))
                    ref_types.append(('citet*', _('Cite \'{bibitem}\' (detailed)')))
                    ref_types.append(('citep*', _('Cite \'{bibitem}\' (detailed with brackets)')))
                    ref_types.append(('citealt', _('Cite \'{bibitem}\' (alternative style 1)')))
                    ref_types.append(('citealp', _('Cite \'{bibitem}\' (alternative style 2)')))
                    ref_types.append(('citeauthor', _('Cite \'{bibitem}\' (author)')))
                    ref_types.append(('citeauthor*', _('Cite \'{bibitem}\' (author detailed)')))
                    ref_types.append(('citeyear', _('Cite \'{bibitem}\' (year)')))
                    ref_types.append(('citeyearpar', _('Cite \'{bibitem}\' (year with brackets)')))
                    for bibitem in iter(bibitems):
                        if len(dynamic_items) >= 5: break

                        for ref_type in ref_types:
                            if len(dynamic_items) >= 5: break

                            command = {'command': ref_type[0] + '{' + bibitem + '}', 'description': ref_type[1].format(bibitem=bibitem)}
                            if command['command'][:len(word) - 1] == word[1:].lower():
                                if command['command'] not in [item['command'] for item in dynamic_items]:
                                    dynamic_items.append(command)
        return dynamic_items

    def get_commands(self):
        commands = dict()
        tree = ET.parse(os.path.join(self.resources_path, 'latexdb', 'commands', 'general.xml'))
        root = tree.getroot()
        for child in root:
            attrib = child.attrib
            commands[attrib['name']] = {'command': attrib['text'], 'description': attrib['description']}
        return commands

    def generate_static_proposals(self):
        commands = self.get_commands()

        self.static_proposals = dict()
        for command in commands.values():
            for i in range(1, len(command['command']) + 1):
                try:
                    if len(self.static_proposals[command['command'][0:i].lower()]) < 5:
                        self.static_proposals[command['command'][0:i].lower()].append(command)
                except KeyError:
                    self.static_proposals[command['command'][0:i].lower()] = [command]

    def generate_dynamic_word_beginnings(self):
        commands = ('ref{', 'pageref{', 'eqref{', 'cite{', 'citet{', 'citep{', 'citet*{', 'citep*{', 'citealt{', 'citealp{', 'citeauthor{', 'citeauthor*{', 'citeyear{', 'citeyearpar{')

        self.dynamic_word_beginnings = list()
        for command in commands:
            for i in range(1, len(command) + 1):
                self.dynamic_word_beginnings.append('\\' + command[:i])


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
import time
import xml.etree.ElementTree as ET

import setzer.helpers.timer as timer


class AutocompleteProvider(object):

    def __init__(self, resources_path, workspace, latex_parser_regex, bibtex_parser_regex):
        self.workspace = workspace
        self.resources_path = resources_path
        self.latex_parser_regex = latex_parser_regex
        self.bibtex_parser_regex = bibtex_parser_regex

        self.static_proposals = dict()
        self.dynamic_word_beginnings = list()
        self.included_files_labels = dict()

        self.ref_types = dict()
        self.ref_types['references'] = list()
        self.ref_types['references'].append(('ref', _('Reference to \'{label}\''), _('Reference')))
        self.ref_types['references'].append(('pageref', _('Reference to page of \'{label}\''), _('Page reference')))
        self.ref_types['references'].append(('eqref', _('Reference to \'{label}\', with parantheses'), _('Reference with parantheses')))
        self.ref_types['citations'] = list()
        self.ref_types['citations'].append(('cite', _('Cite \'{label}\''), _('Citation')))
        self.ref_types['citations'].append(('citet', _('Cite \'{label}\' (abbreviated)'), _('Citation (abbreviated)')))
        self.ref_types['citations'].append(('citep', _('Cite \'{label}\' (abbreviated with brackets)'), _('Citation (abbreviated with brackets)')))
        self.ref_types['citations'].append(('citet*', _('Cite \'{label}\' (detailed)'), _('Citation (detailed)')))
        self.ref_types['citations'].append(('citep*', _('Cite \'{label}\' (detailed with brackets)'), _('Citation (detailed with brackets)')))
        self.ref_types['citations'].append(('citealt', _('Cite \'{label}\' (alternative style 1)'), _('Citation (alternative style 1)')))
        self.ref_types['citations'].append(('citealp', _('Cite \'{label}\' (alternative style 2)'), _('Citation (alternative style 2)')))
        self.ref_types['citations'].append(('citeauthor', _('Cite \'{label}\' (author)'), _('Citation (author)')))
        self.ref_types['citations'].append(('citeauthor*', _('Cite \'{label}\' (author detailed)'), _('Citation (author detailed)')))
        self.ref_types['citations'].append(('citeyear', _('Cite \'{label}\' (year)'), _('Citation (year)')))
        self.ref_types['citations'].append(('citeyearpar', _('Cite \'{label}\' (year with brackets)'), _('Citation (year with brackets)')))

        self.last_command = None
        self.last_dynamic_proposals = list()

        self.generate_dynamic_word_beginnings()
        self.generate_static_proposals()
        self.parse_included_files()
        GObject.timeout_add(2000, self.parse_included_files)

    def get_items_for_completion_window(self, current_word, last_tabbed_command):
        items = list()

        items_all = self.get_items(current_word)

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
            items = items_rest[:5 - count] + items

        return items

    def get_items(self, word):
        items = list()
        try: static_items = self.static_proposals[word[1:].lower()]
        except KeyError: static_items = list()
        dynamic_items = self.get_dynamic_items(word)
        add_dynamic = True
        for item in sorted(static_items, key=lambda command: command['command'].lower()):
            if add_dynamic and len(dynamic_items) > 0 and dynamic_items[0]['command'].lower() < item['command'].lower():
                add_dynamic = False
                items += dynamic_items
            items.append(item)
        if add_dynamic:
            items += dynamic_items
        return items

    def get_dynamic_items(self, word):
        if word == self.last_command:
            return self.last_dynamic_proposals
        else:
            dynamic_items = list()
            offset = word.find('{')
            if offset > 1:
                word_beginning = word[:offset + 1]
            else:
                word_beginning = word
            if word_beginning in self.dynamic_word_beginnings['references']:
                dynamic_items += self.get_dynamic_reference_commands(word)
            elif word_beginning in self.dynamic_word_beginnings['citations']:
                dynamic_items += self.get_dynamic_bibliography_commands(word)

            self.last_command = word
            self.last_dynamic_proposals = dynamic_items
        return dynamic_items

    def get_dynamic_reference_commands(self, word):
        ref_types = self.ref_types['references']

        dynamic_items = list()
        labels = self.get_labels_for_dynamic_items('labels')

        for ref_type in ref_types:
            if len(dynamic_items) >= 5: break
            self.append_to_dynamic_items(word, dynamic_items, ref_type, labels)
        return dynamic_items

    def get_dynamic_bibliography_commands(self, word):
        ref_types = self.ref_types['citations']

        dynamic_items = list()
        labels = self.get_labels_for_dynamic_items('bibitems')

        for ref_type in ref_types:
            if len(dynamic_items) >= 5: break
            self.append_to_dynamic_items(word, dynamic_items, ref_type, labels)
        return dynamic_items

    #@timer.timer
    def get_labels_for_dynamic_items(self, label_type):
        labels_first = set()
        labels_second = set()
        labels_rest = set()

        pathnames_done = set()
        if self.workspace.active_document != None:
            pathnames_done = pathnames_done | {self.workspace.active_document.get_filename()}
            labels_dict = self.workspace.active_document.parser.get_labels()
            if label_type in labels_dict:
                labels_first = labels_first | labels_dict[label_type]

            included_files = self.workspace.active_document.get_included_files()
            for pathname in included_files:
                if pathname not in pathnames_done:
                    pathnames_done = pathnames_done | {pathname}
                    if pathname in self.included_files_labels:
                        labels_dict = self.included_files_labels[pathname]['labels']
                        if label_type in labels_dict:
                            labels_second = labels_second | labels_dict[label_type]
                    else:
                        document_object = self.workspace.get_document_by_filename(pathname)
                        if document_object:
                            labels_dict = document_object.parser.get_labels()
                            if label_type in labels_dict:
                                labels_second = labels_second | labels_dict[label_type]

        for document in self.workspace.open_documents:
            pathnames = {document.get_filename()} | document.get_included_files()
            for pathname in pathnames:
                if pathname not in pathnames_done:
                    pathnames_done = pathnames_done | {pathname}
                    if pathname in self.included_files_labels:
                        labels_dict = self.included_files_labels[pathname]['labels']
                        if label_type in labels_dict:
                            labels_rest = labels_rest | labels_dict[label_type]
                    else:
                        document_object = self.workspace.get_document_by_filename(pathname)
                        if document_object:
                            labels_dict = document_object.parser.get_labels()
                            if label_type in labels_dict:
                                labels_rest = labels_rest | labels_dict[label_type]

        labels = ['•'] + list(labels_first) + list(labels_second) + list(labels_rest)
        return labels

    def append_to_dynamic_items(self, word, items, ref_type, labels):
        for label in iter(labels):
            if len(items) >= 5: break

            if label == '•':
                description = ref_type[2]
            else:
                description = ref_type[1].format(label=label)
            command = {'command': ref_type[0] + '{' + label + '}', 'description': description}
            if command['command'][:len(word) - 1] == word[1:].lower():
                if command['command'] not in [item['command'] for item in items]:
                    items.append(command)

    #@timer.timer
    def parse_included_files(self):
        current_includes = set()
        open_docs_pathnames = self.workspace.get_open_documents_filenames()
        for document in self.workspace.open_latex_documents:
            labels_dict = document.parser.get_labels()
            current_includes = current_includes | labels_dict['bibliographies'] | labels_dict['included_latex_files']
            for pathname in labels_dict['bibliographies']:
                if pathname not in open_docs_pathnames:
                    if os.path.isfile(pathname):
                        if pathname not in self.included_files_labels:
                            self.included_files_labels[pathname] = self.parse_bibtex_file(pathname)
                        else:
                            last_parse_time = self.included_files_labels[pathname]['last_parse_time']
                            if last_parse_time < os.path.getmtime(pathname):
                                self.included_files_labels[pathname] = self.parse_bibtex_file(pathname)
            for pathname in labels_dict['included_latex_files']:
                if pathname not in open_docs_pathnames:
                    if os.path.isfile(pathname):
                        if pathname not in self.included_files_labels:
                            self.included_files_labels[pathname] = self.parse_latex_file(pathname)
                        else:
                            last_parse_time = self.included_files_labels[pathname]['last_parse_time']
                            if last_parse_time < os.path.getmtime(pathname):
                                self.included_files_labels[pathname] = self.parse_latex_file(pathname)
        for pathname in list(self.included_files_labels):
            if pathname not in current_includes or pathname in open_docs_pathnames:
                del(self.included_files_labels[pathname])
        return True

    def parse_latex_file(self, pathname):
        with open(pathname, 'r') as f:
            text = f.read()
        labels = set()
        bibitems = set()
        for match in self.latex_parser_regex.finditer(text):
            if match.group(1) == 'label':
                labels = labels | {match.group(2).strip()}
            elif match.group(5) == 'bibitem':
                bibitems = bibitems | {match.group(6).strip()}
        return {'last_parse_time': time.time(), 'labels': {'labels': labels, 'bibitems': bibitems}}

    def parse_bibtex_file(self, pathname):
        with open(pathname, 'r') as f:
            text = f.read()
        bibitems = set()
        for match in self.bibtex_parser_regex.finditer(text):
            bibitems = bibitems | {match.group(2).strip()}
        return {'last_parse_time': time.time(), 'labels': {'bibitems': bibitems}}

    def generate_dynamic_word_beginnings(self):
        self.dynamic_word_beginnings = dict()
        for ref_types_type in self.ref_types:
            self.dynamic_word_beginnings[ref_types_type] = list()
            for command in self.ref_types[ref_types_type]:
                command = command[0] + '{'
                for i in range(1, len(command) + 1):
                    self.dynamic_word_beginnings[ref_types_type].append('\\' + command[:i])

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

    def get_commands(self):
        commands = dict()
        tree = ET.parse(os.path.join(self.resources_path, 'latexdb', 'commands', 'general.xml'))
        root = tree.getroot()
        for child in root:
            attrib = child.attrib
            commands[attrib['name']] = {'command': attrib['text'], 'description': attrib['description']}
        return commands



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
import re
import time
import xml.etree.ElementTree as ET

import setzer.helpers.path as path_helpers
import setzer.helpers.timer as timer


class AutocompleteProvider(object):

    def __init__(self, resources_path, workspace, latex_parser_regex, bibtex_parser_regex, packages_dict):
        self.workspace = workspace
        self.resources_path = resources_path
        self.latex_parser_regex = latex_parser_regex
        self.bibtex_parser_regex = bibtex_parser_regex
        self.packages_dict = packages_dict

        self.static_proposals = dict()
        self.static_begin_end_proposals = dict()
        self.dynamic_word_beginnings = list()
        self.begin_end_commands = dict()
        self.included_files_labels = dict()

        self.ref_types = dict()
        self.ref_types['references'] = list()
        self.ref_types['references'].append(('\\ref', _('Reference to \'{label}\''), _('Reference')))
        self.ref_types['references'].append(('\\pageref', _('Reference to page of \'{label}\''), _('Page reference')))
        self.ref_types['references'].append(('\\eqref', _('Reference to \'{label}\', with parantheses'), _('Reference with parantheses')))
        self.ref_types['citations'] = list()
        self.ref_types['citations'].append(('\\cite', _('Cite \'{label}\''), _('Citation')))
        self.ref_types['citations'].append(('\\citet', _('Cite \'{label}\' (abbreviated)'), _('Citation (abbreviated)')))
        self.ref_types['citations'].append(('\\citep', _('Cite \'{label}\' (abbreviated with brackets)'), _('Citation (abbreviated with brackets)')))
        self.ref_types['citations'].append(('\\citet*', _('Cite \'{label}\' (detailed)'), _('Citation (detailed)')))
        self.ref_types['citations'].append(('\\citep*', _('Cite \'{label}\' (detailed with brackets)'), _('Citation (detailed with brackets)')))
        self.ref_types['citations'].append(('\\citealt', _('Cite \'{label}\' (alternative style 1)'), _('Citation (alternative style 1)')))
        self.ref_types['citations'].append(('\\citealp', _('Cite \'{label}\' (alternative style 2)'), _('Citation (alternative style 2)')))
        self.ref_types['citations'].append(('\\citeauthor', _('Cite \'{label}\' (author)'), _('Citation (author)')))
        self.ref_types['citations'].append(('\\citeauthor*', _('Cite \'{label}\' (author detailed)'), _('Citation (author detailed)')))
        self.ref_types['citations'].append(('\\citeyear', _('Cite \'{label}\' (year)'), _('Citation (year)')))
        self.ref_types['citations'].append(('\\citeyearpar', _('Cite \'{label}\' (year with brackets)'), _('Citation (year with brackets)')))
        self.ref_types['citations'].append(('\\textcite', _('Cite \'{label}\' (BibLaTeX)'), _('BibLaTeX citation')))
        self.ref_types['citations'].append(('\\parencite', _('Cite \'{label}\' (BibLaTeX, with brackets)'), _('BibLaTeX citation (with brackets)')))
        self.ref_types['citations'].append(('\\autocite', _('Cite \'{label}\' (BibLaTeX)'), _('BibLaTeX citation')))
        self.ref_types['usepackage'] = list()
        self.ref_types['usepackage'].append(('\\usepackage',))

        self.last_command = None
        self.last_dynamic_proposals = list()

        self.generate_dynamic_word_beginnings()
        self.generate_static_proposals()
        self.generate_static_begin_end_proposals()
        self.parse_included_files()
        GObject.timeout_add(2000, self.parse_included_files)

    def get_items_for_completion_window(self, current_word, last_tabbed_command=None):
        items = list()

        items_all = self.get_items(current_word)

        if len(items_all) != 1 or current_word.lower() != items_all[0]['command']:
            count = 0
            items_rest = list()
            for item in items_all:
                if last_tabbed_command != None and last_tabbed_command == item['command']:
                    items.insert(0, item)
                    count += 1
                elif item['command'][:len(current_word)] == current_word:
                    items.append(item)
                    count += 1
                else:
                    items_rest.append(item)
            if count >= 20:
                items = items[:20]
            items = items + items_rest[:20 - count]

        return items

    def get_begin_end_items(self, word, last_tabbed_command=None):
        try: items_all = self.static_begin_end_proposals[word.lower()]
        except KeyError: items = list()
        else:
            items = list()
            for item in items_all:
                if last_tabbed_command != None and last_tabbed_command == item['command']:
                    items.insert(0, item)
                else:
                    items.append(item)
        return items

    #@timer.timer
    def get_items(self, word):
        items = list()
        try: static_items = self.static_proposals[word.lower()]
        except KeyError: static_items = list()
        dynamic_items = self.get_dynamic_items(word)
        add_dynamic = True
        for item in static_items:
            if add_dynamic and len(dynamic_items) > 0 and dynamic_items[0]['command'].lower() < item['command'].lower():
                add_dynamic = False
                items += dynamic_items
            if not item['lowpriority']:
                items.append(item)
        if add_dynamic:
            items += dynamic_items
        for item in static_items:
            if item['lowpriority']:
                items.append(item)
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
            elif word_beginning in self.dynamic_word_beginnings['usepackage']:
                dynamic_items += self.get_dynamic_usepackage_commands(word)

            self.last_command = word
            self.last_dynamic_proposals = dynamic_items
        return dynamic_items

    def get_dynamic_reference_commands(self, word):
        ref_types = self.ref_types['references']

        dynamic_items = list()
        labels = self.get_labels_for_dynamic_items()

        for ref_type in ref_types:
            if len(dynamic_items) >= 20: break
            self.append_to_dynamic_items(word, dynamic_items, ref_type, labels, 'label')
        return dynamic_items

    def get_dynamic_bibliography_commands(self, word):
        ref_types = self.ref_types['citations']

        dynamic_items = list()
        labels = self.get_bibitems_for_dynamic_items()

        for ref_type in ref_types:
            if len(dynamic_items) >= 20: break
            self.append_to_dynamic_items(word, dynamic_items, ref_type, labels, 'keylist')
        return dynamic_items

    def get_dynamic_usepackage_commands(self, word):
        dynamic_items = list()
        for package in self.packages_dict.values():
            if len(dynamic_items) >= 20: break

            description = ''
            command = {'command': '\\usepackage' + '{' + package['command'] + '}', 'description': package['description'], 'dotlabels': ''}
            if command['command'][:len(word)] == word.lower():
                if command['command'] not in [item['command'] for item in dynamic_items]:
                    dynamic_items.append(command)
        return dynamic_items

    #@timer.timer
    def get_bibitems_for_dynamic_items(self):
        bibitems_first = set()
        bibitems_second = set()
        bibitems_rest = set()

        pathnames_done = set()
        if self.workspace.active_document != None:
            pathnames_done = pathnames_done | {self.workspace.active_document.get_filename()}
            bibitems_first = bibitems_first | self.workspace.active_document.get_bibitems()

            included_files = self.get_included_files(self.workspace.active_document)
            for pathname in included_files:
                if pathname not in pathnames_done:
                    pathnames_done = pathnames_done | {pathname}
                    if pathname in self.included_files_labels:
                        labels_dict = self.included_files_labels[pathname]['labels']
                        if 'bibitems' in labels_dict:
                            bibitems_second = bibitems_second | labels_dict['bibitems']
                    else:
                        document_object = self.workspace.get_document_by_filename(pathname)
                        if document_object:
                            bibitems_second = bibitems_second | document_object.get_bibitems()

        for document in self.workspace.open_documents:
            pathnames = {document.get_filename()} | self.get_included_files(document)
            for pathname in pathnames:
                if pathname not in pathnames_done:
                    pathnames_done = pathnames_done | {pathname}
                    if pathname in self.included_files_labels:
                        labels_dict = self.included_files_labels[pathname]['labels']
                        if 'bibitems' in labels_dict:
                            bibitems_rest = bibitems_rest | labels_dict['bibitems']
                    else:
                        document_object = self.workspace.get_document_by_filename(pathname)
                        if document_object:
                            bibitems_rest = bibitems_rest | document_object.get_bibitems()

        bibitems = ['•'] + list(bibitems_first) + list(bibitems_second) + list(bibitems_rest)
        return bibitems

    def get_labels_for_dynamic_items(self):
        labels_first = set()
        labels_second = set()
        labels_rest = set()

        pathnames_done = set()
        if self.workspace.active_document != None:
            pathnames_done = pathnames_done | {self.workspace.active_document.get_filename()}
            labels_first = labels_first | self.workspace.active_document.get_labels()

            included_files = self.get_included_files(self.workspace.active_document)
            for pathname in included_files:
                if pathname not in pathnames_done:
                    pathnames_done = pathnames_done | {pathname}
                    if pathname in self.included_files_labels:
                        labels_dict = self.included_files_labels[pathname]['labels']
                        if 'labels' in labels_dict:
                            labels_second = labels_second | labels_dict['labels']
                    else:
                        document_object = self.workspace.get_document_by_filename(pathname)
                        if document_object:
                            labels_second = labels_second | document_object.get_labels()

        for document in self.workspace.open_documents:
            pathnames = {document.get_filename()} | self.get_included_files(document)
            for pathname in pathnames:
                if pathname not in pathnames_done:
                    pathnames_done = pathnames_done | {pathname}
                    if pathname in self.included_files_labels:
                        labels_dict = self.included_files_labels[pathname]['labels']
                        if 'labels' in labels_dict:
                            labels_rest = labels_rest | labels_dict['labels']
                    else:
                        document_object = self.workspace.get_document_by_filename(pathname)
                        if document_object:
                            labels_rest = labels_rest | document_object.get_labels()

        labels = ['•'] + list(labels_first) + list(labels_second) + list(labels_rest)
        return labels

    def append_to_dynamic_items(self, word, items, ref_type, labels, parlabel):
        for label in iter(labels):
            if len(items) >= 20: break

            if label == '•':
                description = ref_type[2]
                dotlabels = parlabel
            else:
                description = ref_type[1].format(label=label)
                dotlabels = ''
            command = {'command': ref_type[0] + '{' + label + '}', 'description': description, 'dotlabels': dotlabels}
            if command['command'][:len(word)] == word.lower():
                if command['command'] not in [item['command'] for item in items]:
                    items.append(command)

    def parse_included_files(self):
        current_includes = set()
        open_docs_pathnames = self.workspace.get_open_documents_filenames()
        for document in self.workspace.open_latex_documents:
            current_includes = current_includes | self.get_included_files(document)
            for pathname in self.get_bibliography_files(document):
                if pathname not in open_docs_pathnames:
                    if os.path.isfile(pathname):
                        if pathname not in self.included_files_labels:
                            self.included_files_labels[pathname] = self.parse_bibtex_file(pathname)
                        else:
                            last_parse_time = self.included_files_labels[pathname]['last_parse_time']
                            if last_parse_time < os.path.getmtime(pathname):
                                self.included_files_labels[pathname] = self.parse_bibtex_file(pathname)
            for pathname in self.get_included_latex_files(document):
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

    def get_included_files(self, document):
        return self.get_included_latex_files(document) | self.get_bibliography_files(document)

    def get_included_latex_files(self, document):
        dirname = document.get_dirname()

        filenames = set()
        if document.get_included_latex_files():
            for filename, offset in document.get_included_latex_files():
                filenames |= {path_helpers.get_abspath(filename, dirname)}

        return filenames

    def get_bibliography_files(self, document):
        dirname = document.get_dirname()

        filenames = set()
        for filename in document.get_bibliography_files():
            filenames |= {path_helpers.get_abspath(filename, dirname)}

        return filenames

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
                for i in range(2, len(command) + 1):
                    self.dynamic_word_beginnings[ref_types_type].append(command[:i])

    def generate_static_begin_end_proposals(self):
        commands = self.begin_end_commands
        self.static_begin_end_proposals = dict()
        for command in commands.values():
            for i in range(1, len(command['command']) + 1):
                try:
                    if len(self.static_begin_end_proposals[command['command'][0:i].lower()]) < 20:
                        self.static_begin_end_proposals[command['command'][0:i].lower()].append(command)
                except KeyError:
                    self.static_begin_end_proposals[command['command'][0:i].lower()] = [command]

    #@timer.timer
    def generate_static_proposals(self):
        commands = self.get_commands()
        self.static_proposals = dict()
        for command in commands.values():
            if not command['lowpriority']:
                for i in range(2, len(command['command']) + 1):
                    try:
                        if len(self.static_proposals[command['command'][0:i].lower()]) < 20:
                            self.static_proposals[command['command'][0:i].lower()].append(command)
                    except KeyError:
                        self.static_proposals[command['command'][0:i].lower()] = [command]
        for command in commands.values():
            if command['lowpriority']:
                for i in range(2, len(command['command']) + 1):
                    try:
                        if len(self.static_proposals[command['command'][0:i].lower()]) < 20:
                            self.static_proposals[command['command'][0:i].lower()].append(command)
                    except KeyError:
                        self.static_proposals[command['command'][0:i].lower()] = [command]

    #@timer.timer
    def get_commands(self):
        commands = dict()
        for filename in ['additional.xml', 'latex-document.xml', 'tex.xml', 'textcomp.xml', 'graphicx.xml', 'latex-dev.xml', 'amsmath.xml', 'amsopn.xml', 'amsbsy.xml', 'amsfonts.xml', 'amssymb.xml', 'amsthm.xml', 'color.xml', 'url.xml', 'geometry.xml', 'glossaries.xml', 'beamer.xml']:
            tree = ET.parse(os.path.join(self.resources_path, 'latexdb', 'commands', filename))
            root = tree.getroot()
            for child in root:
                attrib = child.attrib
                commands[attrib['name']] = {'command': attrib['text'], 'description': attrib['description'], 'lowpriority': True if attrib['lowpriority'] == "True" else False, 'dotlabels': attrib['dotlabels']}
                match = re.match(r'\\begin\{([^\}]+)\}', attrib['name'])
                if match:
                    name = match.group(1)
                    self.begin_end_commands[name] = {'command': name, 'description': '', 'lowpriority': False, 'dotlabels': ''}
        return commands



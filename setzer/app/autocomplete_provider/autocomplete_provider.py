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

        self.ref_types = dict()
        self.ref_types['references'] = list()
        self.ref_types['references'].append(('ref', _('Reference to \'{label}\'')))
        self.ref_types['references'].append(('pageref', _('Reference to page of \'{label}\'')))
        self.ref_types['references'].append(('eqref', _('Reference to \'{label}\', with parantheses')))
        self.ref_types['citations'] = list()
        self.ref_types['citations'].append(('cite', _('Cite \'{label}\'')))
        self.ref_types['citations'].append(('citet', _('Cite \'{label}\' (abbreviated)')))
        self.ref_types['citations'].append(('citep', _('Cite \'{label}\' (abbreviated with brackets)')))
        self.ref_types['citations'].append(('citet*', _('Cite \'{label}\' (detailed)')))
        self.ref_types['citations'].append(('citep*', _('Cite \'{label}\' (detailed with brackets)')))
        self.ref_types['citations'].append(('citealt', _('Cite \'{label}\' (alternative style 1)')))
        self.ref_types['citations'].append(('citealp', _('Cite \'{label}\' (alternative style 2)')))
        self.ref_types['citations'].append(('citeauthor', _('Cite \'{label}\' (author)')))
        self.ref_types['citations'].append(('citeauthor*', _('Cite \'{label}\' (author detailed)')))
        self.ref_types['citations'].append(('citeyear', _('Cite \'{label}\' (year)')))
        self.ref_types['citations'].append(('citeyearpar', _('Cite \'{label}\' (year with brackets)')))

        self.last_command = None
        self.last_dynamic_proposals = list()

        self.generate_dynamic_word_beginnings()
        self.generate_static_proposals()

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
        try: items = self.static_proposals[word[1:].lower()]
        except KeyError: pass
        dynamic_items = self.get_dynamic_items(word)
        return dynamic_items + items

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

    #@timer.timer
    def get_dynamic_reference_commands(self, word):
        ref_types = self.ref_types['references']

        dynamic_items = list()
        documents = self.get_documents_for_dynamic_items()

        for ref_type in ref_types:
            if len(dynamic_items) >= 5: break

            for document in documents:
                if len(dynamic_items) >= 5: break
                labels_dict = document.parser.get_labels()
                if 'labels' in labels_dict:
                    labels = ['•'] + list(labels_dict['labels'])
                else:
                    labels = ['•']
                self.append_to_dynamic_items(word, dynamic_items, ref_type, labels, document)
        return dynamic_items

    def get_dynamic_bibliography_commands(self, word):
        ref_types = self.ref_types['citations']

        dynamic_items = list()
        documents = self.get_documents_for_dynamic_items()

        for ref_type in ref_types:
            if len(dynamic_items) >= 5: break

            for document in documents:
                if len(dynamic_items) >= 5: break
                labels_dict = document.parser.get_labels()
                if 'bibitems' in labels_dict:
                    labels = ['•'] + list(labels_dict['bibitems'])
                else:
                    labels = ['•']
                self.append_to_dynamic_items(word, dynamic_items, ref_type, labels, document)
        return dynamic_items

    def append_to_dynamic_items(self, word, items, ref_type, labels, document):
        for label in iter(labels):
            if len(items) >= 5: break

            command = {'command': ref_type[0] + '{' + label + '}', 'description': ref_type[1].format(label=label)}
            if command['command'][:len(word) - 1] == word[1:].lower():
                if command['command'] not in [item['command'] for item in items]:
                    items.append(command)

    def get_documents_for_dynamic_items(self):
        documents = list()
        if self.workspace.active_document != None:
            documents.append(self.workspace.active_document)
            for document in self.workspace.open_documents:
                if self.workspace.active_document.is_latex_document() and document not in documents and document.filename in self.workspace.active_document.get_included_files():
                    documents.append(document)
            for document in self.workspace.open_documents:
                if document not in documents:
                    documents.append(document)
        return documents

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
        self.dynamic_word_beginnings = dict()
        for ref_types_type in self.ref_types:
            self.dynamic_word_beginnings[ref_types_type] = list()
            for command in self.ref_types[ref_types_type]:
                command = command[0] + '{'
                for i in range(1, len(command) + 1):
                    self.dynamic_word_beginnings[ref_types_type].append('\\' + command[:i])



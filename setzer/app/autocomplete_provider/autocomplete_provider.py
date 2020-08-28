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


class AutocompleteProvider(object):

    def __init__(self, resources_path, workspace):
        self.workspace = workspace
        self.resources_path = resources_path

        self.static_proposals = dict()
        self.dynamic_proposals = dict()

        self.generate_static_proposals()
        GObject.timeout_add(500, self.generate_dynamic_proposals)

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
        try: items = self.static_proposals[word[1:].lower()]
        except KeyError: pass
        try: dynamic_items = self.dynamic_proposals[word[1:].lower()]
        except KeyError: dynamic_items = list()
        return items + dynamic_items

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

    def generate_dynamic_proposals(self):
        for document in self.workspace.open_documents:
            if document.is_latex_document():
                labels = document.parser.get_labels()
                if labels != None:
                    self.dynamic_proposals = dict()
                    for label in iter(labels):
                        command = {'command': 'ref{' + label + '}', 'description': _('Reference to \'{label}\'').format(label=label)}
                        for i in range(1, len(command['command']) + 1):
                            try:
                                if len(self.dynamic_proposals[command['command'][0:i].lower()]) < 5:
                                    self.dynamic_proposals[command['command'][0:i].lower()].append(command)
                            except KeyError:
                                self.dynamic_proposals[command['command'][0:i].lower()] = [command]
        return True

    def get_commands(self):
        commands = dict()
        tree = ET.parse(os.path.join(self.resources_path, 'latexdb', 'commands', 'general.xml'))
        root = tree.getroot()
        for child in root:
            attrib = child.attrib
            commands[attrib['name']] = {'command': attrib['text'], 'description': attrib['description']}
        return commands



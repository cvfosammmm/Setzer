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
from gi.repository import GObject

import os.path, re, time, bibtexparser
import xml.etree.ElementTree as ET

import setzer.helpers.path as path_helpers
from setzer.app.service_locator import ServiceLocator


class LaTeXDB():

    static_proposals = dict()
    resources_path = None
    dynamic_commands = dict()
    dynamic_commands['references'] = ['\\ref*', '\\ref', '\\pageref*', '\\pageref', '\\eqref']
    dynamic_commands['citations'] = ['\\citet*', '\\citet', '\\citep*', '\\citep', '\\citealt', '\\citealp', '\\citeauthor*', '\\citeauthor', '\\citeyearpar', '\\citeyear', '\\textcite', '\\parencite', '\\autocite', '\\cite']
    files = dict()
    languages_dict = None
    packages_dict = None

    def init(resources_path):
        LaTeXDB.resources_path = resources_path
        LaTeXDB.generate_static_proposals()
        LaTeXDB.parse_included_files()
        GObject.timeout_add(3000, LaTeXDB.parse_included_files)

    def get_items(word, top_item=None):
        try: static_items = LaTeXDB.static_proposals[word.lower()]
        except KeyError: static_items = list()
        dynamic_items = LaTeXDB.get_dynamic_proposals(word.lower())
        if len(static_items) > 0 and len(dynamic_items) > 4:
            items = dynamic_items[:5] + static_items + dynamic_items[5:]
        else:
            items = dynamic_items + static_items

        if top_item == None: return items
        result = []
        for item in items:
            if item['command'] == top_item:
                result.insert(0, item)
            else:
                result.append(item)
        return result

    def generate_static_proposals():
        commands = LaTeXDB.get_commands()
        LaTeXDB.static_proposals = dict()
        for command in commands.values():
            if not command['lowpriority']:
                for i in range(2, len(command['command']) + 1):
                    if not command['command'][0:i].lower() in LaTeXDB.static_proposals:
                        LaTeXDB.static_proposals[command['command'][0:i].lower()] = []
                    if len(LaTeXDB.static_proposals[command['command'][0:i].lower()]) < 20:
                        LaTeXDB.static_proposals[command['command'][0:i].lower()].append(command)
        for command in commands.values():
            if command['lowpriority']:
                for i in range(2, len(command['command']) + 1):
                    if not command['command'][0:i].lower() in LaTeXDB.static_proposals:
                        LaTeXDB.static_proposals[command['command'][0:i].lower()] = []
                    if len(LaTeXDB.static_proposals[command['command'][0:i].lower()]) < 20:
                        LaTeXDB.static_proposals[command['command'][0:i].lower()].append(command)

    def get_commands():
        commands = dict()
        for filename in ['additional.xml', 'latex-document.xml', 'dynamic.xml', 'tex.xml', 'textcomp.xml', 'graphicx.xml', 'latex-dev.xml', 'amsmath.xml', 'amsopn.xml', 'amsbsy.xml', 'amsfonts.xml', 'amssymb.xml', 'amsthm.xml', 'color.xml', 'url.xml', 'geometry.xml', 'glossaries.xml', 'beamer.xml', 'hyperref.xml']:
            tree = ET.parse(os.path.join(LaTeXDB.resources_path, 'latexdb', 'commands', filename))
            root = tree.getroot()
            for child in root:
                attrib = child.attrib
                commands[attrib['name']] = {'command': attrib['text'], 'description': _(attrib['description']), 'lowpriority': True if attrib['lowpriority'] == "True" else False, 'dotlabels': attrib['dotlabels']}
        return commands

    def get_dynamic_proposals(word):
        documents = []

        ref_regex = '(' + re.escape('|'.join(LaTeXDB.dynamic_commands['references'])).replace('\\|', '|') + ')'
        cite_regex = '(' + re.escape('|'.join(LaTeXDB.dynamic_commands['citations'])).replace('\\|', '|') + ')'
        matchings = dict()
        matchings['labels'] = ServiceLocator.get_regex_object(ref_regex).match(word)
        matchings['bibitems'] = ServiceLocator.get_regex_object(cite_regex).match(word)
        key = 'labels' if matchings['labels'] != None else 'bibitems'
        if matchings['labels'] == None and matchings['bibitems'] == None: return list()

        commands = list()
        for file in LaTeXDB.files.values():
            for value in file[key]:
                command = matchings[key].group(1) + '{' + value + '}'
                if command.startswith(word):
                    commands.append({'command': command, 'description': '', 'lowpriority': False, 'dotlabels': ''})
        return commands

    def parse_included_files():
        workspace = ServiceLocator.get_workspace()
        if workspace == None: return

        def get_file_dict(filename):
            if filename in LaTeXDB.files:
                return LaTeXDB.files[filename]
            else:
                return {'last_parse': -1, 'bibitems': list(), 'labels': list(), 'includes': list()}

        files = dict()
        for document in ServiceLocator.get_workspace().open_documents:
            if document.get_filename() != None:
                files[document.get_filename()] = get_file_dict(document.get_filename())
                files[document.get_filename()]['includes'] = list()

                dirname = document.get_dirname()
                for filename, offset in document.parser.symbols['included_latex_files']:
                    filename = path_helpers.get_abspath(filename, dirname)
                    files[document.get_filename()]['includes'].append(filename)
                    files[filename] = get_file_dict(filename)
                for filename in document.parser.symbols['bibliographies']:
                    filename = path_helpers.get_abspath(filename, dirname)
                    files[document.get_filename()]['includes'].append(filename)
                    files[filename] = get_file_dict(filename)
        LaTeXDB.files = files

        for filename, file_dict in LaTeXDB.files.items():
            if os.path.isfile(filename):
                last_modified = os.path.getmtime(filename)
                if file_dict['last_parse'] < last_modified:
                    if filename.endswith('.tex'):
                        LaTeXDB.parse_latex_file(filename)
                    elif filename.endswith('.bib'):
                        LaTeXDB.parse_bibtex_file(filename)
                    LaTeXDB.files[filename]['last_parse'] = time.time()

        return True

    def parse_latex_file(pathname):
        with open(pathname, 'r') as f:
            text = f.read()
        labels = set()
        bibitems = set()
        latex_parser_regex = ServiceLocator.get_regex_object(r'\\(label|include|input|bibliography|addbibresource)\{((?:\s|\w|\:|\.|,)*)\}|\\(usepackage)(?:\[.*\]){0,1}\{((?:\s|\w|\:|,)*)\}|\\(bibitem)(?:\[.*\]){0,1}\{((?:\s|\w|\:)*)\}')
        for match in latex_parser_regex.finditer(text):
            if match.group(1) == 'label':
                labels = labels | {match.group(2).strip()}
            elif match.group(5) == 'bibitem':
                bibitems = bibitems | {match.group(6).strip()}

        LaTeXDB.files[pathname]['bibitems'] = bibitems
        LaTeXDB.files[pathname]['labels'] = labels

    def parse_bibtex_file(pathname):
        with open(pathname, 'r') as f:
            db = bibtexparser.load(f)
        bibitems = set()
        for match in db.entries:
            bibitems = bibitems | {match['ID']}

        LaTeXDB.files[pathname]['bibitems'] = bibitems

    def get_languages_dict():
        if LaTeXDB.languages_dict == None:
            LaTeXDB.languages_dict = dict()

            resources_path = ServiceLocator.get_resources_path()
            tree = ET.parse(os.path.join(resources_path, 'latexdb', 'languages', 'languages.xml'))
            root = tree.getroot()
            for child in root:
                attrib = child.attrib
                LaTeXDB.languages_dict[attrib['code']] = _(attrib['name'])

        return LaTeXDB.languages_dict

    def get_packages_dict():
        if LaTeXDB.packages_dict == None:
            LaTeXDB.packages_dict = dict()

            resources_path = ServiceLocator.get_resources_path()
            tree = ET.parse(os.path.join(resources_path, 'latexdb', 'packages', 'general.xml'))
            root = tree.getroot()
            for child in root:
                attrib = child.attrib
                LaTeXDB.packages_dict[attrib['name']] = {'command': attrib['text'], 'description': _(attrib['description'])}
        return LaTeXDB.packages_dict



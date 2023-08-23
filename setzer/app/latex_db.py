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

import os.path
import re
import xml.etree.ElementTree as ET


class LaTeXDB(object):

    static_proposals = dict()
    resources_path = None

    def init(resources_path):
        LaTeXDB.resources_path = resources_path
        LaTeXDB.generate_static_proposals()

    def get_items(word):
        try: items = LaTeXDB.static_proposals[word.lower()]
        except KeyError: items = list()

        return items

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
        for filename in ['additional.xml', 'latex-document.xml', 'tex.xml', 'textcomp.xml', 'graphicx.xml', 'latex-dev.xml', 'amsmath.xml', 'amsopn.xml', 'amsbsy.xml', 'amsfonts.xml', 'amssymb.xml', 'amsthm.xml', 'color.xml', 'url.xml', 'geometry.xml', 'glossaries.xml', 'beamer.xml', 'hyperref.xml']:
            tree = ET.parse(os.path.join(LaTeXDB.resources_path, 'latexdb', 'commands', filename))
            root = tree.getroot()
            for child in root:
                attrib = child.attrib
                commands[attrib['name']] = {'command': attrib['text'], 'description': _(attrib['description']), 'lowpriority': True if attrib['lowpriority'] == "True" else False, 'dotlabels': attrib['dotlabels']}
        return commands



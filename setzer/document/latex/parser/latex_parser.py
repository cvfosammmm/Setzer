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

import os.path

from setzer.app.service_locator import ServiceLocator
from setzer.helpers.timer import timer


class LaTeXParser(object):

    def __init__(self, document):
        self.document = document
        self.dirname = self.document.get_dirname()
        self.text = ''

        self.document.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'text_inserted':
            self.on_text_inserted(parameter)

        if change_code == 'text_deleted':
            self.on_text_deleted(parameter)

    #@timer
    def on_text_deleted(self, parameter):
        buffer, start_iter, end_iter = parameter
        start_offset = start_iter.get_offset()
        end_offset = end_iter.get_offset()
        self.text = self.text[:start_offset] + self.text[end_offset:]
        self.parse()

    #@timer
    def on_text_inserted(self, parameter):
        buffer, location_iter, text, text_length = parameter
        offset = location_iter.get_offset()
        self.text = self.text[:offset] + text + self.text[offset:]
        self.parse()

    #@timer
    def parse(self):
        self.dirname = self.document.get_dirname()
        self.parse_symbols(self.text)
        self.parse_blocks(self.text)

    #@timer
    def parse_blocks(self, text):
        text_length = len(text)

        matches = {'begin_or_end': list(), 'others': list()}
        for match in ServiceLocator.get_regex_object(r'\\(begin|end)\{((?:\w|•)+(?:\*){0,1})\}|\\(part|chapter|section|subsection|subsubsection)(?:\*){0,1}\{').finditer(text):
            if match.group(1) != None:
                matches['begin_or_end'].append(match)
            else:
                matches['others'].append(match)

        blocks = dict()

        end_document_offset = None
        for match in matches['begin_or_end']:
            if match.group(1) == 'begin':
                try: blocks[match.group(2)].append([match.start(), None])
                except KeyError: blocks[match.group(2)] = [[match.start(), None]]
            else:
                if match.group(2).strip() == 'document':
                    end_document_offset = match.start()
                try: begins = blocks[match.group(2)]
                except KeyError: pass
                else:
                    for block in reversed(begins):
                        if block[1] == None:
                            block[1] = match.start()
                            break

        blocks_list = list()
        for single_list in blocks.values():
            blocks_list += single_list

        blocks = [list(), list(), list(), list(), list()]
        relevant_following_blocks = [list(), list(), list(), list(), list()]
        levels = {'part': 0, 'chapter': 1, 'section': 2, 'subsection': 3, 'subsubsection': 4}
        for match in reversed(matches['others']):
            level = levels[match.group(3)]
            block = [match.start(), None]

            if len(relevant_following_blocks[level]) >= 1:
                # - 1 to go one line up
                block[1] = relevant_following_blocks[level][-1][0] - 1
            else:
                if end_document_offset != None and block[0] < end_document_offset:
                    # - 1 to go one line up
                    block[1] = end_document_offset - 1
                else:
                    block[1] = text_length

            blocks[level].append(block)
            for i in range(level, 5):
                relevant_following_blocks[i].append(block)

        for single_list in blocks:
            blocks_list += single_list

        self.document.symbols['blocks'] = sorted(blocks_list, key=lambda block: block[0])

    #@timer
    def parse_symbols(self, text):
        labels = set()
        included_latex_files = set()
        bibliographies = set()
        bibitems = set()
        packages = set()
        packages_detailed = dict()
        for match in ServiceLocator.get_regex_object(r'\\(label|include|input|bibliography|addbibresource)\{((?:\s|\w|\:|\.|,)*)\}|\\(usepackage)(?:\[[^\{\[]*\]){0,1}\{((?:\s|\w|\:|,)*)\}|\\(bibitem)(?:\[.*\]){0,1}\{((?:\s|\w|\:)*)\}').finditer(text):
            if match.group(1) == 'label':
                labels = labels | {match.group(2).strip()}
            elif match.group(1) == 'include' or match.group(1) == 'input':
                filename = os.path.normpath(os.path.join(self.dirname, match.group(2).strip()))
                if not filename.endswith('.tex'):
                    filename += '.tex'
                included_latex_files = included_latex_files | {filename}
            elif match.group(1) == 'bibliography':
                bibfiles = match.group(2).strip().split(',')
                for entry in bibfiles:
                    bibliographies = bibliographies | {os.path.normpath(os.path.join(self.dirname, entry.strip() + '.bib'))}
            elif match.group(1) == 'addbibresource':
                bibfiles = match.group(2).strip().split(',')
                for entry in bibfiles:
                    bibliographies = bibliographies | {os.path.normpath(os.path.join(self.dirname, entry.strip()))}
            elif match.group(3) == 'usepackage':
                packages = packages | {match.group(4).strip()}
                packages_detailed[match.group(4).strip()] = match
            elif match.group(5) == 'bibitem':
                bibitems = bibitems | {match.group(6).strip()}

        self.document.symbols['labels'] = labels
        self.document.symbols['included_latex_files'] = included_latex_files
        self.document.symbols['bibliographies'] = bibliographies
        self.document.symbols['bibitems'] = bibitems
        self.document.symbols['packages'] = packages
        self.document.symbols['packages_detailed'] = packages_detailed



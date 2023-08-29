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

from setzer.app.service_locator import ServiceLocator
from setzer.helpers.observable import Observable
from setzer.helpers.timer import timer


class ParserLaTeX(Observable):

    def __init__(self, document):
        Observable.__init__(self)
        self.document = document
        self.text_length = 0
        self.number_of_lines = 0
        self.block_symbol_matches = {'begin_or_end': list(), 'others': list()}
        self.other_symbols = list()

        self.symbols = dict()
        self.symbols['bibitems'] = set()
        self.symbols['labels'] = set()
        self.symbols['labels_with_offset'] = list()
        self.symbols['todos'] = set()
        self.symbols['todos_with_offset'] = set()
        self.symbols['included_latex_files'] = set()
        self.symbols['bibliographies'] = set()
        self.symbols['packages'] = set()
        self.symbols['packages_detailed'] = dict()
        self.symbols['blocks'] = list()

        self.last_edit = None

        self.document.source_buffer.connect('insert-text', self.on_insert_text)
        self.document.source_buffer.connect('delete-range', self.on_text_deleted)

    #@timer
    def on_text_deleted(self, buffer, start_iter, end_iter):
        self.last_edit = ('delete', start_iter, end_iter)

        offset_start = start_iter.get_offset()
        offset_end = end_iter.get_offset()
        line_start = start_iter.get_line()
        line_end = end_iter.get_line()
        char_count = buffer.get_char_count()
        _, before_iter = buffer.get_iter_at_line(line_start)
        _, after_iter = buffer.get_iter_at_line(line_end + 1)
        if not after_iter.get_offset() == char_count:
            after_iter.backward_char()

        text_length = offset_end - offset_start
        text = buffer.get_text(start_iter, end_iter, True)
        deleted_line_count = text.count('\n')
        text_before = buffer.get_text(before_iter, start_iter, True)
        text_after = buffer.get_text(end_iter, after_iter, True)
        offset_line_start = before_iter.get_offset()
        self.text_length = char_count - offset_end + offset_start

        block_symbol_matches = {'begin_or_end': list(), 'others': list()}
        for match in self.block_symbol_matches['begin_or_end']:
            if match[1] < line_start:
                block_symbol_matches['begin_or_end'].append(match)
        for match in self.block_symbol_matches['others']:
            if match[1] < line_start:
                block_symbol_matches['others'].append(match)
        other_symbols = list()
        for match in self.other_symbols:
            if match[1] < offset_line_start:
                other_symbols.append((match[0], match[1]))

        offset_line_end = offset_end + len(text_after)
        text = text_before + text_after

        additional_matches = self.parse_for_blocks(text, line_start, offset_line_start)
        block_symbol_matches['begin_or_end'] += additional_matches['begin_or_end']
        block_symbol_matches['others'] += additional_matches['others']
        for match in ServiceLocator.get_regex_object(r'\\(label|include|input|subfile|subimport|bibliography|addbibresource|todo)(?:\[[^\{\[]*\]){0,1}\{((?:\s|\w|\:|\.|,|\/|\\|\'|-|\"|\(|\))*)\}|\\(usepackage)(?:\[[^\{\[]*\]){0,1}\{((?:\s|\w|\:|,)*)\}|\\(bibitem)(?:\[.*\]){0,1}\{((?:\s|\w|\:)*)\}').finditer(text):
            other_symbols.append((match, match.start() + offset_line_start))

        for match in self.block_symbol_matches['begin_or_end']:
            if match[1] > line_end:
                block_symbol_matches['begin_or_end'].append((match[0], match[1] - deleted_line_count, match[2] - text_length))
        for match in self.block_symbol_matches['others']:
            if match[1] > line_end:
                block_symbol_matches['others'].append((match[0], match[1] - deleted_line_count, match[2] - text_length))
        for match in self.other_symbols:
            if match[1] > offset_line_end:
                other_symbols.append((match[0], match[1] - text_length))

        self.block_symbol_matches = block_symbol_matches
        self.number_of_lines = self.number_of_lines - deleted_line_count
        self.parse_blocks()

        self.other_symbols = other_symbols
        self.parse_symbols()

        self.add_change_code('finished_parsing')

    #@timer
    def on_insert_text(self, buffer, location_iter, text, text_length):
        self.last_edit = ('insert', location_iter, text, text_length)

        text_length = len(text)
        offset = location_iter.get_offset()
        new_line_count = text.count('\n')
        line_start = location_iter.get_line()
        char_count = buffer.get_char_count()
        _, before_iter = buffer.get_iter_at_line(line_start)
        _, after_iter = buffer.get_iter_at_line(line_start + 1)
        if not after_iter.get_offset() == char_count:
            after_iter.backward_char()

        text_before = buffer.get_text(before_iter, location_iter, True)
        offset_line_start = before_iter.get_offset()
        text_after = buffer.get_text(location_iter, after_iter, True)
        offset_line_end = offset + len(text_after)
        self.text_length = char_count + text_length
        text_parse = text_before + text + text_after

        block_symbol_matches = {'begin_or_end': list(), 'others': list()}
        for match in self.block_symbol_matches['begin_or_end']:
            if match[1] < line_start:
                block_symbol_matches['begin_or_end'].append(match)
        for match in self.block_symbol_matches['others']:
            if match[1] < line_start:
                block_symbol_matches['others'].append(match)
        other_symbols = list()
        for match in self.other_symbols:
            if match[1] < offset_line_start:
                other_symbols.append((match[0], match[1]))

        additional_matches = self.parse_for_blocks(text_parse, line_start, offset_line_start)
        block_symbol_matches['begin_or_end'] += additional_matches['begin_or_end']
        block_symbol_matches['others'] += additional_matches['others']
        for match in ServiceLocator.get_regex_object(r'\\(label|include|input|subfile|subimport|bibliography|addbibresource|todo)(?:\[[^\{\[]*\]){0,1}\{((?:\s|\w|\:|\.|,|\/|\\|\'|-|\"|\(|\))*)\}|\\(usepackage)(?:\[[^\{\[]*\]){0,1}\{((?:\s|\w|\:|,)*)\}|\\(bibitem)(?:\[.*\]){0,1}\{((?:\s|\w|\:)*)\}').finditer(text_parse):
            other_symbols.append((match, match.start() + offset_line_start))

        for match in self.block_symbol_matches['begin_or_end']:
            if match[1] > line_start:
                block_symbol_matches['begin_or_end'].append((match[0], match[1] + new_line_count, match[2] + text_length))
        for match in self.block_symbol_matches['others']:
            if match[1] > line_start:
                block_symbol_matches['others'].append((match[0], match[1] + new_line_count, match[2] + text_length))
        for match in self.other_symbols:
            if match[1] > offset_line_end:
                other_symbols.append((match[0], match[1] + text_length))

        self.block_symbol_matches = block_symbol_matches
        self.number_of_lines = self.number_of_lines + new_line_count
        self.parse_blocks()

        self.other_symbols = other_symbols
        self.parse_symbols()

        self.add_change_code('finished_parsing')

    #@timer
    def parse_for_blocks(self, text, line_start, offset_line_start):
        block_symbol_matches = {'begin_or_end': list(), 'others': list()}
        counter = line_start
        for match in ServiceLocator.get_regex_object(r'\n|\\(begin|end)\{((?:\w|•|\*)+)\}|\\(part|chapter|section|subsection|subsubsection|paragraph|subparagraph)(?:\*){0,1}\{([^\{]*)\}').finditer(text):
            if match.group(1) != None:
                block_symbol_matches['begin_or_end'].append((match, counter, match.start() + offset_line_start))
            elif match.group(3) != None:
                block_symbol_matches['others'].append((match, counter, match.start() + offset_line_start))
                counter += len(match.group(0).splitlines()) - 1
            if match.group(0) == '\n':
                counter += 1
        return block_symbol_matches

    #@timer
    def parse_blocks(self):
        blocks = dict()

        add_preamble_folding = True
        end_document_offset = None
        end_document_line = None
        begin_document_offset = None
        begin_document_line = None
        blocks_list = list()
        for (match, line_number, offset) in self.block_symbol_matches['begin_or_end']:
            if line_number == 0:
                add_preamble_folding = False

            if match.group(1) == 'begin':
                if match.group(2).strip() == 'document':
                    begin_document_offset = offset
                    begin_document_line = line_number
                try: blocks[match.group(2)].append([offset, None, line_number, None])
                except KeyError: blocks[match.group(2)] = [[offset, None, line_number, None]]
            else:
                if match.group(2).strip() == 'document':
                    end_document_offset = offset
                    end_document_line = line_number
                try: blocks_begin = blocks[match.group(2)]
                except KeyError: pass
                else:
                    try: block_begin = blocks_begin.pop()
                    except IndexError: pass
                    else:
                        block_begin[1] = offset
                        block_begin[3] = line_number
                        block_begin.append(match.group(2))
                        blocks_list.append(block_begin)

        relevant_following_blocks = [list(), list(), list(), list(), list(), list(), list()]
        levels = {'part': 0, 'chapter': 1, 'section': 2, 'subsection': 3, 'subsubsection': 4, 'paragraph': 5, 'subparagraph': 6}
        for (match, line_number, offset) in reversed(self.block_symbol_matches['others']):
            if line_number == 0:
                add_preamble_folding = False

            level = levels[match.group(3)]
            block = [offset, None, line_number, None]

            if len(relevant_following_blocks[level]) >= 1:
                # - 1 to go one line up
                block[1] = relevant_following_blocks[level][-1][0] - 1
                block[3] = relevant_following_blocks[level][-1][2] - 1
            else:
                if end_document_offset != None and block[0] < end_document_offset:
                    # - 1 to go one line up
                    block[1] = end_document_offset - 1
                    block[3] = end_document_line - 1
                else:
                    block[1] = self.text_length
                    block[3] = self.number_of_lines

            block.append(match.group(3))
            block.append(match.group(4))
            blocks_list.append(block)
            for i in range(level, 7):
                relevant_following_blocks[i].append(block)

        if add_preamble_folding and begin_document_offset and begin_document_line:
            blocks_list.append([0, begin_document_offset - 1, 0, begin_document_line - 1, 'preamble'])

        self.symbols['blocks'] = sorted(blocks_list, key=lambda block: block[0])

    #@timer
    def parse_symbols(self):
        labels = set()
        labels_with_offset = list()
        todos = set()
        todos_with_offset = list()
        included_latex_files = list()
        bibliographies = set()
        bibitems = set()
        packages = set()
        packages_detailed = dict()
        for match in self.other_symbols:
            offset = match[1]
            match = match[0]
            if match.group(1) == 'label':
                labels = labels | {match.group(2).strip()}
                labels_with_offset.append([match.group(2).strip(), offset])
            elif match.group(1) == 'include' or match.group(1) == 'input' or match.group(1) == 'subfile' or match.group(1) == 'subimport':
                filename = match.group(2).strip()
                if not filename.endswith('.tex'):
                    filename += '.tex'
                included_latex_files.append((filename, offset))
            elif match.group(1) == 'bibliography':
                bibfiles = match.group(2).strip().split(',')
                for entry in bibfiles:
                    bibliographies = bibliographies | {entry.strip() + '.bib'}
            elif match.group(1) == 'addbibresource':
                bibfiles = match.group(2).strip().split(',')
                for entry in bibfiles:
                    bibliographies = bibliographies | {entry.strip()}
            elif match.group(1) == 'todo':
                todos = todos | {match.group(2).strip()}
                todos_with_offset.append([match.group(2).strip(), offset])
            elif match.group(3) == 'usepackage':
                packages = packages | {match.group(4).strip()}
                if match.group(4).strip() not in packages_detailed:
                    packages_detailed[match.group(4).strip()] = []
                packages_detailed[match.group(4).strip()].append([offset, match])
            elif match.group(5) == 'bibitem':
                bibitems = bibitems | {match.group(6).strip()}

        self.symbols['labels'] = labels
        self.symbols['labels_with_offset'] = labels_with_offset
        self.symbols['included_latex_files'] = included_latex_files
        self.symbols['todos'] = todos
        self.symbols['todos_with_offset'] = todos_with_offset
        self.symbols['bibliographies'] = bibliographies
        self.symbols['bibitems'] = bibitems
        self.symbols['packages'] = packages
        self.symbols['packages_detailed'] = packages_detailed



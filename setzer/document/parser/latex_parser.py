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
from gi.repository import GObject

from setzer.app.service_locator import ServiceLocator
import _thread as thread, queue
import time


class LaTeXParser(object):

    def __init__(self, document):
        self.document = document

        self.symbols = dict()
        self.symbols['labels'] = set()
        self.symbols['includes'] = set()
        self.symbols['inputs'] = set()
        self.symbols['bibliographies'] = set()
        self.symbols['bibitems'] = set()
        self.symbols['packages'] = set()
        self.symbols['packages_detailed'] = dict()
        self.labels_changed = True
        self.last_result = None
        self.symbols_lock = thread.allocate_lock()

        self.last_buffer_change = time.time()

        self.blocks = list()
        self.blocks_changed = True
        self.last_blocks_change = time.time()
        self.blocks_lock = thread.allocate_lock()

        self.parse_jobs = dict()
        self.parse_jobs['symbols'] = None
        self.parse_jobs['blocks'] = None
        self.parse_symbols_job_running = False
        self.parse_blocks_job_running = False
        self.parse_jobs_lock = thread.allocate_lock()

        GObject.timeout_add(1, self.compute_loop)

    def on_buffer_changed(self):
        self.last_buffer_change = time.time()
        text = self.document.get_text()
        with self.parse_jobs_lock:
            self.parse_jobs['symbols'] = ParseJob(time.time() + 0.1, text)
            self.parse_jobs['blocks'] = ParseJob(time.time(), text)

    def compute_loop(self):
        with self.parse_jobs_lock:
            job = self.parse_jobs['symbols']
        if job != None:
            with self.parse_jobs_lock:
                parse_symbols_job_running = self.parse_symbols_job_running
            if not parse_symbols_job_running and job.starting_time < time.time():
                with self.parse_jobs_lock:
                    self.parse_jobs['symbols'] = None
                thread.start_new_thread(self.parse_symbols, (job.text, ))

        with self.parse_jobs_lock:
            job = self.parse_jobs['blocks']
        if job != None:
            with self.parse_jobs_lock:
                parse_blocks_job_running = self.parse_blocks_job_running
            if not parse_blocks_job_running and job.starting_time < time.time():
                with self.parse_jobs_lock:
                    self.parse_jobs['blocks'] = None
                thread.start_new_thread(self.parse_blocks, (job.text, ))

        return True

    def get_labels(self):
        with self.symbols_lock:
            if self.labels_changed or self.last_result == None:
                result = dict()
                result['labels'] = self.symbols['labels'].copy()
                result['bibitems'] = self.symbols['bibitems'].copy()
                self.last_result = result
            else:
                result = self.last_result
            self.labels_changed = False
        return result

    def get_blocks(self):
        with self.blocks_lock:
            if self.last_buffer_change > self.last_blocks_change:
                result = None
            elif self.blocks_changed:
                result = self.blocks.copy()
            else:
                result = None
            self.blocks_changed = False
        return result

    def parse_blocks(self, text):
        with self.parse_jobs_lock:
            self.parse_blocks_job_running = True

        text_length = len(text)

        matches = {'begin_or_end': list(), 'others': list()}
        for match in ServiceLocator.get_regex_object(r'\n.*\\(begin|end)\{((?:\w)*(?:\*){0,1})\}|\n.*\\(part|chapter|section|subsection|subsubsection)(?:\*){0,1}\{').finditer(text):
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
                block[1] = relevant_following_blocks[level][len(relevant_following_blocks[level]) - 1][0] - 1
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
        blocks_list = sorted(blocks_list, key=lambda block: block[0])

        with self.blocks_lock:
            self.blocks = blocks_list
            self.blocks_changed = True
            self.last_blocks_change = time.time()

        with self.parse_jobs_lock:
            self.parse_blocks_job_running = False

    def parse_symbols(self, text):
        with self.parse_jobs_lock:
            self.parse_symbols_job_running = True
        labels = set()
        includes = set()
        inputs = set()
        bibliographies = set()
        bibitems = set()
        packages = set()
        packages_detailed = dict()
        for match in ServiceLocator.get_regex_object(r'\\(label|include|input|bibliography)\{((?:\s|\w|\:|,)*)\}|\\(usepackage)(?:\[.*\]){0,1}\{((?:\s|\w|\:|,)*)\}|\\(bibitem)(?:\[.*\]){0,1}\{((?:\s|\w|\:)*)\}').finditer(text):
            if match.group(1) == 'label':
                labels = labels | {match.group(2).strip()}
            elif match.group(1) == 'include':
                includes = includes | {match.group(2).strip()}
            elif match.group(1) == 'input':
                inputs = inputs | {match.group(2).strip()}
            elif match.group(1) == 'bibliography':
                bibfiles = match.group(2).strip().split(',')
                for entry in bibfiles:
                    bibliographies = bibliographies | {entry.strip()}
            elif match.group(3) == 'usepackage':
                packages = packages | {match.group(4).strip()}
                packages_detailed[match.group(4).strip()] = match
            elif match.group(5) == 'bibitem':
                bibitems = bibitems | {match.group(6).strip()}

        with self.symbols_lock:
            self.symbols['labels'] = labels
            self.symbols['includes'] = includes
            self.symbols['inputs'] = inputs
            self.symbols['bibliographies'] = bibliographies
            self.symbols['bibitems'] = bibitems
            self.symbols['packages'] = packages
            self.symbols['packages_detailed'] = packages_detailed
            self.labels_changed = True
        with self.parse_jobs_lock:
            self.parse_symbols_job_running = False


class ParseJob():

    def __init__(self, starting_time, text):
        self.starting_time = starting_time
        self.text = text



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
from gi.repository import GObject

import _thread as thread, queue
import time, re, difflib

from setzer.app.service_locator import ServiceLocator
from setzer.dialogs.dialog_locator import DialogLocator
import setzer.document.build_system.builder.builder_build_latex as builder_build_latex
import setzer.document.build_system.builder.builder_build_bibtex as builder_build_bibtex
import setzer.document.build_system.builder.builder_build_biber as builder_build_biber
import setzer.document.build_system.builder.builder_build_makeindex as builder_build_makeindex
import setzer.document.build_system.builder.builder_build_glossaries as builder_build_glossaries
import setzer.document.build_system.builder.builder_forward_sync as builder_forward_sync
import setzer.document.build_system.builder.builder_backward_sync as builder_backward_sync
import setzer.document.build_system.query.query as query
from setzer.helpers.observable import Observable


class BuildSystem(Observable):

    def __init__(self, document):
        Observable.__init__(self)
        self.document = document
        self.settings = ServiceLocator.get_settings()
        self.active_query = None

        # possible states: idle, ready_for_building
        # building_in_progress, building_to_stop
        self.build_state = 'idle'

        # possible values: build, forward_sync, build_and_forward_sync
        self.build_mode = 'build_and_forward_sync'

        self.document_has_been_built = False
        self.build_time = None
        self.last_build_start_time = None

        self.has_synctex_file = False
        self.backward_sync_data = None
        self.forward_sync_arguments = None
        self.can_sync = False
        self.update_can_sync()

        self.build_log_data = {'items': list(), 'error_count': 0, 'warning_count': 0, 'badbox_count': 0}

        self.builders = dict()
        self.builders['build_latex'] = builder_build_latex.BuilderBuildLaTeX()
        self.builders['build_bibtex'] = builder_build_bibtex.BuilderBuildBibTeX()
        self.builders['build_biber'] = builder_build_biber.BuilderBuildBiber()
        self.builders['build_makeindex'] = builder_build_makeindex.BuilderBuildMakeindex()
        self.builders['build_glossaries'] = builder_build_glossaries.BuilderBuildGlossaries()
        self.builders['forward_sync'] = builder_forward_sync.BuilderForwardSync()
        self.builders['backward_sync'] = builder_backward_sync.BuilderBackwardSync()

        self.document.preview.connect('pdf_changed', self.update_can_sync)

        GObject.timeout_add(50, self.results_loop)

    def change_build_state(self, state):
        self.build_state = state

        if self.build_mode in ['build', 'build_and_forward_sync']:
            if state == 'building_in_progress':
                self.last_build_start_time = time.time()
            elif state == 'building_to_stop':
                pass
            elif state == 'idle':
                pass
        self.add_change_code('build_state_change', self.build_state)

    def get_build_state(self):
        return self.build_state

    def show_build_state(self, message):
        self.add_change_code('build_state', message)

    def set_build_mode(self, mode):
        self.build_mode = mode

    def get_build_mode(self):
        return self.build_mode

    def set_has_synctex_file(self, has_synctex_file):
        self.has_synctex_file = has_synctex_file
        self.update_can_sync()

    def update_can_sync(self, *params):
        self.can_sync = False
        if self.has_synctex_file and self.document.preview.poppler_document != None:
            self.can_sync = True
        else:
            self.can_sync = False
        self.add_change_code('can_sync_changed', self.can_sync)

    def forward_sync(self, active_document):
        if not self.can_sync: return

        self.set_forward_sync_arguments(active_document)
        self.set_build_mode('forward_sync')
        self.start_building()

    def backward_sync(self, page, x, y, word, context):
        if not self.can_sync: return

        self.backward_sync_data = {'page': page, 'x': x, 'y': y, 'word': word, 'context': context}
        self.set_build_mode('backward_sync')
        self.start_building()

    def build_and_forward_sync(self, active_document):
        self.set_forward_sync_arguments(active_document)
        self.set_build_mode('build_and_forward_sync')
        self.start_building()

    def set_forward_sync_arguments(self, active_document):
        sb = active_document.source_buffer
        self.forward_sync_arguments = dict()
        self.forward_sync_arguments['filename'] = active_document.get_filename()
        self.forward_sync_arguments['line'] = sb.get_iter_at_mark(sb.get_insert()).get_line() + 1
        self.forward_sync_arguments['line_offset'] = sb.get_iter_at_mark(sb.get_insert()).get_line_offset() + 1

    def set_build_log_items(self, log_items):
        build_log_items = list()
        error_count = 0
        warning_count = 0
        badbox_count = 0

        def add_items(items_list, new_items, filename, item_type):
            for item in new_items[item_type.lower()]:
                items_list.append((item_type, item[0], filename, item[1], item[2]))

        for item_type in ['Error', 'Warning', 'Badbox']:
            if self.document.filename in log_items:
                add_items(build_log_items, log_items[self.document.filename], self.document.filename, item_type)

            for filename, items in log_items.items():
                if item_type == 'Error':
                    error_count += len(items['error'])
                if item_type == 'Warning':
                    warning_count += len(items['warning'])
                if item_type == 'Badbox':
                    badbox_count += len(items['badbox'])
                if filename != self.document.filename:
                    add_items(build_log_items, log_items[filename], filename, item_type)

        self.build_log_data = {'items': build_log_items, 'error_count': error_count, 'warning_count': warning_count, 'badbox_count': badbox_count}

    def invalidate_build_log(self):
        self.add_change_code('build_log_update')

    def get_error_count(self):
        return self.build_log_data['error_count']

    def get_warning_count(self):
        return self.build_log_data['warning_count']

    def get_badbox_count(self):
        return self.build_log_data['badbox_count']

    def results_loop(self):
        if self.active_query != None:
            if self.active_query.is_done():
                build_result = self.active_query.get_build_result()
                forward_sync_result = self.active_query.get_forward_sync_result()
                backward_sync_result = self.active_query.get_backward_sync_result()
                if forward_sync_result != None or backward_sync_result != None or build_result != None:
                    self.parse_result({'build': build_result, 'forward_sync': forward_sync_result, 'backward_sync': backward_sync_result})
                self.active_query = None
        return True

    def parse_result(self, result_blob):
        if result_blob['build'] != None or result_blob['forward_sync'] != None:
            if result_blob['build'] != None:
                try:
                    self.document.preview.set_pdf_filename(result_blob['build']['pdf_filename'])
                except KeyError: pass
                self.document.add_change_code('pdf_updated')

            if result_blob['forward_sync'] != None:
                self.document.preview.set_synctex_rectangles(result_blob['forward_sync'])
                self.show_build_state('')

            if result_blob['build'] != None:
                build_blob = result_blob['build']

                if build_blob['error'] == 'interpreter_missing':
                    self.show_build_state('')
                    self.change_build_state('idle')
                    DialogLocator.get_dialog('interpreter_missing').run(build_blob['error_arg'])
                    return

                if build_blob['error'] == 'interpreter_not_working':
                    self.show_build_state('')
                    self.change_build_state('idle')
                    DialogLocator.get_dialog('building_failed').run(build_blob['error_arg'])
                    return

                build_blob['log_messages']['BibTeX'] = build_blob['bibtex_log_messages']
                self.set_build_log_items(build_blob['log_messages'])
                self.build_time = time.time() - self.last_build_start_time

                error_count = self.get_error_count()
                if error_count > 0:
                    self.show_build_state('error')
                else:
                    self.show_build_state('success')

                self.set_has_synctex_file(build_blob['has_synctex_file'])
                self.document_has_been_built = True

        elif result_blob['backward_sync'] != None:
            if not self.document.root_is_set:
                if result_blob['backward_sync']['filename'] == self.document.get_filename():
                    self.set_synctex_position(self.document, result_blob['backward_sync'])
                    self.document.scroll_cursor_onscreen()
            elif self.document.is_root:
                workspace = ServiceLocator.get_workspace()
                document = workspace.open_document_by_filename(result_blob['backward_sync']['filename'])
                if document != None:
                    self.set_synctex_position(document, result_blob['backward_sync'])
                    document.scroll_cursor_onscreen()

        self.change_build_state('idle')

        if result_blob['build'] != None:
            self.invalidate_build_log()

    def add_query(self, query):
        self.stop_building(notify=False)
        self.active_query = query
        thread.start_new_thread(self.execute_query, (query,))

        self.change_build_state('building_in_progress')

    def execute_query(self, query):
        while len(query.jobs) > 0:
            if not query.force_building_to_stop:
                self.builders[query.jobs.pop(0)].run(query)
        query.mark_done()

    def start_building(self):
        if self.build_mode == 'forward_sync' and not self.has_synctex_file: return
        if self.build_mode == 'backward_sync' and self.backward_sync_data == None: return
        if self.document.filename == None: return

        self.build_time = None
        mode = self.get_build_mode()
        query_obj = query.Query(self.document.get_filename()[:])

        if mode in ['forward_sync', 'build_and_forward_sync']:
            synctex_arguments = self.forward_sync_arguments

        if mode in ['build', 'build_and_forward_sync']:
            interpreter = self.settings.get_value('preferences', 'latex_interpreter')
            use_latexmk = self.settings.get_value('preferences', 'use_latexmk')
            build_option_system_commands = self.settings.get_value('preferences', 'build_option_system_commands')
            additional_arguments = ''

            if interpreter == 'tectonic':
                pass
            else:
                lualatex_prefix = ' -' if interpreter == 'lualatex' else ' '
                if build_option_system_commands == 'disable':
                    additional_arguments += lualatex_prefix + '-no-shell-escape'
                elif build_option_system_commands == 'restricted':
                    additional_arguments += lualatex_prefix + '-shell-restricted'
                elif build_option_system_commands == 'enable':
                    additional_arguments += lualatex_prefix + '-shell-escape'

            text = self.document.get_all_text()
            do_cleanup = self.settings.get_value('preferences', 'cleanup_build_files')

        if mode == 'build':
            query_obj.jobs = ['build_latex']
            query_obj.build_data['text'] = text
            query_obj.build_data['latex_interpreter'] = interpreter
            query_obj.build_data['use_latexmk'] = use_latexmk
            query_obj.build_data['additional_arguments'] = additional_arguments
            query_obj.build_data['do_cleanup'] = do_cleanup
        elif mode == 'forward_sync':
            query_obj.jobs = ['forward_sync']
            query_obj.can_sync = True
            query_obj.forward_sync_data['filename'] = synctex_arguments['filename']
            query_obj.forward_sync_data['line'] = synctex_arguments['line']
            query_obj.forward_sync_data['line_offset'] = synctex_arguments['line_offset']
        elif mode == 'backward_sync' and self.backward_sync_data != None:
            query_obj.jobs = ['backward_sync']
            query_obj.can_sync = True
            query_obj.backward_sync_data['page'] = self.backward_sync_data['page']
            query_obj.backward_sync_data['x'] = self.backward_sync_data['x']
            query_obj.backward_sync_data['y'] = self.backward_sync_data['y']
            query_obj.backward_sync_data['word'] = self.backward_sync_data['word']
            query_obj.backward_sync_data['context'] = self.backward_sync_data['context']
        else:
            query_obj.jobs = ['build_latex', 'forward_sync']
            query_obj.build_data['text'] = text
            query_obj.build_data['latex_interpreter'] = interpreter
            query_obj.build_data['use_latexmk'] = use_latexmk
            query_obj.build_data['additional_arguments'] = additional_arguments
            query_obj.build_data['do_cleanup'] = do_cleanup
            query_obj.can_sync = False
            query_obj.forward_sync_data['filename'] = synctex_arguments['filename']
            query_obj.forward_sync_data['line'] = synctex_arguments['line']
            query_obj.forward_sync_data['line_offset'] = synctex_arguments['line_offset']

        self.add_query(query_obj)

    def stop_building(self, notify=True):
        if self.active_query != None:
            self.active_query.jobs = []
            self.active_query = None
        for builder in self.builders.values():
            builder.stop_running()
        if notify:
            self.show_build_state('')
            self.change_build_state('idle')

    def set_synctex_position(self, document, position):
        position_found, start = document.source_buffer.get_iter_at_line(position['line'])
        end = start.copy()
        if not start.ends_line():
            end.forward_to_line_end()
        text = document.source_buffer.get_text(start, end, False)

        matches = self.get_synctex_word_bounds(text, position['word'], position['context'])
        if matches != None:
            for word_bounds in matches:
                end = start.copy()
                new_start = start.copy()
                new_start.forward_chars(word_bounds[0])
                end.forward_chars(word_bounds[1])
                document.source_buffer.place_cursor(new_start)
                document.highlight_section(new_start, end)
        else:
            ws_number = len(text) - len(text.lstrip())
            start.forward_chars(ws_number)
            document.source_buffer.place_cursor(start)
            document.highlight_section(start, end)

    def get_synctex_word_bounds(self, text, word, context):
        if not word: return None
        word = word.split(' ')
        if len(word) > 2:
            word = word[:2]
        word = ' '.join(word)
        regex_pattern = re.escape(word)

        for c in regex_pattern:
            if ord(c) > 127:
                regex_pattern = regex_pattern.replace(c, '(?:\\w)')

        matches = list()
        top_score = 0.1
        regex = ServiceLocator.get_regex_object(r'(\W{0,1})' + regex_pattern.replace('\\x1b', r'(?:\w{2,3})').replace('\\x1c', r'(?:\w{2})').replace('\\x1d', r'(?:\w{2,3})').replace('\\-', r'(?:-{0,1})') + r'(\W{0,1})')
        for match in regex.finditer(text):
            offset1 = context.find(word)
            offset2 = len(context) - offset1 - len(word)
            match_text = text[max(match.start() - max(offset1, 0), 0):min(match.end() + max(offset2, 0), len(text))]
            score = difflib.SequenceMatcher(None, match_text, context).ratio()
            if bool(match.group(1)) or bool(match.group(2)):
                if score > top_score + 0.1:
                    top_score = score
                    matches = [[match.start() + len(match.group(1)), match.end() - len(match.group(2))]]
                elif score > top_score - 0.1:
                    matches.append([match.start() + len(match.group(1)), match.end() - len(match.group(2))])
        if len(matches) > 0:
            return matches
        else:
            return None



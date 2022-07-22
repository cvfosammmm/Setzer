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

import _thread as thread, queue
import time

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
        if self.has_synctex_file and self.document.preview.poppler_document != None:
            self.can_sync = True
        else:
            self.can_sync = False
        self.add_change_code('can_sync_changed', self.can_sync)

    def forward_sync(self, active_document):
        self.forward_sync_arguments = dict()
        self.forward_sync_arguments['filename'] = active_document.get_filename()
        self.forward_sync_arguments['line'] = active_document.content.get_cursor_line_number() + 1
        self.forward_sync_arguments['line_offset'] = active_document.content.get_cursor_line_offset() + 1
        if self.can_sync:
            self.set_build_mode('forward_sync')
            self.start_building()

    def backward_sync(self, page, x, y, word, context):
        if self.can_sync:
            self.backward_sync_data = {'page': page, 'x': x, 'y': y, 'word': word, 'context': context}
            self.set_build_mode('backward_sync')
            self.start_building()

    def build_and_forward_sync(self, active_document):
        self.forward_sync_arguments = dict()
        self.forward_sync_arguments['filename'] = active_document.get_filename()
        self.forward_sync_arguments['line'] = active_document.content.get_cursor_line_number() + 1
        self.forward_sync_arguments['line_offset'] = active_document.content.get_cursor_line_offset() + 1
        self.set_build_mode('build_and_forward_sync')
        self.start_building()

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
                    if DialogLocator.get_dialog('interpreter_missing').run(build_blob['error_arg']):
                        DialogLocator.get_dialog('preferences').run()
                    return

                if build_blob['error'] == 'interpreter_not_working':
                    self.show_build_state('')
                    self.change_build_state('idle')
                    if DialogLocator.get_dialog('building_failed').run(build_blob['error_arg']):
                        DialogLocator.get_dialog('preferences').run()
                    return

                build_blob['log_messages']['BibTeX'] = build_blob['bibtex_log_messages']
                self.set_build_log_items(build_blob['log_messages'])
                self.build_time = time.time() - self.last_build_start_time

                error_count = self.get_error_count()
                if error_count > 0:
                    error_color_rgba = ServiceLocator.get_color_manager().get_theme_color('error_color')
                    error_color = '#' + format(int(error_color_rgba.red * 255), '02x') + format(int(error_color_rgba.green * 255), '02x') + format(int(error_color_rgba.blue * 255), '02x')
                    str_errors = ngettext('<span color="{color}">Failed</span> ({amount} error)!', '<span color="{color}">Failed</span> ({amount} errors)!', error_count)
                    message = str_errors.format(color=error_color, amount=str(error_count))
                    self.show_build_state(message)
                else:
                    self.show_build_state(_('Success!'))

                self.set_has_synctex_file(build_blob['has_synctex_file'])
                self.document_has_been_built = True

        elif result_blob['backward_sync'] != None:
            if not self.document.root_is_set:
                if result_blob['backward_sync']['filename'] == self.document.get_filename():
                    self.document.content.set_synctex_position(result_blob['backward_sync'])
                    self.document.content.scroll_cursor_onscreen()
            elif self.document.is_root:
                workspace = ServiceLocator.get_workspace()
                document = workspace.open_document_by_filename(result_blob['backward_sync']['filename'])
                if document != None:
                    document.content.set_synctex_position(result_blob['backward_sync'])
                    document.content.scroll_cursor_onscreen()

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

            lualatex_prefix = ' -' if interpreter == 'lualatex' else ' '
            if build_option_system_commands == 'disable':
                additional_arguments += lualatex_prefix + '-no-shell-escape'
            elif build_option_system_commands == 'restricted':
                additional_arguments += lualatex_prefix + '-shell-restricted'
            elif build_option_system_commands == 'enable':
                additional_arguments += lualatex_prefix + '-shell-escape'

            text = self.document.content.get_all_text()
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



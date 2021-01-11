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
import time

from setzer.document.document import Document
import setzer.document.latex.build_system.build_system as build_system
import setzer.document.latex.build_widget.build_widget as build_widget
import setzer.document.latex.autocomplete.autocomplete as autocomplete
import setzer.document.latex.code_folding.code_folding as code_folding
import setzer.document.latex.parser.latex_parser as latex_parser
import setzer.document.latex.preview.preview as preview
import setzer.document.latex.state_manager.state_manager_latex as state_manager_latex
from setzer.helpers.observable import Observable
from setzer.app.service_locator import ServiceLocator


class DocumentLaTeX(Document):

    def __init__(self):
        Document.__init__(self)
        self.has_visible_build_system = False

        # possible states: idle, ready_for_building
        # building_in_progress, building_to_stop
        self.build_state = 'idle'

        # possible values: build, forward_sync, build_and_forward_sync
        self.build_mode = 'build_and_forward_sync'
        self.has_synctex_file = False
        self.backward_sync_data = None
        self.can_sync = False

        self.preview = preview.Preview(self)
        self.state_manager = state_manager_latex.StateManagerLaTeX(self)

        self.build_log_data = {'items': list(), 'error_count': 0, 'warning_count': 0, 'badbox_count': 0}
        self.has_been_built = False
        self.last_build_start_time = None
        self.build_time = None
        self.build_widget = build_widget.BuildWidget(self)

        self.autocomplete = autocomplete.Autocomplete(self, self.view)
        self.view.scrolled_window.get_vadjustment().connect('value-changed', self.autocomplete.on_adjustment_value_changed)
        self.view.scrolled_window.get_hadjustment().connect('value-changed', self.autocomplete.on_adjustment_value_changed)
        self.view.source_view.connect('focus-out-event', self.autocomplete.on_focus_out)
        self.view.source_view.connect('focus-in-event', self.autocomplete.on_focus_in)

        self.build_system = build_system.BuildSystem(self)
        self.code_folding = code_folding.CodeFolding(self)

        self.symbols = dict()
        self.symbols['labels'] = set()
        self.symbols['included_latex_files'] = set()
        self.symbols['bibliographies'] = set()
        self.symbols['bibitems'] = set()
        self.symbols['packages'] = set()
        self.symbols['packages_detailed'] = dict()
        self.symbols['blocks'] = list()

        self.parser = latex_parser.LaTeXParser(self)

        self.update_can_sync()

    def init_shortcuts(self, shortcuts_manager):
        shortcuts_manager.set_accels_for_insert_before_after_action(['\\textbf{', '}'], ['<Control>b'])
        shortcuts_manager.set_accels_for_insert_before_after_action(['\\textit{', '}'], ['<Control>i'])
        shortcuts_manager.set_accels_for_insert_before_after_action(['\\underline{', '}'], ['<Control>u'])
        shortcuts_manager.set_accels_for_insert_before_after_action(['\\emph{', '}'], ['<Control><Shift>e'])
        shortcuts_manager.set_accels_for_insert_before_after_action(['\\texttt{', '}'], ['<Control>m'])
        shortcuts_manager.set_accels_for_insert_before_after_action(['$ ', ' $'], ['<Control><Shift>m'])
        shortcuts_manager.set_accels_for_insert_before_after_action(['\\[ ', ' \\]'], ['<Alt><Shift>m'])
        shortcuts_manager.set_accels_for_insert_before_after_action(['\\begin{equation}\n\t', '\n\\end{equation}'], ['<Control><Shift>n'])
        shortcuts_manager.set_accels_for_insert_before_after_action(['\\begin{•}\n\t', '\n\\end{•}'], ['<Control>e'])
        shortcuts_manager.set_accels_for_insert_before_after_action(['_{', '}'], ['<Control><Shift>d'])
        shortcuts_manager.set_accels_for_insert_before_after_action(['^{', '}'], ['<Control><Shift>u'])
        shortcuts_manager.set_accels_for_insert_before_after_action(['\\sqrt{', '}'], ['<Control><Shift>q'])
        shortcuts_manager.set_accels_for_insert_symbol_action(['\\frac{•}{•}'], ['<Alt><Shift>f'])
        shortcuts_manager.set_accels_for_insert_symbol_action(['\\left •'], ['<Control><Shift>l'])
        shortcuts_manager.set_accels_for_insert_symbol_action(['\\right •'], ['<Control><Shift>r'])
        shortcuts_manager.set_accels_for_insert_symbol_action(['\\item •'], ['<Control><Shift>i'])
        shortcuts_manager.set_accels_for_insert_symbol_action(['\\\\\n'], ['<Control>Return'])
        shortcuts_manager.main_window.app.set_accels_for_action('win.comment-uncomment', ['<Control>K'])

    def get_latex_command_at_cursor(self):
        return self.source_buffer.get_latex_command_at_cursor()

    def get_latex_command_at_cursor_offset(self):
        return self.source_buffer.get_latex_command_at_cursor_offset()

    def replace_latex_command_at_cursor(self, command, dotlabels, is_full_command=False):
        self.source_buffer.replace_latex_command_at_cursor(command, dotlabels, is_full_command)

    def add_packages(self, packages):
        self.get_buffer().add_packages(packages)

    def get_packages(self):
        return self.symbols['packages']

    def get_package_details(self):
        return self.symbols['packages_detailed']

    def remove_packages(self, packages):
        self.get_buffer().remove_packages(packages)

    def get_matching_begin_end_offset(self, orig_offset):
        blocks = self.get_blocks()
        for block in blocks:
            if block[0] == orig_offset - 7:
                return None if block[1] == None else block[1] + 5
            elif block[1] == orig_offset - 5:
                return None if block[0] == None else block[0] + 7
        return None

    def get_blocks(self):
        return self.symbols['blocks']

    def set_blocks(self, blocks):
        self.symbols['blocks'] = blocks
        self.add_change_code('blocks_changed')

    def set_build_log_items(self, log_items):
        build_log_items = list()
        error_count = 0
        warning_count = 0
        badbox_count = 0

        def add_items(items_list, new_items, filename, item_type):
            for item in new_items[item_type.lower()]:
                items_list.append((item_type, item[0], filename, item[1], item[2]))

        for item_type in ['Error', 'Warning', 'Badbox']:
            if self.filename in log_items:
                add_items(build_log_items, log_items[self.filename], self.filename, item_type)

            for filename, items in log_items.items():
                if item_type == 'Error':
                    error_count += len(items['error'])
                if item_type == 'Warning':
                    warning_count += len(items['warning'])
                if item_type == 'Badbox':
                    badbox_count += len(items['badbox'])
                if filename != self.filename:
                    add_items(build_log_items, log_items[filename], filename, item_type)

        self.build_log_data = {'items': build_log_items, 'error_count': error_count, 'warning_count': warning_count, 'badbox_count': badbox_count}

    def get_error_count(self):
        return self.build_log_data['error_count']

    def get_warning_count(self):
        return self.build_log_data['warning_count']

    def get_badbox_count(self):
        return self.build_log_data['badbox_count']

    def set_initial_folded_regions(self, folded_regions):
        try:
            self.code_folding.set_initial_folded_regions(folded_regions)
        except AttributeError:
            pass

    def get_included_files(self):
        return self.get_included_latex_files() | self.get_bibliography_files()

    def get_included_latex_files(self):
        return self.symbols['included_latex_files']

    def get_bibliography_files(self):
        return self.symbols['bibliographies']

    def get_bibitems(self):
        return self.symbols['bibitems']

    def get_labels(self):
        return self.symbols['labels']

    def change_build_state(self, state):
        self.build_state = state

        if self.build_mode in ['build', 'build_and_forward_sync']:
            if state == 'ready_for_building':
                self.build_time = None
            elif state == 'building_in_progress':
                self.last_build_start_time = time.time()
            elif state == 'building_to_stop':
                pass
            elif state == 'idle':
                pass
            self.add_change_code('build_state_change', self.build_state)
        else:
            self.add_change_code('build_state_change', self.build_state)

    def show_build_state(self, message):
        self.add_change_code('build_state', message)

    def get_build_state(self):
        return self.build_state

    def set_build_mode(self, mode):
        self.build_mode = mode

    def get_build_mode(self):
        return self.build_mode

    def set_has_synctex_file(self, has_synctex_file):
        self.has_synctex_file = has_synctex_file
        self.update_can_sync()

    def update_can_sync(self):
        if self.has_synctex_file and self.preview.pdf_loaded:
            self.can_sync = True
        else:
            self.can_sync = False
        self.add_change_code('can_sync_changed', self.can_sync)

    def forward_sync(self):
        if self.can_sync:
            self.set_build_mode('forward_sync')
            self.start_building()

    def backward_sync(self, page, x, y, word, context):
        if self.can_sync:
            self.backward_sync_data = {'page': page, 'x': x, 'y': y, 'word': word, 'context': context}
            self.set_build_mode('backward_sync')
            self.start_building()

    def build_and_forward_sync(self):
        self.set_build_mode('build_and_forward_sync')
        self.start_building()

    def start_building(self):
        if self.build_mode == 'forward_sync' and not self.has_synctex_file: return
        if self.build_mode == 'backward_sync' and self.backward_sync_data == None: return
        if self.filename == None: return

        self.change_build_state('ready_for_building')

    def stop_building(self):
        self.change_build_state('building_to_stop')

    def cleanup_build_files(self):
        file_endings = ['.aux', '.blg', '.bbl', '.dvi', '.xdv', '.fdb_latexmk', '.fls', '.idx' ,'.ilg', '.ind', '.log', '.nav', '.out', '.snm', '.synctex.gz', '.toc', '.ist', '.glo', '.glg', '.acn', '.alg', '.gls', '.acr', '.bcf', '.run.xml', '.out.ps']
        for ending in file_endings:
            filename = os.path.splitext(self.get_filename())[0] + ending
            try: os.remove(filename)
            except FileNotFoundError: pass
        self.add_change_code('cleaned_up_build_files')

    def invalidate_build_log(self):
        self.add_change_code('build_log_update')

    def set_is_root(self, is_root):
        self.is_root = is_root
        self.add_change_code('root_state_change', is_root)

    def set_has_visible_build_system(self, has_visible_build_system):
        if self.has_visible_build_system != has_visible_build_system:
            self.has_visible_build_system = has_visible_build_system
            self.add_change_code('build_system_visibility_change', has_visible_build_system)

    def comment_uncomment(self):
        self.get_buffer().comment_uncomment()

    def set_invert_pdf(self, invert_pdf):
        self.preview.set_invert_pdf(invert_pdf)

    def set_synctex_position(self, position):
        self.get_buffer().set_synctex_position(position)

    def get_folded_regions(self):
        try:
            regions = self.code_folding.get_folded_regions()
        except AttributeError:
            regions = list()
        return regions

    def get_file_ending(self):
        return 'tex'

    def get_is_root(self):
        return self.is_root

    def is_latex_document(self):
        return True

    def is_bibtex_document(self):
        return False

    def get_gsv_language_name(self):
        return 'latex'



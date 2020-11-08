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
        self.build_pathname = None
        self.can_backward_sync = False
        self.backward_sync_data = None

        self.preview = preview.Preview(self)
        self.state_manager = state_manager_latex.StateManagerLaTeX(self)

        self.build_log_items = list()
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

        self.parser = latex_parser.LaTeXParser(self)

        self.update_can_forward_sync()
        self.update_can_backward_sync()

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

    def get_matching_begin_end_offset(self, orig_offset):
        blocks = self.parser.get_blocks_now()
        for block in blocks:
            if block[0] == orig_offset - 7:
                return None if block[1] == None else block[1] + 5
            elif block[1] == orig_offset - 5:
                return None if block[0] == None else block[0] + 7
        return None

    def get_blocks(self):
        return self.parser.get_blocks()

    def get_included_files(self):
        return self.get_included_latex_files() | self.get_bibliography_files()

    def get_included_latex_files(self):
        labels_dict = self.parser.get_labels()
        return labels_dict['included_latex_files']

    def get_bibliography_files(self):
        labels_dict = self.parser.get_labels()
        return labels_dict['bibliographies']

    def get_bibitems(self):
        labels_dict = self.parser.get_labels()
        return labels_dict['bibitems']

    def get_labels(self):
        labels_dict = self.parser.get_labels()
        return labels_dict['labels']

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

    def set_build_pathname(self, pathname):
        self.build_pathname = pathname
        self.update_can_forward_sync()
        self.update_can_backward_sync()

    def update_can_forward_sync(self):
        if self.build_pathname != None and self.preview.pdf_loaded:
            self.can_forward_sync = True
        else:
            self.can_forward_sync = False
        self.add_change_code('can_forward_sync_changed', self.can_forward_sync)

    def update_can_backward_sync(self):
        if self.build_pathname != None and self.preview.pdf_loaded:
            self.can_backward_sync = True
        else:
            self.can_backward_sync = False
        self.add_change_code('can_backward_sync_changed', self.can_backward_sync)

    def forward_sync(self):
        if self.can_forward_sync:
            self.set_build_mode('forward_sync')
            self.start_building()

    def backward_sync(self, page, x, y, word, context):
        if self.can_backward_sync:
            self.backward_sync_data = {'page': page, 'x': x, 'y': y, 'word': word, 'context': context}
            self.set_build_mode('backward_sync')
            self.start_building()

    def build_and_forward_sync(self):
        self.set_build_mode('build_and_forward_sync')
        self.start_building()

    def start_building(self):
        if self.build_mode == 'forward_sync' and self.build_pathname == None: return
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

    def set_is_master(self, is_master):
        self.is_master = is_master
        self.add_change_code('master_state_change', is_master)

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
        return self.code_folding.get_folded_regions()

    def get_file_ending(self):
        return 'tex'

    def get_is_master(self):
        return self.is_master

    def is_latex_document(self):
        return True

    def is_bibtex_document(self):
        return False

    def get_gsv_language_name(self):
        return 'latex'



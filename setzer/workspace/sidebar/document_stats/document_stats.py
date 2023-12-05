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

import os.path
import subprocess
import _thread as thread

import setzer.workspace.sidebar.document_stats.document_stats_viewgtk as document_stats_section_view
import setzer.helpers.path as path_helpers
from setzer.helpers.timer import timer


class DocumentStats(object):

    def __init__(self, workspace, labels):
        self.workspace = workspace
        self.headline_labels = labels
        self.document = None

        self.view = document_stats_section_view.DocumentStatsView()

        self.values = dict()
        self.values[None] = {'save_date': 0, 'counts': None}
        self.values_lock = thread.allocate_lock()
        self.texcount_missing = False

        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('root_state_change', self.on_root_state_change)

        GObject.timeout_add(200, self.update_view)
        GObject.timeout_add(1000, self.update_data)

    def on_new_active_document(self, workspace, document):
        self.set_document()

    def on_root_state_change(self, workspace, root_state):
        self.set_document()

    def set_document(self):
        document = self.workspace.get_root_or_active_latex_document()
        if document != self.document:
            self.document = document
            self.update_data()
        self.update_view()

    def on_modified_changed(self, buffer):
        self.update_data()

    #@timer
    def update_data(self):
        if self.document == None: return True

        filenames = {self.document.get_filename()}
        if self.workspace.get_active_document() != None:
            filenames |= {self.workspace.get_active_document().get_filename()}
        for filename, _ in self.document.parser.symbols['included_latex_files']:
            filenames |= {path_helpers.get_abspath(filename, self.document.get_dirname())}

        for filename in filenames:
            if filename not in self.values:
                self.values[filename] = {'save_date': 0, 'counts': None}

            if filename == None:
                with self.values_lock:
                    self.values[filename]['counts'] = None

            else:
                try:
                    save_date = os.path.getmtime(filename)
                except FileNotFoundError:
                    pass
                else:
                    if save_date > self.values[filename]['save_date']:
                        self.values[filename]['save_date'] = save_date
                        self.count_words(filename)
        return True

    def count_words(self, filename):
        thread.start_new_thread(self.run_query, (['texcount', '-brief', filename], filename))
        return False

    #@timer
    def run_query(self, arguments, filename):
        try:
            process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except FileNotFoundError:
            with self.values_lock:
                self.texcount_missing = True
                self.values[filename]['counts'] = None
            return
        process.wait()

        with self.values_lock:
            raw_result = process.communicate()[0].decode('utf-8').split('+')
            count_0 = raw_result[0].split('\n')[-1]
            count_1 = raw_result[1]
            count_2 = raw_result[2].split(' ')[0]
            self.values[filename]['counts'] = [count_0, count_1, count_2]
            self.texcount_missing = False

    #@timer
    def update_view(self):
        with self.values_lock:
            if self.texcount_missing:
                self.hide_view()

        if self.document != None and self.document.get_is_root():
            with self.values_lock:
                values = self.values[self.document.get_filename()]['counts']

            if values == None or len(values) != 3:
                values = ['?', '?', '?']

            else:
                values = [int(value) for value in values]
                for filename, _ in self.document.parser.symbols['included_latex_files']:
                    filename = path_helpers.get_abspath(filename, self.document.get_dirname())
                    with self.values_lock:
                        if filename in self.values:
                            values_include = self.values[filename]['counts']
                            if values_include != None and len(values_include) == 3:
                                values[0] += int(values_include[0])
                                values[1] += int(values_include[1])
                                values[2] += int(values_include[2])

            markup = 'The whole document has <b>'
            markup += str(values[0])
            markup += '</b> words in text, <b>'
            markup += str(values[1])
            markup += '</b> words in headers and <b>'
            markup += str(values[2])
            markup += '</b> words outside text (captions, ...).'
            self.view.label_whole_document.set_markup(markup)
            self.view.label_whole_document.set_visible(True)
        else:
            self.view.label_whole_document.set_visible(False)

        document = self.workspace.get_active_document()
        if document == None: return True

        with self.values_lock:
            if document.get_filename() not in self.values:
                values = None
            else:
                values = self.values[document.get_filename()]['counts']

        if values == None or len(values) != 3:
            values = ['?', '?', '?']

        markup = os.path.basename(document.get_displayname())
        markup += ' has <b>'
        markup += values[0]
        markup += '</b> words in text, <b>'
        markup += values[1]
        markup += '</b> words in headers and <b>'
        markup += values[2]
        markup += '</b> words outside text (captions, ...).'
        self.view.label_current_file.set_markup(markup)

        return True

    def hide_view(self):
        self.view.set_visible(False)
        self.headline_labels['inline'].set_visible(False)
        self.headline_labels['overlay'].set_visible(False)



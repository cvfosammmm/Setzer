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
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

import os.path
import subprocess
import _thread as thread

import setzer.workspace.sidebar.document_stats.document_stats_viewgtk as document_stats_section_view
from setzer.helpers.timer import timer


class DocumentStats(object):

    def __init__(self, workspace, labels):
        self.workspace = workspace
        self.headline_labels = labels
        self.document = None

        self.view = document_stats_section_view.DocumentStatsView()

        self.values = dict()
        self.values_lock = thread.allocate_lock()

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
        if self.document not in self.values:
            self.values[self.document] = {'save_date': 0, 'counts': None}
        if self.document.get_filename() == None:
            with self.values_lock:
                self.values[self.document]['counts'] = None
            return True

        save_date = os.path.getmtime(self.document.get_filename())
        if save_date > self.values[self.document]['save_date']:
            self.values[self.document]['save_date'] = save_date
            self.count_words()
        return True

    def count_words(self):
        thread.start_new_thread(self.run_query, (['texcount', '-brief', self.document.get_filename()],))
        return False

    #@timer
    def run_query(self, arguments):
        try:
            self.process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except FileNotFoundError:
            with self.values_lock:
                self.values[self.document]['counts'] = None
            return
        self.process.wait()

        with self.values_lock:
            self.values[self.document]['counts'] = self.process.communicate()[0].decode('utf-8').split(' ')[0].split('+')

    #@timer
    def update_view(self):
        if self.document == None: return True

        with self.values_lock:
            values = self.values[self.document]['counts']

        if values == None or len(values) != 3:
            values = ['?', '?', '?']

        markup = os.path.basename(self.document.get_displayname())
        markup += ' has <b>'
        markup += values[0]
        markup += '</b> words in text, <b>'
        markup += values[1]
        markup += '</b> words in headers and <b>'
        markup += values[2]
        markup += '</b> words outside text (captions, ...).'
        self.view.label_current_file.set_markup(markup)

        return True



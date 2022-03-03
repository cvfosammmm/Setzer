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

import time
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

        self.request_time = None
        self.values = None
        self.values_changed = True
        self.values_lock = thread.allocate_lock()

        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('root_state_change', self.on_root_state_change)

        self.update_view()
        GObject.timeout_add(500, self.update_view)

    def on_new_active_document(self, workspace, document):
        self.set_document()

    def on_root_state_change(self, workspace, root_state):
        self.set_document()

    def set_document(self):
        if self.workspace.get_active_document() == None:
            document = None
        else:
            if self.workspace.root_document != None:
                document = self.workspace.root_document
            elif self.workspace.active_document.is_latex_document():
                document = self.workspace.active_document
            else:
                document = None
        if document != self.document:
            if self.document != None:
                self.document.content.source_buffer.disconnect('modified_changed', self.on_modified_changed)
            self.document = document
            self.document.content.source_buffer.connect('modified_changed', self.on_modified_changed)
            self.update_data(wait_ms=0)

    def on_modified_changed(self, buffer):
        self.update_data()

    def update_data(self, wait_ms=1000):
        self.request_time = time.time()
        GObject.timeout_add(wait_ms, self.count_words, self.request_time)

    def count_words(self, request_time):
        if request_time < self.request_time: return False

        thread.start_new_thread(self.run_query, (['texcount', '-brief', self.document.get_filename()],))
        return False

    #@timer
    def run_query(self, arguments):
        try:
            self.process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except FileNotFoundError:
            with self.values_lock:
                self.values = None
            return
        self.process.wait()

        with self.values_lock:
            self.values = self.process.communicate()[0].decode('utf-8').split(' ')[0].split('+')
            self.values_changed = True

    #@timer
    def update_view(self):
        with self.values_lock:
            if self.values_changed == False: return True

            values = self.values
            self.values_changed = False

        if values != None and len(values) == 3:
            self.view.label_words_in_text.set_text(values[0])
            self.view.label_words_in_headers.set_text(values[1])
            self.view.label_words_outside_text.set_text(values[2])
        else:
            self.view.label_words_in_text.set_text('?')
            self.view.label_words_in_headers.set_text('?')
            self.view.label_words_outside_text.set_text('?')

        return True



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


class BibTeXParser(object):

    def __init__(self, document):
        self.document = document

        self.symbols = dict()
        self.symbols['bibitems'] = set()
        self.labels_changed = True
        self.last_result = None
        self.symbols_lock = thread.allocate_lock()

        self.last_buffer_change = time.time()

        self.parse_jobs = dict()
        self.parse_jobs['symbols'] = None
        self.parse_symbols_job_running = False
        self.parse_jobs_lock = thread.allocate_lock()

        GObject.timeout_add(1, self.compute_loop)

    def on_buffer_changed(self):
        self.last_buffer_change = time.time()
        text = self.document.get_text()
        with self.parse_jobs_lock:
            self.parse_jobs['symbols'] = ParseJob(time.time() + 0.1, text)

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
        return True

    def get_labels(self):
        with self.symbols_lock:
            if self.labels_changed or self.last_result == None:
                result = dict()
                result['bibitems'] = self.symbols['bibitems'].copy()
                self.last_result = result
            else:
                result = self.last_result
            self.labels_changed = False
        return result

    def parse_symbols(self, text):
        with self.parse_jobs_lock:
            self.parse_symbols_job_running = True

        bibitems = set()
        for match in ServiceLocator.get_regex_object(r'@(\w+)\{(\w+)').finditer(text):
            bibitems = bibitems | {match.group(2).strip()}

        with self.symbols_lock:
            self.symbols['bibitems'] = bibitems
            self.labels_changed = True
        with self.parse_jobs_lock:
            self.parse_symbols_job_running = False


class ParseJob():

    def __init__(self, starting_time, text):
        self.starting_time = starting_time
        self.text = text



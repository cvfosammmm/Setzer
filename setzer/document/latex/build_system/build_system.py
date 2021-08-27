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

import setzer.document.latex.build_system.build_system_controller as build_system_controller
import setzer.document.latex.build_system.build_system_presenter as build_system_presenter

import setzer.document.latex.build_system.builder.builder_build_latex as builder_build_latex
import setzer.document.latex.build_system.builder.builder_build_bibtex as builder_build_bibtex
import setzer.document.latex.build_system.builder.builder_build_biber as builder_build_biber
import setzer.document.latex.build_system.builder.builder_build_makeindex as builder_build_makeindex
import setzer.document.latex.build_system.builder.builder_build_glossaries as builder_build_glossaries
import setzer.document.latex.build_system.builder.builder_forward_sync as builder_forward_sync
import setzer.document.latex.build_system.builder.builder_backward_sync as builder_backward_sync


class BuildSystem(object):

    def __init__(self, document):
        self.observers = set()
        self.active_query = None

        self.builders = dict()
        self.builders['build_latex'] = builder_build_latex.BuilderBuildLaTeX()
        self.builders['build_bibtex'] = builder_build_bibtex.BuilderBuildBibTeX()
        self.builders['build_biber'] = builder_build_biber.BuilderBuildBiber()
        self.builders['build_makeindex'] = builder_build_makeindex.BuilderBuildMakeindex()
        self.builders['build_glossaries'] = builder_build_glossaries.BuilderBuildGlossaries()
        self.builders['forward_sync'] = builder_forward_sync.BuilderForwardSync()
        self.builders['backward_sync'] = builder_backward_sync.BuilderBackwardSync()

        self.controller = build_system_controller.BuildSystemController(document, self)
        self.presenter = build_system_presenter.BuildSystemPresenter(document, self)

        self.change_code_queue = queue.Queue() # change code for observers are put on here
        GObject.timeout_add(50, self.results_loop)
        GObject.timeout_add(50, self.change_code_loop)

    def change_code_loop(self):
        ''' notify observers '''

        if not self.change_code_queue.empty():
            change_code = self.change_code_queue.get(block=False)
            for observer in self.observers:
                observer.change_notification(change_code['change_code'], self, change_code['parameter'])
        return True
    
    def register_observer(self, observer):
        ''' Observer call this method to register themselves with observable
            objects. They have themselves to implement a method
            'change_notification(change_code, parameter)' which the observable
            will call when it's state changes. '''

        self.observers.add(observer)

    def add_change_code(self, change_code, parameter=None):
        self.change_code_queue.put({'change_code': change_code, 'parameter': parameter})

    def results_loop(self):
        if self.active_query != None:
            if self.active_query.is_done():
                build_result = self.active_query.get_build_result()
                forward_sync_result = self.active_query.get_forward_sync_result()
                backward_sync_result = self.active_query.get_backward_sync_result()
                if forward_sync_result != None or backward_sync_result != None or build_result != None:
                    self.add_change_code('building_finished', {'build': build_result, 'forward_sync': forward_sync_result, 'backward_sync': backward_sync_result})
                self.active_query = None
        return True
    
    def add_query(self, query):
        self.stop_building(notify=False)
        self.active_query = query
        thread.start_new_thread(self.execute_query, (query,))
        self.add_change_code('reset_timer')
        self.add_change_code('building_started')

    def execute_query(self, query):
        while len(query.jobs) > 0:
            if not query.force_building_to_stop:
                self.builders[query.jobs.pop(0)].run(query)
        query.mark_done()

    def stop_building(self, notify=True):
        if self.active_query != None:
            self.active_query.jobs = []
            self.active_query = None
        for builder in self.builders.values():
            builder.stop_running()
        if notify:
            self.add_change_code('building_stopped')



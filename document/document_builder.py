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

import document.build_system.build_system as build_system
from app.service_locator import ServiceLocator


class DocumentBuilder(object):
    ''' Mediator between document and build_system. '''
    
    def __init__(self, document):
        self.document = document
        self.build_system = build_system.BuildSystem()
        self.settings = ServiceLocator.get_settings()
        self.document.register_observer(self)
        self.build_system.register_observer(self)

    '''
    *** notification handlers, get called by observed document
    '''

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'document_state_change' and parameter == 'ready_for_building':
            document = self.document
            insert = document.source_buffer.get_iter_at_mark(document.source_buffer.get_insert())
            synctex_arguments = dict()
            synctex_arguments['line'] = insert.get_line()
            synctex_arguments['line_offset'] = insert.get_line_offset()
            buffer = document.get_buffer()
            if buffer != None:
                query = build_system.Query(buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True), self, synctex_arguments, self.settings.get_value('preferences', 'build_command'))
                self.build_system.add_query(query)

        if change_code == 'document_state_change' and parameter == 'building_to_stop':
            document = notifying_object
            self.build_system.stop_building_by_document(document)
        
        if change_code == 'building_started':
            query = parameter
            if self.document == query.get_document():
                self.document.change_state('building_in_progress')
                
        if change_code == 'reset_timer':
            document = parameter
            if self.document == document:
                self.document.view.build_widget.reset_timer()
                self.document.view.build_widget.label.set_text('0:00')

        if change_code == 'building_stopped':
            document = parameter
            if self.document == document:
                self.document.change_state('idle')

        if change_code == 'building_finished':
            result_blob = parameter
            if self == result_blob['document_controller']:
                try:
                    self.document.set_pdf(result_blob['pdf_filename'], result_blob['pdf_position'])
                except KeyError: pass

                build_log_items = list()
                if result_blob['error'] == 'interpreter_missing':
                    self.document.change_state('idle')
                    if ServiceLocator.get_dialog('interpreter_missing').run(result_blob['error_arg']):
                        ServiceLocator.get_dialog('preferences').run()
                    return

                if result_blob['error'] == 'interpreter_not_working':
                    self.document.change_state('idle')
                    if ServiceLocator.get_dialog('building_failed').run(result_blob['error_arg']):
                        ServiceLocator.get_dialog('preferences').run()
                    return

                try:
                    build_log_blob = result_blob['log_messages']
                except KeyError:
                    pass
                else:
                    for item in build_log_blob:
                        build_log_items.append(item)
                self.document.build_log_items = build_log_items

                self.document.change_state('idle')
        


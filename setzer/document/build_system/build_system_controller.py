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

import setzer.document.build_system.query.query as query
from setzer.app.service_locator import ServiceLocator


class BuildSystemController(object):
    ''' Mediator between document and build_system. '''
    
    def __init__(self, document, build_system):
        self.document = document
        self.build_system = build_system
        self.settings = ServiceLocator.get_settings()
        self.document.register_observer(self)

    '''
    *** notification handlers, get called by observed document
    '''

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'build_state_change' and parameter == 'ready_for_building':
            document = self.document
            mode = document.get_build_mode()
            query_obj = query.Query(self.document.get_filename()[:])

            if mode in ['forward_sync', 'build_and_forward_sync']:
                insert = document.source_buffer.get_iter_at_mark(document.source_buffer.get_insert())
                synctex_arguments = dict()
                synctex_arguments['line'] = insert.get_line() + 1
                synctex_arguments['line_offset'] = insert.get_line_offset() + 1

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

                text = document.get_text()
                do_cleanup = self.settings.get_value('preferences', 'cleanup_build_files')

            if mode == 'build':
                query_obj.jobs = ['build_latex']
                query_obj.build_data['text'] = text
                query_obj.build_data['latex_interpreter'] = interpreter
                query_obj.build_data['use_latexmk'] = use_latexmk
                query_obj.build_data['additional_arguments'] = additional_arguments
                query_obj.build_data['do_cleanup'] = do_cleanup
                query_obj.generate_temporary_files()
            elif mode == 'forward_sync' and document.build_pathname != None:
                query_obj.jobs = ['forward_sync']
                query_obj.forward_sync_data['build_pathname'] = document.build_pathname
                query_obj.forward_sync_data['line'] = synctex_arguments['line']
                query_obj.forward_sync_data['line_offset'] = synctex_arguments['line_offset']
            elif mode == 'backward_sync' and document.backward_sync_data != None:
                query_obj.jobs = ['backward_sync']
                query_obj.backward_sync_data['build_pathname'] = document.build_pathname
                query_obj.backward_sync_data['page'] = document.backward_sync_data['page']
                query_obj.backward_sync_data['x'] = document.backward_sync_data['x']
                query_obj.backward_sync_data['y'] = document.backward_sync_data['y']
                query_obj.backward_sync_data['word'] = document.backward_sync_data['word']
                query_obj.backward_sync_data['context'] = document.backward_sync_data['context']
            else:
                query_obj.jobs = ['build_latex', 'forward_sync']
                query_obj.build_data['text'] = text
                query_obj.build_data['latex_interpreter'] = interpreter
                query_obj.build_data['use_latexmk'] = use_latexmk
                query_obj.build_data['additional_arguments'] = additional_arguments
                query_obj.build_data['do_cleanup'] = do_cleanup
                query_obj.forward_sync_data['line'] = synctex_arguments['line']
                query_obj.forward_sync_data['line_offset'] = synctex_arguments['line_offset']
                query_obj.generate_temporary_files()

            self.build_system.add_query(query_obj)

        if change_code == 'build_state_change' and parameter == 'building_to_stop':
            self.build_system.stop_building()



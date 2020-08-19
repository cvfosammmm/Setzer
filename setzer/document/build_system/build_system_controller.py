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
            filename = self.document.get_filename()[:]

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

                buffer = document.get_buffer()
                if buffer != None:
                    text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
                else:
                    text = ''
                do_cleanup = self.settings.get_value('preferences', 'cleanup_build_files')

            if mode == 'build':
                query_obj = query.QueryBuild(text, filename, interpreter, use_latexmk, additional_arguments, do_cleanup)
            elif mode == 'forward_sync':
                if document.build_pathname != None:
                    query_obj = query.QueryForwardSync(filename, document.build_pathname, synctex_arguments)
            elif mode == 'backward_sync':
                if document.backward_sync_data != None:
                    query_obj = query.QueryBackwardSync(filename, document.build_pathname, document.backward_sync_data)
            else:
                query_obj = query.QueryBuildAndForwardSync(text, filename, interpreter, use_latexmk, additional_arguments, do_cleanup, synctex_arguments)

            self.build_system.add_query(query_obj)

        if change_code == 'build_state_change' and parameter == 'building_to_stop':
            self.build_system.stop_building()



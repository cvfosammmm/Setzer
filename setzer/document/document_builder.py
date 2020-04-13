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

import time

import setzer.document.build_system.build_system as build_system
from setzer.app.service_locator import ServiceLocator
from setzer.dialogs.dialog_locator import DialogLocator
import setzer.helpers.helpers as helpers


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
                build_option_system_commands = self.settings.get_value('preferences', 'build_option_system_commands')
                additional_arguments = ''
                lualatex_prefix = ' -' if interpreter == 'lualatex' else ' '
                latexmk_prefix = ' -latexoption=' if interpreter == 'latexmk' else ' '
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
                query = build_system.QueryBuild(text, filename, interpreter, additional_arguments, do_cleanup)
            elif mode == 'forward_sync':
                if document.build_pathname != None:
                    query = build_system.QueryForwardSync(filename, document.build_pathname, synctex_arguments)
            elif mode == 'backward_sync':
                if document.backward_sync_data != None:
                    query = build_system.QueryBackwardSync(filename, document.build_pathname, document.backward_sync_data)
            else:
                query = build_system.QueryBuildAndForwardSync(text, filename, interpreter, additional_arguments, do_cleanup, synctex_arguments)

            self.build_system.add_query(query)

        if change_code == 'build_state_change' and parameter == 'building_to_stop':
            self.build_system.stop_building()
        
        if change_code == 'building_started':
            self.document.change_build_state('building_in_progress')
                
        if change_code == 'reset_timer':
            self.document.build_widget.view.reset_timer()
            self.document.build_widget.view.label.set_text('0:00')

        if change_code == 'building_stopped':
            self.document.show_build_state('')
            self.document.change_build_state('idle')

        if change_code == 'building_finished':
            result_blob = parameter
            if result_blob['build'] != None or result_blob['forward_sync'] != None:
                if result_blob['build'] != None:
                    try:
                        self.document.preview.set_pdf_filename(result_blob['build']['pdf_filename'])
                    except KeyError: pass

                if result_blob['forward_sync'] != None:
                    self.document.preview.set_synctex_rectangles(result_blob['forward_sync'])
                    self.document.show_build_state('')

                if result_blob['build'] != None:
                    build_blob = result_blob['build']

                    build_log_items = list()
                    if build_blob['error'] == 'interpreter_missing':
                        self.document.show_build_state('')
                        self.document.change_build_state('idle')
                        if DialogLocator.get_dialog('interpreter_missing').run(build_blob['error_arg']):
                            DialogLocator.get_dialog('preferences').run()
                        return

                    if build_blob['error'] == 'interpreter_not_working':
                        self.document.show_build_state('')
                        self.document.change_build_state('idle')
                        if DialogLocator.get_dialog('building_failed').run(build_blob['error_arg']):
                            DialogLocator.get_dialog('preferences').run()
                        return

                    try:
                        build_log_blob = build_blob['log_messages']
                    except KeyError:
                        pass
                    else:
                        for item in build_log_blob:
                            build_log_items.append(item)
                    self.document.build_log_items = build_log_items
                    self.document.build_time = time.time() - self.document.last_build_start_time

                    error_count = 0
                    for item in self.document.build_log_items:
                        if item[0] == 'Error':
                            error_count += 1
                    if error_count > 0:
                        error_color = helpers.theme_color_to_css(self.document.view.get_style_context(), 'error_color')
                        message = '<span color="' + error_color + '">Failed</span> (' + str(error_count) + ' error' + ('s' if error_count > 1 else '') + ')!'
                        self.document.show_build_state(message)
                    else:
                        self.document.show_build_state('Success!')

                    self.document.set_build_pathname(build_blob['build_pathname'])
                    self.document.has_been_built = True

            elif result_blob['backward_sync'] != None:
                self.document.set_synctex_position(result_blob['backward_sync'])

            self.document.change_build_state('idle')



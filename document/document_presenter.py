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


import helpers.helpers as helpers
from helpers.service_locator import ServiceLocator

import time
import os.path


class DocumentPresenter(object):
    ''' Mediator between document and view. '''
    
    def __init__(self, document, document_view):
        self.document = document
        self.view = document_view
        self.settings = ServiceLocator.get_settings()
        self.doclist_item = self.view.doclist_item
        self.modified_state = document.get_modified()

        self.document.build_widget.view.build_button.show_all()
        self.document.build_widget.view.stop_button.hide()

        self.document.register_observer(self)
        self.document.get_buffer().connect('modified-changed', self.on_modified_change)
        self.settings.register_observer(self)
        self.build_log_animating = False
        self.document.build_log.view.connect('size-allocate', self.build_log_on_size_allocate)
        self.build_log_initialized = False
        self.view.connect('draw', self.build_log_on_realize)

        self.build_button_state = ('idle', int(time.time()*1000))
        self.set_clean_button_state()

    '''
    *** notification handlers, get called by observed document
    '''

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'filename_change':
            self.doclist_item.set_name(self.document.get_displayname(), self.modified_state)
            self.set_clean_button_state()

        if change_code == 'displayname_change':
            self.doclist_item.set_name(self.document.get_displayname(), self.modified_state)

        if change_code == 'document_state_change':
            build_log = self.document.build_log
            if build_log.has_items('errors'):
                error_count = build_log.count_items('errors')
                error_color = helpers.theme_color_to_css(self.document.view.get_style_context(), 'error_color')
                message = '<span color="' + error_color + '">Failed</span> (' + str(error_count) + ' error' + ('s' if error_count > 1 else '') + ')!'
            else:
                message = 'Success!'
            self.on_build_state_change(message)
            self.set_clean_button_state()

        if change_code == 'settings_changed':
            section, item, value = parameter
            if (section, item) == ('preferences', 'cleanup_build_files'):
                self.set_clean_button_state()

        if change_code == 'show_build_log_state_change':
            self.build_log_animate(parameter, True)

        if change_code == 'cleaned_up_build_files':
            self.set_clean_button_state()

    def on_modified_change(self, buff):
        if buff.get_modified() != self.modified_state:
            self.modified_state = buff.get_modified()
            self.doclist_item.set_name(self.document.get_displayname(), self.modified_state)
            
    def on_build_state_change(self, message=''):
        document = self.document
        state = document.get_state()
        selfstate = self.build_button_state
        build_widget = self.document.build_widget.view
        if state == 'idle' or state == '':
            build_button_state = ('idle', int(time.time()*1000))
        else:
            build_button_state = ('building', int(time.time()*1000))

        build_widget.build_timer.show_all()
        if selfstate[0] != build_button_state[0]:
            self.build_button_state = build_button_state
            if build_button_state[0] == 'idle':
                build_widget.build_button.set_sensitive(True)
                build_widget.build_button.show_all()
                build_widget.stop_button.hide()
                build_widget.stop_timer()
                build_widget.show_result(message)
                if build_widget.get_parent() != None:
                    build_widget.hide_timer(4000)
            else:
                build_widget.build_button.set_sensitive(False)
                build_widget.build_button.hide()
                build_widget.stop_button.show_all()
                build_widget.reset_timer()
                build_widget.show_timer()
                build_widget.start_timer()

    def set_clean_button_state(self):
        def get_clean_button_state(document):
            file_endings = ['.aux', '.blg', '.bbl', '.dvi', '.fdb_latexmk', '.fls', '.idx' ,'.ilg', '.ind', '.log', '.nav', '.out', '.snm', '.synctex.gz', '.toc']
            if document != None:
                if document.filename != None:
                    pathname = document.get_filename().rsplit('/', 1)
                    for ending in file_endings:
                        filename = pathname[0] + '/' + pathname[1].rsplit('.', 1)[0] + ending
                        if os.path.exists(filename): return True
            return False

        if self.settings.get_value('preferences', 'cleanup_build_files') == True:
            self.document.build_widget.view.clean_button.hide()
        else:
            self.document.build_widget.view.clean_button.show_all()
            self.document.build_widget.view.clean_button.set_sensitive(get_clean_button_state(self.document))

    def build_log_on_realize(self, view, cr, user_data=None):
        if self.build_log_initialized == False:
            self.build_log_initialized = True
            self.build_log_animate(self.document.get_show_build_log(), False)

    def build_log_on_size_allocate(self, view, allocation, user_data=None):
        if self.build_log_animating == False:
            self.document.build_log.view.position = allocation.height
    
    def build_log_animate(self, show_build_log=True, animate=False):
        def set_position_on_tick(paned, frame_clock_cb, user_data=None):
            def ease(time): return (time - 1)**3 + 1;

            show_build_log = user_data
            now = frame_clock_cb.get_frame_time()
            if now < end_time and paned.get_position != end:
                t = ease((now - start_time) / (end_time - start_time))
                paned.set_position(int(start + t * (end - start)))
                return True
            else:
                paned.set_position(end)
                if not show_build_log:
                    self.document.build_log.view.hide()
                else:
                    paned.child_set_property(self.document.build_log.view, 'shrink', False)
                self.view.shortcuts_bar_bottom.button_build_log.set_active(show_build_log)
                self.build_log_animating = False
                return False

        if self.build_log_animating == False:
            frame_clock = self.view.document_paned.get_frame_clock()
            duration = 200
            if show_build_log:
                self.document.build_log.view.show_all()
                start = self.view.get_allocated_height()
                end = self.view.get_allocated_height() - max(self.document.build_log.view.position, 200)
            else:
                start = self.view.document_paned.get_position()
                end = self.view.get_allocated_height()
                self.view.document_paned.child_set_property(self.document.build_log.view, 'shrink', True)
            if frame_clock != None and animate:
                start_time = frame_clock.get_frame_time()
                end_time = start_time + 1000 * duration
                self.build_log_animating = True
                self.view.document_paned.add_tick_callback(set_position_on_tick, show_build_log)
            else:
                self.view.document_paned.set_position(end)
                if not show_build_log:
                    self.document.build_log.view.hide()
                else:
                    self.view.document_paned.child_set_property(self.document.build_log.view, 'shrink', False)
                self.view.shortcuts_bar_bottom.button_build_log.set_active(show_build_log)



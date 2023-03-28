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

import setzer.workspace.build_log.build_log_presenter as build_log_presenter
import setzer.workspace.build_log.build_log_controller as build_log_controller
from setzer.helpers.observable import Observable
from setzer.app.service_locator import ServiceLocator
from setzer.helpers.timer import timer


class BuildLog(Observable):

    def __init__(self, workspace):
        Observable.__init__(self)
        self.workspace = workspace
        self.settings = ServiceLocator.get_settings()
        self.document = None

        self.items = list()
        self.hover_item = None

        self.view = ServiceLocator.get_main_window().build_log
        self.presenter = build_log_presenter.BuildLogPresenter(self, self.view)
        self.controller = build_log_controller.BuildLogController(self, self.view)

    def on_build_log_update(self, build_system):
        if build_system.document == self.document:
            self.update_items(True)

    def set_document(self, document):
        if document == self.document: return

        if self.document != None:
            self.document.build_system.disconnect('build_log_update', self.on_build_log_update)

        self.document = document
        self.update_items()
        self.document.build_system.connect('build_log_update', self.on_build_log_update)

    #@timer
    def update_items(self, just_built=False):
        self.items = self.document.build_system.build_log_data['items']
        self.signal_finish_adding()

        if just_built and self.has_items(self.settings.get_value('preferences', 'autoshow_build_log')):
            self.workspace.set_show_build_log(True)

        self.set_hover_item(None)

    def set_hover_item(self, item_num): 
        if self.hover_item != item_num:
            self.hover_item = item_num
            self.add_change_code('hover_item_changed')

    def signal_finish_adding(self):
        self.add_change_code('build_log_finished_adding', self.document.build_system.document_has_been_built)

    def has_items(self, types='all'):
        return self.count_items(types) > 0

    def count_items(self, types='all'):
        if types == 'errors':
            return self.document.build_system.get_error_count()
        elif types == 'errors_warnings':
            return self.document.build_system.get_error_count() + self.document.build_system.get_warning_count()
        elif types == 'all':
            return self.document.build_system.get_error_count() + self.document.build_system.get_warning_count() + self.document.build_system.get_badbox_count()
        elif types == 'warnings':
            return self.document.build_system.get_warning_count()
        elif types == 'badboxes':
            return self.document.build_system.get_badbox_count()
        return 0



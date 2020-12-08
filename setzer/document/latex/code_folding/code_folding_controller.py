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
from gi.repository import Gtk
from gi.repository import Gdk

from setzer.app.service_locator import ServiceLocator


class CodeFoldingController(object):

    def __init__(self, model):
        self.model = model
        self.source_view = self.model.document.view.source_view
        self.settings = ServiceLocator.get_settings()

        if self.settings.get_value('preferences', 'enable_code_folding'):
            self.model.enable_code_folding()
        else:
            self.model.disable_code_folding()
        self.settings.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'settings_changed':
            section, item, value = parameter
            if (section, item) == ('preferences', 'enable_code_folding'):
                if value == True:
                    self.model.enable_code_folding()
                else:
                    self.model.disable_code_folding()



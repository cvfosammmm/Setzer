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

import os.path

import setzer.workspace.help_panel.help_panel_controller as help_panel_controller
import setzer.workspace.help_panel.help_panel_presenter as help_panel_presenter
from setzer.app.service_locator import ServiceLocator


class HelpPanel(object):

    def __init__(self, workspace):
        self.workspace = workspace
        self.view = ServiceLocator.get_main_window().help_panel

        self.path = 'file://' + os.path.join(ServiceLocator.get_resources_path(), 'help')
        self.home_uri = self.path + '/latex2e_0.html'

        self.controller = help_panel_controller.HelpPanelController(self, self.view)
        self.presenter = help_panel_presenter.HelpPanelPresenter(self, self.view)



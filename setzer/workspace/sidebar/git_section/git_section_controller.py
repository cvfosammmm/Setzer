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


class GitSectionController(object):

    def __init__(self, git_section):
        self.git_section = git_section
        self.view = git_section.view

        self.view.button_pull.connect('clicked', self.on_pull_button_clicked)
        self.view.button_push.connect('clicked', self.on_push_button_clicked)

    def on_pull_button_clicked(self, button):
        self.git_section.pull()

    def on_push_button_clicked(self, button):
        self.git_section.push()

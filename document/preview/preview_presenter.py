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
gi.require_version('Poppler', '0.18')
from gi.repository import Poppler

import os.path
import math


class PreviewPresenter(object):

    def __init__(self, preview, view):
        self.preview = preview
        self.view = view

        self.layout_data = dict()

        self.preview.register_observer(self)

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'pdf_changed':
            pass
            '''check if pdf != none
            calc layout in device pixels
            queue_draw'''

        if change_code == 'position_changed':
            pass#move



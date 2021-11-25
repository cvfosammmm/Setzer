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
import time

from setzer.document.document import Document
import setzer.document.content.content as content
import setzer.document.state_manager.state_manager_bibtex as state_manager_bibtex
from setzer.helpers.observable import Observable
from setzer.app.service_locator import ServiceLocator


class DocumentBibTeX(Document):

    def __init__(self, document_type):
        Document.__init__(self, document_type)

        self.state_manager = state_manager_bibtex.StateManagerBibTeX(self)

    def get_file_ending(self):
        return 'bib'

    def get_is_root(self):
        return False

    def is_latex_document(self):
        return False

    def is_bibtex_document(self):
        return True



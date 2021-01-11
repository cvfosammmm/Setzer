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
import setzer.document.latex_sty.state_manager.state_manager_latex_sty as state_manager_latex_sty
from setzer.helpers.observable import Observable
from setzer.app.service_locator import ServiceLocator


class DocumentLaTeXSty(Document):

    def __init__(self):
        Document.__init__(self)

        self.state_manager = state_manager_latex_sty.StateManagerLaTeXSty(self)

    def init_shortcuts(self, shortcuts_manager):
        shortcuts_manager.set_accels_for_insert_before_after_action(['\\textbf{', '}'], [])
        shortcuts_manager.set_accels_for_insert_before_after_action(['\\textit{', '}'], [])
        shortcuts_manager.set_accels_for_insert_before_after_action(['\\underline{', '}'], [])
        shortcuts_manager.set_accels_for_insert_before_after_action(['\\emph{', '}'], [])
        shortcuts_manager.set_accels_for_insert_before_after_action(['\\texttt{', '}'], [])
        shortcuts_manager.set_accels_for_insert_before_after_action(['$ ', ' $'], [])
        shortcuts_manager.set_accels_for_insert_before_after_action(['\\[ ', ' \\]'], [])
        shortcuts_manager.set_accels_for_insert_before_after_action(['\\begin{equation}\n\t', '\n\\end{equation}'], [])
        shortcuts_manager.set_accels_for_insert_before_after_action(['_{', '}'], [])
        shortcuts_manager.set_accels_for_insert_before_after_action(['^{', '}'], [])
        shortcuts_manager.set_accels_for_insert_before_after_action(['\\sqrt{', '}'], [])
        shortcuts_manager.set_accels_for_insert_symbol_action(['\\frac{•}{•}'], [])
        shortcuts_manager.set_accels_for_insert_symbol_action(['\\left •'], [])
        shortcuts_manager.set_accels_for_insert_symbol_action(['\\right •'], [])
        shortcuts_manager.set_accels_for_insert_symbol_action(['\\item •'], [])
        shortcuts_manager.set_accels_for_insert_symbol_action(['\\\\\n'], [])
        shortcuts_manager.main_window.app.set_accels_for_action('win.comment-uncomment', [])

    def get_bibitems(self):
        return set()

    def get_labels(self):
        return set()

    def comment_uncomment(self):
        pass

    def get_folded_regions(self):
        return []

    def get_included_files(self):
        return set()

    def get_file_ending(self):
        return 'sty'

    def get_is_root(self):
        return False

    def is_latex_document(self):
        return False

    def is_bibtex_document(self):
        return False

    def get_gsv_language_name(self):
        return 'latex'



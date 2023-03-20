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

from setzer.document.document import Document
import setzer.document.content.content as content
import setzer.document.parser.parser_latex as parser_latex
import setzer.document.autocomplete.autocomplete as autocomplete
import setzer.document.build_system.build_system as build_system
import setzer.document.build_widget.build_widget as build_widget
import setzer.document.code_folding.code_folding as code_folding
import setzer.document.preview.preview as preview


class DocumentLaTeX(Document):

    def __init__(self):
        Document.__init__(self)

        self.content = content.Content('latex', self)
        self.parser = parser_latex.ParserLaTeX(self)
        self.init_default_modules()

        self.preview = preview.Preview(self)
        self.autocomplete = autocomplete.Autocomplete(self, self.view)
        self.build_system = build_system.BuildSystem(self)
        self.build_widget = build_widget.BuildWidget(self)
        self.code_folding = code_folding.CodeFolding(self)

    def is_latex_document(self):
        return True

    def is_bibtex_document(self):
        return False

    def get_document_type(self):
        return 'latex'



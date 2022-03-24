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

from setzer.document.document import Document
import setzer.document.content.content as content
import setzer.document.parser.parser_bibtex as parser_bibtex


class DocumentBibTeX(Document):

    def __init__(self):
        Document.__init__(self)

        self.content = content.Content('bibtex', self)
        self.parser = parser_bibtex.ParserBibTeX(self)
        self.init_default_modules()

    def is_latex_document(self):
        return False

    def is_bibtex_document(self):
        return True

    def get_document_type(self):
        return 'bibtex'



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

from setzer.document.source_buffer.source_buffer import SourceBuffer
import setzer.document.source_buffer.parser.parser_latex as parser_latex


class SourceBufferLaTeX(SourceBuffer):

    def __init__(self):
        SourceBuffer.__init__(self)

        self.symbols = dict()
        self.symbols['bibitems'] = set()
        self.symbols['labels'] = set()
        self.symbols['included_latex_files'] = set()
        self.symbols['bibliographies'] = set()
        self.symbols['packages'] = set()
        self.symbols['packages_detailed'] = dict()
        self.symbols['blocks'] = list()

        self.parser = parser_latex.ParserLaTeX(self)

    def get_bibitems(self):
        return self.symbols['bibitems']

    def add_packages(self, packages):
        first_package = True
        text = ''
        for packagename in packages:
            if not first_package: text += '\n'
            text += '\\usepackage{' + packagename + '}'
            first_package = False
        
        package_data = self.get_package_details()
        if package_data:
            max_end = 0
            for package in package_data.items():
                if package[1].end() > max_end:
                    max_end = package[1].end()
            insert_iter = self.source_buffer.get_iter_at_offset(max_end)
            if not insert_iter.ends_line():
                insert_iter.forward_to_line_end()
            self.insert_text_at_iter(insert_iter, '\n' + text)
        else:
            end_iter = self.source_buffer.get_end_iter()
            result = end_iter.backward_search('\\documentclass', Gtk.TextSearchFlags.VISIBLE_ONLY, None)
            if result != None:
                result[0].forward_to_line_end()
                self.insert_text_at_iter(result[0], '\n' + text)
            else:
                self.insert_text_at_cursor(text)

    def remove_packages(self, packages):
        packages_dict = self.get_package_details()
        for package in packages:
            try:
                match_obj = packages_dict[package]
            except KeyError: return
            start_iter = self.source_buffer.get_iter_at_offset(match_obj.start())
            end_iter = self.source_buffer.get_iter_at_offset(match_obj.end())
            text = self.source_buffer.get_text(start_iter, end_iter, False)
            if text == match_obj.group(0):  
                if start_iter.get_line_offset() == 0:
                    start_iter.backward_char()
                self.source_buffer.delete(start_iter, end_iter)

    def get_packages(self):
        return self.symbols['packages']

    def get_package_details(self):
        return self.symbols['packages_detailed']

    def get_blocks(self):
        return self.symbols['blocks']

    def set_blocks(self, blocks):
        self.symbols['blocks'] = blocks

    def get_included_latex_files(self):
        return self.symbols['included_latex_files']

    def get_bibliography_files(self):
        return self.symbols['bibliographies']

    def get_labels(self):
        return self.symbols['labels']

    def get_gsv_language_name(self):
        return 'latex'



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

import os
import os.path
import shutil


class BuilderBuild(object):

    def __init__(self):
        self.process = None

    def throw_build_error(self, query, error, error_arg):
        with query.build_result_lock:
            query.build_result = {'error': error,
                                 'error_arg': error_arg}

    def move_build_files(self, query, tex_file_name):
        if query.build_data['do_cleanup']:
            self.cleanup_build_files(query, query.tex_filename)
            self.cleanup_glossaries_files(query)
        else:
            self.rename_build_files(query, tex_file_name)

    def cleanup_build_files(self, query, tex_file_name):
        file_endings = ['.aux', '.blg', '.bbl', '.dvi', '.fdb_latexmk', '.fls', '.idx' , '.ilg',
                        '.ind', '.log', '.nav', '.out', '.snm', '.synctex.gz', '.toc',
                        '.ist', '.glo', '.glg', '.acn', '.alg',
                        '.bcf', '.run.xml']
        for ending in file_endings:
            try: os.remove(os.path.splitext(tex_file_name)[0] + ending)
            except FileNotFoundError: pass

    def cleanup_glossaries_files(self, query):
        for ending in ['.gls', '.acr']:
            try: os.remove(os.path.splitext(query.tex_filename)[0] + ending)
            except FileNotFoundError: pass

    def rename_build_files(self, query, tex_file_name):
        file_endings = ['.aux', '.blg', '.bbl', '.dvi', '.fdb_latexmk', '.fls', '.idx' ,
                        '.ilg', '.ind', '.log', '.nav', '.out', '.snm', '.synctex.gz', '.toc',
                        '.ist', '.glo', '.glg', '.acn', '.alg', '.bcf', '.run.xml']
        for ending in file_endings:
            move_from = os.path.splitext(tex_file_name)[0] + ending
            move_to = os.path.splitext(query.tex_filename)[0] + ending
            try: shutil.move(move_from, move_to)
            except FileNotFoundError: pass



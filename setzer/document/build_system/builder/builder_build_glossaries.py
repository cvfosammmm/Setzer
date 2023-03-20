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

import os
import os.path
import shutil
import subprocess

import setzer.document.build_system.builder.builder_build as builder_build


class BuilderBuildGlossaries(builder_build.BuilderBuild):

    def __init__(self):
        builder_build.BuilderBuild.__init__(self)

    def run(self, query):
        tex_filename = query.tex_filename

        basename = os.path.basename(tex_filename).rsplit('.', 1)[0]
        arguments = ['makeglossaries']
        arguments.append(basename)
        try:
            self.process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.path.dirname(tex_filename))
        except FileNotFoundError:
            self.cleanup_files(query)
            self.throw_build_error(query, 'interpreter_not_working', 'makeglossaries missing')
            return
        self.process.wait()
        for ending in ['.gls', '.acr']:
            move_from = os.path.join(os.path.dirname(tex_filename), basename + ending)
            move_to = os.path.join(os.path.dirname(query.tex_filename), basename + ending)
            try: shutil.move(move_from, move_to)
            except FileNotFoundError: pass

        query.jobs.insert(0, 'build_latex')

    def stop_running(self):
        if self.process != None:
            self.process.kill()
            self.process = None



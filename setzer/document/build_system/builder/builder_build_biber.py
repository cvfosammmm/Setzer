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
import subprocess

import setzer.document.build_system.builder.builder_build as builder_build
from setzer.app.service_locator import ServiceLocator


class BuilderBuildBiber(builder_build.BuilderBuild):

    def __init__(self):
        builder_build.BuilderBuild.__init__(self)

    def run(self, query):
        tex_filename = query.build_data['tmp_tex_filename']

        arguments = ['biber']
        arguments.append(tex_filename.rsplit('/', 1)[1][:-4])
        custom_env = os.environ.copy()
        custom_env['BIBINPUTS'] = os.path.dirname(query.tex_filename) + ':' + os.path.dirname(tex_filename)
        try:
            self.process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.path.dirname(tex_filename), env=custom_env)
        except FileNotFoundError as e:
            print(e)
            self.move_build_files(query, tex_filename)
            self.throw_build_error(query, 'interpreter_not_working', 'biber missing')
            return
        self.process.wait()

        self.parse_biber_log(query, tex_filename[:-3] + 'blg')

        query.jobs.insert(0, 'build_latex')

    def parse_biber_log(self, query, log_filename):
        pass



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

from helpers.helpers import timer


class CodeFoldingPresenter(object):

    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.line_invisible = dict()

        self.view.connect('query-data', self.query_data)

    #@timer
    def query_data(self, renderer, start_iter, end_iter, state):
        if self.line_invisible.get(start_iter.get_line(), False): return
        if start_iter.get_line() in self.model.folding_regions.keys():
            if self.model.folding_regions[start_iter.get_line()]['is_folded']:
                renderer.set_pixbuf(self.view.pixbuf_folded)
            else:
                renderer.set_pixbuf(self.view.pixbuf_unfolded)
        else:
            renderer.set_pixbuf(self.view.pixbuf_neutral)

    def show_folding_bar(self):
        self.view.set_visible(True)

    def hide_folding_bar(self):
        self.view.set_visible(False)



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

import gi
gi.require_version('Poppler', '0.18')
from gi.repository import Poppler

from setzer.helpers.observable import Observable
from setzer.helpers.timer import timer


class PreviewLinksParser(Observable):

    def __init__(self, preview):
        Observable.__init__(self)
        self.preview = preview
        self.links = dict()

        self.preview.connect('pdf_changed', self.on_pdf_changed)

    def on_pdf_changed(self, notifying_object):
        if self.preview.poppler_document != None:
            self.links = dict()
            for page_num in range(self.preview.poppler_document.get_n_pages()):
                self.links[page_num] = None
        else:
            self.links = dict()

    def get_links_for_page(self, page_number):
        if page_number in self.links:
            if self.links[page_number] == None:
                links = list()
                link_mapping_list = self.preview.poppler_document.get_page(page_number).get_link_mapping()
                for link_mapping in link_mapping_list:
                    action = link_mapping.action
                    area = link_mapping.area
                    if action.type == Poppler.ActionType.URI:
                        links.append([area, action.uri.uri, 'uri'])
                    elif action.type == Poppler.ActionType.GOTO_DEST:
                        dest = self.preview.poppler_document.find_dest(action.goto_dest.dest.named_dest)
                        links.append([area, dest, 'goto'])
                self.links[page_number] = links
            return self.links[page_number]
        else:
            return list()



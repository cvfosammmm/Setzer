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

import pickle
import base64
import os.path

from setzer.app.service_locator import ServiceLocator


class StateManagerLaTeX():

    def __init__(self, document):
        self.document = document
        self.data_pathname = ServiceLocator.get_config_folder()

    def load_document_state(self):
        if self.document.filename == None: return

        try: filehandle = open(self.data_pathname + '/' + base64.urlsafe_b64encode(str.encode(self.document.filename)).decode() + '.pickle', 'rb')
        except IOError: pass
        else:
            try: document_data = pickle.load(filehandle)
            except EOFError: pass
            else:
                try:
                    save_date = document_data['save_date']
                except KeyError:
                    pass
                else:
                    if save_date > os.path.getmtime(self.document.filename) - 0.001:
                        self.load_code_folding_state(document_data)
                        self.load_build_log_state(document_data)
                        self.load_preview_state(document_data)

    def load_code_folding_state(self, document_data):
        try:
            self.document.set_initial_folded_regions(document_data['folded_regions'])
        except KeyError:
            self.document.set_initial_folded_regions([])

    def load_build_log_state(self, document_data):
        try:
            self.document.build_log_items = document_data['build_log_items']
        except KeyError:
            self.document.build_log_items = list()
        try:
            self.document.has_been_built = document_data['has_been_built']
        except KeyError:
            self.document.has_been_built = list()
        try:
            self.document.build_time = document_data['build_time']
        except KeyError:
            self.document.build_time = None
        try:
            self.document.has_synctex_file = document_data['has_synctex_file']
        except KeyError:
            self.document.has_synctex_file = False

    def load_preview_state(self, document_data):
        try:
            pdf_filename = document_data['pdf_filename']
        except KeyError:
            pdf_filename = None
        try:
            pdf_date = document_data['pdf_date']
        except KeyError:
            pdf_date = None
        try:
            xoffset = document_data['xoffset']
        except KeyError:
            xoffset = None
        try:
            yoffset = document_data['yoffset']
        except KeyError:
            yoffset = None

        if pdf_filename == None: return
        if not os.path.isfile(pdf_filename): return
        if pdf_date == None: return
        if pdf_date <= os.path.getmtime(pdf_filename) - 10: return

        self.document.preview.set_pdf_filename(pdf_filename)
        self.document.preview.scroll_to_position_from_offsets(xoffset, yoffset)

    def save_document_state(self):
        document_data = dict()
        document_data['save_date'] = self.document.save_date
        document_data['folded_regions'] = self.document.get_folded_regions()
        document_data['build_log_items'] = self.document.build_log_items
        document_data['has_been_built'] = self.document.has_been_built
        document_data['build_time'] = self.document.build_time
        document_data['has_synctex_file'] = self.document.has_synctex_file

        document_data['pdf_filename'] = self.document.preview.pdf_filename
        document_data['pdf_date'] = self.document.preview.pdf_date
        document_data['xoffset'] = self.document.preview.xoffset
        document_data['yoffset'] = self.document.preview.yoffset

        if self.document.filename != None:
            try: filehandle = open(self.data_pathname + '/' + base64.urlsafe_b64encode(str.encode(self.document.filename)).decode() + '.pickle', 'wb')
            except IOError: pass
            else: pickle.dump(document_data, filehandle)



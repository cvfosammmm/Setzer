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

from app.service_locator import ServiceLocator


class StateManagerLaTeX():

    def __init__(self, document):
        self.document = document
        self.data_pathname = ServiceLocator.get_dot_folder()

    def load_document_state(self):
        try: filehandle = open(self.data_pathname + '/' + base64.urlsafe_b64encode(str.encode(self.document.filename)).decode() + '.pickle', 'rb')
        except IOError: pass
        else:
            try: document_data = pickle.load(filehandle)
            except EOFError: pass
            else:
                pass

    def save_document_state(self):
        document_data = dict()

        if self.document.filename != None:
            try: filehandle = open(self.data_pathname + '/' + base64.urlsafe_b64encode(str.encode(self.document.filename)).decode() + '.pickle', 'wb')
            except IOError: pass
            else: pickle.dump(document_data, filehandle)



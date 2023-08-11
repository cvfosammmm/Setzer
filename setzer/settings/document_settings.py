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

import pickle
import base64
import os.path

from setzer.app.service_locator import ServiceLocator


class DocumentSettings():

    def load_document_state(document):
        if not document.is_latex_document(): return
        if document.filename == None: return

        filename = base64.urlsafe_b64encode(str.encode(document.filename)).decode()
        try:
            filehandle = open(ServiceLocator.get_config_folder() + '/' + filename + '.pickle', 'rb')
            document_data = pickle.load(filehandle)
            DocumentSettings.update_document(document, document_data)
        except Exception:
            pass

    def update_document(document, document_data):
        if document_data['save_date'] <= os.path.getmtime(document.filename) - 0.001: return

        document.code_folding.set_initial_folded_regions(document_data['folded_regions'])
        document.build_system.build_log_data = document_data['build_log_data']
        document.build_system.document_has_been_built = document_data['has_been_built']
        document.build_system.build_time = document_data['build_time']
        document.build_system.has_synctex_file = document_data['has_synctex_file']
        document.build_system.update_can_sync()

        pdf_filename = document_data['pdf_filename']
        pdf_date = document_data['pdf_date']
        xoffset = document_data['xoffset']
        yoffset = document_data['yoffset']
        zoom_level = document_data['zoom_level']

        if pdf_filename == None: return
        if not os.path.isfile(pdf_filename): return
        if pdf_date == None: return
        if pdf_date <= os.path.getmtime(pdf_filename) - 10: return

        document.preview.set_pdf_filename(pdf_filename)
        document.preview.zoom_manager.set_zoom_level(zoom_level)
        document.preview.scroll_to_position(xoffset, yoffset)

    def save_document_state(document):
        if document.filename == None: return
        if not document.is_latex_document(): return

        document_data = dict()
        document_data['save_date'] = document.save_date
        document_data['folded_regions'] = document.code_folding.get_folded_regions()
        document_data['build_log_data'] = document.build_system.build_log_data
        document_data['has_been_built'] = document.build_system.document_has_been_built
        document_data['build_time'] = document.build_system.build_time
        document_data['has_synctex_file'] = document.build_system.has_synctex_file

        document_data['pdf_filename'] = document.preview.pdf_filename
        document_data['pdf_date'] = document.preview.get_pdf_date()
        document_data['xoffset'] = document.preview.view.content.scrolling_offset_x
        document_data['yoffset'] = document.preview.view.content.scrolling_offset_y
        document_data['zoom_level'] = document.preview.zoom_manager.zoom_level

        filename = base64.urlsafe_b64encode(str.encode(document.filename)).decode()
        if document.filename != None:
            try: filehandle = open(ServiceLocator.get_config_folder() + '/' + filename + '.pickle', 'wb')
            except IOError: pass
            else:
                pickle.dump(document_data, filehandle)



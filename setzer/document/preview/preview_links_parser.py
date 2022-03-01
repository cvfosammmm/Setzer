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

from pdfminer.pdfpage import PDFPage
from pdfminer.pdftypes import PDFObjRef
import _thread as thread, queue

from setzer.helpers.observable import Observable


class PreviewLinksParser(Observable):

    def __init__(self, preview):
        Observable.__init__(self)
        self.preview = preview

        self.links_lock = thread.allocate_lock()
        self.links_parsed = True
        with self.links_lock:
            self.links = dict()
        self.links_parser_lock = thread.allocate_lock()

        self.preview.connect('pdf_changed', self.on_pdf_changed)

    def on_pdf_changed(self, notifying_object):
        if self.preview.pdf_loaded:
            with self.links_lock:
                self.links = dict()
            self.links_parsed = False
            thread.start_new_thread(self.update_links, ())
        else:
            self.links_parsed = True
            self.links = dict()

    def get_links_for_page(self, page_number):
        with self.links_lock:
            try:
                return self.links[page_number]
            except KeyError:
                return list()

    def update_links(self):
        with self.links_parser_lock:
            if self.links_parsed: return

            links = dict()

            with open(self.preview.pdf_filename, 'rb') as file:
                for page_num, page in enumerate(PDFPage.get_pages(file)):
                    links[page_num] = list()
                    annots_final = self.resolve_annots(page.annots)
                    for annot in annots_final:
                        try:
                            rect = annot['Rect']
                        except KeyError:
                            pass
                        else:
                            try:
                                data = annot['A']
                            except KeyError:
                                pass
                            else:
                                try:
                                    named_dest = data['D']
                                except KeyError:
                                    pass
                                else:
                                    dest = self.preview.poppler_document.find_dest(named_dest.decode('utf-8'))
                                    links[page_num].append([rect, dest, 'goto'])
                                try:
                                    uri = data['URI']
                                except KeyError:
                                    pass
                                else:
                                    links[page_num].append([rect, uri.decode('utf-8'), 'uri'])
            with self.links_lock:
                self.links = links
                self.links_parsed = True

    def resolve_annots(self, annots):
        if annots == None: return []

        if type(annots) is PDFObjRef:
            annots = annots.resolve()

        if type(annots) is dict:
            return [annots]
        else:
            return_value = list()
            for annot in annots:
                if type(annots) is dict:
                    return_value.append(annot)
                else:
                    return_value += self.resolve_annots(annot)
            return return_value



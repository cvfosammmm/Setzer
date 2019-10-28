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

import os.path
import time
import pickle

from document.document import Document
from helpers.observable import *


class Workspace(Observable):
    ''' A workspace contains a user's open documents. '''

    def __init__(self):
        Observable.__init__(self)

        self.pathname = os.path.expanduser('~') + '/.setzer'

        self.open_documents = list()
        self.recently_opened_documents = dict()
        self.untitled_documents_no = 0
        
        self.active_document = None

    def add_document(self, document):
        if self.open_documents.count(document) != 0: return False
        if document.get_filename() == None:
            document.set_displayname('Untitled Document ' + str(self.untitled_documents_no + 1))
            self.untitled_documents_no += 1
        if document.get_buffer() != None:
            self.open_documents.append(document)
            self.add_change_code('new_document', document)
            self.update_recently_opened_document(document.get_filename(), notify=True)

    def remove_document(self, document):
        document.save_document_data()
        self.open_documents.remove(document)
        if self.active_document == document:
            candidate = self.get_last_active_document()
            if candidate == None:
                self.set_active_document(None)
            else:
                self.set_active_document(candidate)
        self.add_change_code('document_removed', document)
        
    def get_document_by_filename(self, filename):
        for document in self.open_documents:
            if filename == document.get_filename():
                return document
        return None

    def get_active_document(self):
        return self.active_document
        
    def set_active_document(self, document):
        if self.active_document != None:
            self.add_change_code('new_inactive_document', self.active_document)

        self.active_document = document
        if self.active_document != None:
            self.active_document.set_last_activated(time.time())
            self.add_change_code('new_active_document', document)
        
    def get_last_active_document(self):
        for document in sorted(self.open_documents, key=lambda val: -val.last_activated):
            return document
        return None

    def get_earliest_active_document(self):
        for document in sorted(self.open_documents, key=lambda val: val.last_activated):
            return document
        return None

    def update_recently_opened_document(self, filename, date=None, notify=True):
        if not isinstance(filename, str): return False
        if not os.path.isfile(filename): return False
        if date == None: date = time.time()
        if len(self.recently_opened_documents) >= 1000: 
            del(self.recently_opened_documents[sorted(self.recently_opened_documents.values(), key=lambda val: -val['date'])[0]['filename']])
        self.recently_opened_documents[filename] = {'filename': filename, 'date': date}
        if notify:
            self.add_change_code('update_recently_opened_documents', self.recently_opened_documents)
    
    def populate_from_disk(self):
        try: filehandle = open(self.pathname + '/workspace.pickle', 'rb')
        except IOError: pass
        else:
            try: data = pickle.load(filehandle)
            except EOFError: self.add_document(Document(self.pathname, with_buffer=True))
            else:
                for item in sorted(data['open_documents'].values(), key=lambda val: val['last_activated']):
                    document = Document(self.pathname, with_buffer=True)
                    document.set_filename(item['filename'])
                    if document.populate_from_filename() != False:
                        self.add_document(document)
                for item in data['recently_opened_documents'].values():
                    self.update_recently_opened_document(item['filename'], item['date'], notify=False)
        self.add_change_code('update_recently_opened_documents', self.recently_opened_documents)

    def save_to_disk(self):
        try: filehandle = open(self.pathname + '/workspace.pickle', 'wb')
        except IOError: pass
        else:
            open_documents = dict()
            for document in self.open_documents:
                filename = document.get_filename()
                if filename != None:
                    open_documents[filename] = {
                        'filename': filename,
                        'last_activated': document.get_last_activated()
                    }
            data = {
                'open_documents': open_documents,
                'recently_opened_documents': self.recently_opened_documents
            }
            pickle.dump(data, filehandle)
            
    def get_unsaved_documents(self):
        unsaved_documents = list()
        for document in self.open_documents:
            if document.get_modified():
                unsaved_documents.append(document)

        return unsaved_documents if len(unsaved_documents) >= 1 else None
        
    def get_all_documents(self):
        return self.open_documents.copy() if len(self.open_documents) >= 1 else None



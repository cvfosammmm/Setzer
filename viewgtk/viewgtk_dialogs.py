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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk


class CloseConfirmation(Gtk.MessageDialog):
    ''' This dialog is asking users to save unsaved documents or discard their changes. '''

    def __init__(self, main_window, documents):
        Gtk.MessageDialog.__init__(self, main_window, 0, Gtk.MessageType.QUESTION)
        
        if len(documents) == 1:
            self.set_property('text', 'Document »' + documents[0].get_displayname() + '« has unsaved changes.')
            self.format_secondary_markup('If you close without saving, these changes will be lost.')

        if len(documents) >= 2:
            self.set_property('text', 'There are ' + str(len(documents)) + ' documents with unsaved changes.\nSave changes before closing?')
            self.format_secondary_markup('Select the documents you want to save:')
            label = self.get_message_area().get_children()[1]
            label.set_xalign(0)
            label.set_halign(Gtk.Align.START)
            
            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_shadow_type(Gtk.ShadowType.IN)
            scrolled_window.set_size_request(446, 112)
            self.chooser = Gtk.ListBox()
            self.chooser.set_selection_mode(Gtk.SelectionMode.NONE)
            counter = 0
            for document in documents:
                button = Gtk.CheckButton(document.get_displayname())
                button.set_name('document_to_save_checkbutton_' + str(counter))
                button.set_active(True)
                button.set_can_focus(False)
                self.chooser.add(button)
                counter += 1
            for listboxrow in self.chooser.get_children():
                listboxrow.set_can_focus(False)
            scrolled_window.add(self.chooser)
                
            secondary_text_label = Gtk.Label('If you close without saving, all changes will be lost.')
            self.message_area = self.get_message_area()
            self.message_area.pack_start(scrolled_window, False, False, 0)
            self.message_area.pack_start(secondary_text_label, False, False, 0)
            self.message_area.show_all()

        self.add_buttons('Close _without Saving', Gtk.ResponseType.NO, '_Cancel', Gtk.ResponseType.CANCEL, '_Save', Gtk.ResponseType.YES)
        self.set_default_response(Gtk.ResponseType.YES)
        

class BuildSaveDialog(Gtk.MessageDialog):
    ''' This dialog is asking users to save never saved documents before building. '''

    def __init__(self, main_window, document):
        Gtk.MessageDialog.__init__(self, main_window, 0, Gtk.MessageType.QUESTION)
        
        self.set_property('text', 'Document »' + document.get_displayname() + '« has no filename.')
        self.format_secondary_markup('Please save your document to a file, so the build system knows where to put the .pdf (it will be in the same folder as your document).')

        self.add_buttons('_Cancel', Gtk.ResponseType.CANCEL, '_Save document now', Gtk.ResponseType.YES)
        self.set_default_response(Gtk.ResponseType.YES)
        

class InterpreterMissingDialog(Gtk.MessageDialog):

    def __init__(self, main_window, interpreter_name):
        Gtk.MessageDialog.__init__(self, main_window, 0, Gtk.MessageType.QUESTION)
        
        self.set_property('text', 'LateX Interpreter is missing.')
        self.format_secondary_markup('''Setzer is configured to use »''' + interpreter_name + '''« which seems to be missing on this system.

To choose a different interpreter go to Preferences.

For instructions on installing LaTeX see <a href="https://en.wikibooks.org/wiki/LaTeX/Installation">https://en.wikibooks.org/wiki/LaTeX/Installation</a>''')

        self.add_buttons('_Cancel', Gtk.ResponseType.CANCEL, '_Go to Preferences', Gtk.ResponseType.YES)
        self.set_default_response(Gtk.ResponseType.YES)
        


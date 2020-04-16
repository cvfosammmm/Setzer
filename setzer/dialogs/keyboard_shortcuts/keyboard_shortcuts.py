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

from setzer.dialogs.dialog import Dialog

import os.path


class KeyboardShortcutsDialog(Dialog):

    def __init__(self, main_window):
        self.main_window = main_window

        data = list()

        section = {'title': 'Documents', 'items': list()}
        section['items'].append({'title': 'Create new document', 'shortcut': '&lt;ctrl&gt;N'})
        section['items'].append({'title': 'Open a document', 'shortcut': '&lt;ctrl&gt;O'})
        section['items'].append({'title': 'Show recent documents', 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;O'})
        section['items'].append({'title': 'Show open documents', 'shortcut': '&lt;ctrl&gt;T'})
        section['items'].append({'title': 'Switch to the next open document', 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;T'})
        section['items'].append({'title': 'Save the current document', 'shortcut': '&lt;ctrl&gt;S'})
        section['items'].append({'title': 'Save the document with a new filename', 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;S'})
        section['items'].append({'title': 'Close the current document', 'shortcut': '&lt;ctrl&gt;W'})
        data.append(section)

        section = {'title': 'Tools', 'items': list()}
        section['items'].append({'title': 'Build .pdf-file from document', 'shortcut': 'F6'})
        section['items'].append({'title': 'Spellchecking dialog', 'shortcut': 'F7'})
        data.append(section)

        section = {'title': 'Windows and Panels', 'items': list()}
        section['items'].append({'title': 'Show build log', 'shortcut': 'F8'})
        section['items'].append({'title': 'Show side panel', 'shortcut': 'F9'})
        section['items'].append({'title': 'Show preview panel', 'shortcut': 'F10'})
        section['items'].append({'title': 'Close Application', 'shortcut': '&lt;ctrl&gt;Q'})
        data.append(section)

        section = {'title': 'Find and Replace', 'items': list()}
        section['items'].append({'title': 'Find', 'shortcut': '&lt;ctrl&gt;F'})
        section['items'].append({'title': 'Find the next match', 'shortcut': '&lt;ctrl&gt;G'})
        section['items'].append({'title': 'Find the previous match', 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;G'})
        section['items'].append({'title': 'Find and Replace', 'shortcut': '&lt;ctrl&gt;H'})
        data.append(section)

        section = {'title': 'Copy and Paste', 'items': list()}
        section['items'].append({'title': 'Copy selected text to clipboard', 'shortcut': '&lt;ctrl&gt;C'})
        section['items'].append({'title': 'Cut selected text to clipboard', 'shortcut': '&lt;ctrl&gt;X'})
        section['items'].append({'title': 'Paste text from clipboard', 'shortcut': '&lt;ctrl&gt;V'})
        data.append(section)

        section = {'title': 'Undo and Redo', 'items': list()}
        section['items'].append({'title': 'Undo previous text edit', 'shortcut': '&lt;ctrl&gt;Z'})
        section['items'].append({'title': 'Redo previous text edit', 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;Z'})
        data.append(section)

        section = {'title': 'Selection', 'items': list()}
        section['items'].append({'title': 'Select all text', 'shortcut': '&lt;ctrl&gt;A'})
        data.append(section)

        section = {'title': 'Editing', 'items': list()}
        section['items'].append({'title': 'Toggle insert / overwrite', 'shortcut': 'Insert'})
        section['items'].append({'title': 'Move current line up', 'shortcut': '&lt;Alt&gt;Up'})
        section['items'].append({'title': 'Move current line down', 'shortcut': '&lt;Alt&gt;Down'})
        section['items'].append({'title': 'Move current word left', 'shortcut': '&lt;Alt&gt;Left'})
        section['items'].append({'title': 'Move current word right', 'shortcut': '&lt;Alt&gt;Right'})
        section['items'].append({'title': 'Increment number at cursor', 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;A'})
        section['items'].append({'title': 'Decrement number at cursor', 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;X'})
        data.append(section)

        section = {'title': 'LaTeX Shortcuts', 'items': list()}
        section['items'].append({'title': 'New Line (\\\\)', 'shortcut': '&lt;ctrl&gt;Return'})
        section['items'].append({'title': 'Bold Text', 'shortcut': '&lt;ctrl&gt;B'})
        section['items'].append({'title': 'Italic Text', 'shortcut': '&lt;ctrl&gt;I'})
        section['items'].append({'title': 'Underlined Text', 'shortcut': '&lt;ctrl&gt;U'})
        section['items'].append({'title': 'Typewriter Text', 'shortcut': '&lt;ctrl&gt;M'})
        section['items'].append({'title': 'Emphasized Text', 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;E'})
        section['items'].append({'title': 'Quotation Marks', 'shortcut': '&lt;ctrl&gt;quotedbl'})
        section['items'].append({'title': 'List Item', 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;I'})
        section['items'].append({'title': 'Environment', 'shortcut': '&lt;ctrl&gt;E'})
        data.append(section)

        section = {'title': 'Math Shortcuts', 'items': list()}
        section['items'].append({'title': 'Inline Math Section', 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;M'})
        section['items'].append({'title': 'Display Math Section', 'shortcut': '&lt;alt&gt;&lt;shift&gt;M'})
        section['items'].append({'title': 'Equation', 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;N'})
        section['items'].append({'title': 'Subscript', 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;D'})
        section['items'].append({'title': 'Superscript', 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;U'})
        section['items'].append({'title': 'Fraction', 'shortcut': '&lt;alt&gt;&lt;shift&gt;F'})
        section['items'].append({'title': '\\left', 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;L'})
        section['items'].append({'title': '\\right', 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;R'})
        data.append(section)

        self.data = data

    def run(self):
        self.setup()
        self.view.show_all()
        del(self.view)

    def setup(self):
        builder_string = '''<?xml version="1.0" encoding="UTF-8"?>
<interface>

  <object class="GtkShortcutsWindow" id="shortcuts-window">
    <property name="modal">1</property>
    <child>
      <object class="GtkShortcutsSection">
        <property name="visible">1</property>
        <property name="section-name">shortcuts</property>
        <property name="max-height">12</property>
'''

        for section in self.data:
            builder_string += '''        <child>
          <object class="GtkShortcutsGroup">
            <property name="visible">1</property>
            <property name="title" translatable="yes">''' + section['title'] + '''</property>
'''

            for item in section['items']:
                builder_string += '''            <child>
              <object class="GtkShortcutsShortcut">
                <property name="visible">1</property>
                <property name="accelerator">''' + item['shortcut'] + '''</property>
                <property name="title" translatable="yes">''' + item['title'] + '''</property>
              </object>
            </child>
'''

            builder_string += '''          </object>
        </child>
'''

        builder_string += '''      </object>
    </child>
  </object>

</interface>'''

        builder = Gtk.Builder.new_from_string(builder_string, -1)
        self.view = builder.get_object('shortcuts-window')
        self.view.set_transient_for(self.main_window)
        


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
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

import os.path


class KeyboardShortcutsDialog(object):

    def __init__(self, main_window):
        self.main_window = main_window

        data = list()

        section = {'title': _('Documents'), 'items': list()}
        section['items'].append({'title': _('Create new document'), 'shortcut': '&lt;ctrl&gt;N'})
        section['items'].append({'title': _('Open a document'), 'shortcut': '&lt;ctrl&gt;O'})
        section['items'].append({'title': _('Show recent documents'), 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;O'})
        section['items'].append({'title': _('Show open documents'), 'shortcut': '&lt;ctrl&gt;T'})
        section['items'].append({'title': _('Switch to the next open document'), 'shortcut': '&lt;ctrl&gt;Tab'})
        section['items'].append({'title': _('Save the current document'), 'shortcut': '&lt;ctrl&gt;S'})
        section['items'].append({'title': _('Save the document with a new filename'), 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;S'})
        section['items'].append({'title': _('Close the current document'), 'shortcut': '&lt;ctrl&gt;W'})
        data.append(section)

        section = {'title': _('Tools'), 'items': list()}
        section['items'].append({'title': _('Save and build .pdf-file from document'), 'shortcut': 'F5'})
        section['items'].append({'title': _('Build .pdf-file from document'), 'shortcut': 'F6'})
        section['items'].append({'title': _('Show current position in preview'), 'shortcut': 'F7'})
        data.append(section)

        section = {'title': 'Windows and Panels', 'items': list()}
        section['items'].append({'title': _('Show help panel'), 'shortcut': 'F1'})
        section['items'].append({'title': _('Show build log'), 'shortcut': 'F8'})
        section['items'].append({'title': _('Show preview panel'), 'shortcut': 'F9'})
        section['items'].append({'title': _('Show global menu'), 'shortcut': 'F10'})
        section['items'].append({'title': _('Show context menu'), 'shortcut': 'F12'})
        section['items'].append({'title': _('Show keyboard shortcuts'), 'shortcut': '&lt;ctrl&gt;question'})
        section['items'].append({'title': _('Close Application'), 'shortcut': '&lt;ctrl&gt;Q'})
        data.append(section)

        section = {'title': _('Find and Replace'), 'items': list()}
        section['items'].append({'title': _('Find'), 'shortcut': '&lt;ctrl&gt;F'})
        section['items'].append({'title': _('Find the next match'), 'shortcut': '&lt;ctrl&gt;G'})
        section['items'].append({'title': _('Find the previous match'), 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;G'})
        section['items'].append({'title': _('Find and Replace'), 'shortcut': '&lt;ctrl&gt;H'})
        data.append(section)

        section = {'title': _('Zoom'), 'items': list()}
        section['items'].append({'title': _('Zoom in'), 'shortcut': '&lt;ctrl&gt;plus'})
        section['items'].append({'title': _('Zoom out'), 'shortcut': '&lt;ctrl&gt;minus'})
        section['items'].append({'title': _('Reset zoom'), 'shortcut': '&lt;ctrl&gt;0'})
        data.append(section)

        section = {'title': 'Copy and Paste', 'items': list()}
        section['items'].append({'title': _('Copy selected text to clipboard'), 'shortcut': '&lt;ctrl&gt;C'})
        section['items'].append({'title': _('Cut selected text to clipboard'), 'shortcut': '&lt;ctrl&gt;X'})
        section['items'].append({'title': _('Paste text from clipboard'), 'shortcut': '&lt;ctrl&gt;V'})
        data.append(section)

        section = {'title': _('Undo and Redo'), 'items': list()}
        section['items'].append({'title': _('Undo previous text edit'), 'shortcut': '&lt;ctrl&gt;Z'})
        section['items'].append({'title': _('Redo previous text edit'), 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;Z'})
        data.append(section)

        section = {'title': _('Selection'), 'items': list()}
        section['items'].append({'title': _('Select all text'), 'shortcut': '&lt;ctrl&gt;A'})
        data.append(section)

        section = {'title': _('Editing'), 'items': list()}
        section['items'].append({'title': _('Toggle insert / overwrite'), 'shortcut': 'Insert'})
        section['items'].append({'title': _('Move current line up'), 'shortcut': '&lt;Alt&gt;Up'})
        section['items'].append({'title': _('Move current line down'), 'shortcut': '&lt;Alt&gt;Down'})
        section['items'].append({'title': _('Move current word left'), 'shortcut': '&lt;Alt&gt;Left'})
        section['items'].append({'title': _('Move current word right'), 'shortcut': '&lt;Alt&gt;Right'})
        section['items'].append({'title': _('Increment number at cursor'), 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;A'})
        section['items'].append({'title': _('Decrement number at cursor'), 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;X'})
        data.append(section)

        section = {'title': _('LaTeX Shortcuts'), 'items': list()}
        section['items'].append({'title': _('Comment / Uncomment current line(s)'), 'shortcut': '&lt;ctrl&gt;K'})
        section['items'].append({'title': _('New Line') + ' (\\\\)', 'shortcut': '&lt;ctrl&gt;Return'})
        section['items'].append({'title': _('Bold Text'), 'shortcut': '&lt;ctrl&gt;B'})
        section['items'].append({'title': _('Italic Text'), 'shortcut': '&lt;ctrl&gt;I'})
        section['items'].append({'title': _('Underlined Text'), 'shortcut': '&lt;ctrl&gt;U'})
        section['items'].append({'title': _('Typewriter Text'), 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;T'})
        section['items'].append({'title': _('Emphasized Text'), 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;E'})
        section['items'].append({'title': _('Quotation Marks'), 'shortcut': '&lt;ctrl&gt;quotedbl'})
        section['items'].append({'title': _('List Item'), 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;I'})
        section['items'].append({'title': _('Environment'), 'shortcut': '&lt;ctrl&gt;E'})
        data.append(section)

        section = {'title': _('Math Shortcuts'), 'items': list()}
        section['items'].append({'title': _('Inline Math Section'), 'shortcut': '&lt;ctrl&gt;M'})
        section['items'].append({'title': _('Display Math Section'), 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;M'})
        section['items'].append({'title': _('Equation'), 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;N'})
        section['items'].append({'title': _('Subscript'), 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;D'})
        section['items'].append({'title': _('Superscript'), 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;U'})
        section['items'].append({'title': _('Fraction'), 'shortcut': '&lt;alt&gt;&lt;shift&gt;F'})
        section['items'].append({'title': '\\left', 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;L'})
        section['items'].append({'title': '\\right', 'shortcut': '&lt;ctrl&gt;&lt;shift&gt;R'})
        data.append(section)

        self.data = data

    def run(self):
        self.setup()
        self.view.present()

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
            <property name="title" translatable="no">''' + section['title'] + '''</property>
'''

            for item in section['items']:
                builder_string += '''            <child>
              <object class="GtkShortcutsShortcut">
                <property name="visible">1</property>
                <property name="accelerator">''' + item['shortcut'] + '''</property>
                <property name="title" translatable="no">''' + item['title'] + '''</property>
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
        


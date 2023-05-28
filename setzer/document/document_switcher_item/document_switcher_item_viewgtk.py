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
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Pango


class OpenDocsPopoverItem(Gtk.ListBoxRow):
    ''' An item in OpenDocsPopover. '''

    def __init__(self, document):
        Gtk.ListBoxRow.__init__(self)
        self.set_selectable(False)
        self.document = document

        self.box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.icon_box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        if document.is_latex_document():
            self.icon = Gtk.Image.new_from_icon_name('text-x-generic-symbolic', Gtk.IconSize.MENU)
        else:
            self.icon = Gtk.Image.new_from_icon_name('text-x-generic-symbolic', Gtk.IconSize.MENU)
        self.icon.set_margin_bottom(2)
        self.icon.set_margin_right(6)
        self.icon.set_margin_left(1)
        self.icon.get_style_context().add_class('icon')
        self.root_icon = Gtk.Image.new_from_icon_name('object-select-symbolic', Gtk.IconSize.MENU)
        self.root_icon.set_margin_bottom(2)
        self.root_icon.set_margin_right(7)
        self.root_icon.get_style_context().add_class('icon')
        self.icon_box.pack_start(self.icon, False, False, 0)
        self.icon_box.pack_start(self.root_icon, False, False, 0)
        self.box.pack_start(self.icon_box, False, False, 0)
        self.radio_button_hover = Gtk.Image.new_from_icon_name('object-select-symbolic', Gtk.IconSize.MENU)
        self.radio_button_hover.set_margin_bottom(2)
        self.radio_button_hover.set_margin_right(7)
        self.radio_button_hover.set_margin_left(0)
        self.radio_button_hover.get_style_context().add_class('radio-hover')
        self.box.pack_start(self.radio_button_hover, False, False, 0)
        self.label = Gtk.Label('')
        self.label.set_ellipsize(Pango.EllipsizeMode.END)
        self.label.set_halign(Gtk.Align.START)
        self.root_label = Gtk.Label('  (root)')
        self.root_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.root_label.set_halign(Gtk.Align.START)
        self.root_label.get_style_context().add_class('root-label')
        self.flabel = Gtk.Label('')
        self.mlabel = Gtk.Label('')
        self.box.pack_start(self.label, False, False, 0)
        self.box.pack_start(self.root_label, False, False, 0)
        self.document_close_button = Gtk.Button.new_from_icon_name('window-close-symbolic', Gtk.IconSize.MENU)
        self.document_close_button.get_style_context().add_class('flat')
        self.document_close_button.get_style_context().add_class('image-button')
        self.document_close_button.set_relief(Gtk.ReliefStyle.NONE)
        self.box.pack_end(self.document_close_button, False, False, 0)
        self.add(self.box)

        self.set_name(document.get_filename(), document.content.get_modified())
        self.show_all()
        
    def set_name(self, filename, modified_state):
        self.title = ''
        self.folder = ''
        if modified_state == True: self.title += '*'
        if filename != None:
            fsplit = filename.rsplit('/', 1)
            if len(fsplit) > 1:
                self.title += fsplit[1]
                self.folder = fsplit[0]
                self.has_title = True
            else:
                self.title += self.document.get_displayname()
                self.has_title = False
        self.label.set_text(self.title)
        self.flabel.set_text(self.folder)
        self.mlabel.set_text(str(modified_state))
        
    def get_has_title(self):
        return self.has_title
    
    def get_title(self):
        return self.title



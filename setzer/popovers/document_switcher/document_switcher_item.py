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
from gi.repository import Gtk, Pango


class DocumentSwitcherItem(Gtk.ListBoxRow):
    ''' An item in OpenDocsPopover. '''

    def __init__(self, document):
        Gtk.ListBoxRow.__init__(self)
        self.set_selectable(False)
        self.document = document

        self.center_box = Gtk.CenterBox()
        self.center_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.icon_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        if document.is_latex_document():
            self.icon = Gtk.Image.new_from_icon_name('text-x-generic-symbolic')
        else:
            self.icon = Gtk.Image.new_from_icon_name('text-x-generic-symbolic')
        self.icon.set_margin_bottom(2)
        self.icon.set_margin_end(6)
        self.icon.set_margin_start(1)
        self.icon.get_style_context().add_class('icon')
        self.root_icon = Gtk.Image.new_from_icon_name('object-select-symbolic')
        self.root_icon.set_margin_bottom(2)
        self.root_icon.set_margin_end(7)
        self.root_icon.get_style_context().add_class('icon')
        self.icon_box.append(self.icon)
        self.icon_box.append(self.root_icon)
        self.box.append(self.icon_box)
        self.radio_button_hover = Gtk.Image.new_from_icon_name('object-select-symbolic')
        self.radio_button_hover.set_margin_bottom(2)
        self.radio_button_hover.set_margin_end(7)
        self.radio_button_hover.set_margin_start(0)
        self.radio_button_hover.get_style_context().add_class('radio-hover')
        self.box.append(self.radio_button_hover)
        self.label = Gtk.Label.new('')
        self.label.set_ellipsize(Pango.EllipsizeMode.END)
        self.label.set_halign(Gtk.Align.START)
        self.root_label = Gtk.Label.new('  (root)')
        self.root_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.root_label.set_halign(Gtk.Align.START)
        self.root_label.get_style_context().add_class('root-label')
        self.flabel = Gtk.Label.new('')
        self.mlabel = Gtk.Label.new('')
        self.box.append(self.label)
        self.box.append(self.root_label)
        self.document_close_button = Gtk.Button.new_from_icon_name('window-close-symbolic')
        self.document_close_button.get_style_context().add_class('flat')
        self.document_close_button.get_style_context().add_class('image-button')

        self.center_box.set_start_widget(self.box)
        self.center_box.set_end_widget(self.document_close_button)
        self.set_child(self.center_box)

        self.set_name(document.get_displayname(), document.source_buffer.get_modified())

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
        
    def set_is_root(self, is_root):
        if is_root:
            self.icon.hide()
            self.root_icon.show()
            self.root_label.show()
        else:
            self.icon.show()
            self.root_icon.hide()
            self.root_label.hide()

    def get_has_title(self):
        return self.has_title
    
    def get_title(self):
        return self.title



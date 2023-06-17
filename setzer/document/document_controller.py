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

import os.path

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import GObject

from setzer.dialogs.dialog_locator import DialogLocator
from setzer.app.service_locator import ServiceLocator


class DocumentController(object):
    
    def __init__(self, document, document_view):

        self.document = document
        self.view = document_view

        self.workspace = ServiceLocator.get_workspace()

        self.key_controller = Gtk.EventControllerKey()
        self.key_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.key_controller.connect('key-pressed', self.on_keypress)
        self.view.source_view.add_controller(self.key_controller)

        self.deleted_on_disk_dialog_shown_after_last_save = False
        self.changed_on_disk_dialog_shown_after_last_change = False
        self.continue_save_date_loop = True
        GObject.timeout_add(500, self.save_date_loop)

    '''
    *** signal handlers: changes in documents
    '''

    def on_keypress(self, controller, keyval, keycode, state):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if keyval == Gdk.keyval_from_name('c') and state & modifiers == Gdk.ModifierType.CONTROL_MASK:
            self.document.content.copy()
            controller.reset()

        elif keyval == Gdk.keyval_from_name('x')and state & modifiers == Gdk.ModifierType.CONTROL_MASK:
            self.document.content.cut()
            controller.reset()

        elif keyval == Gdk.keyval_from_name('v') and state & modifiers == Gdk.ModifierType.CONTROL_MASK:
            self.document.content.paste()
            controller.reset()

        else:
            return False

        return True

    def save_date_loop(self):
        if self.document.filename == None: return True
        if self.deleted_on_disk_dialog_shown_after_last_save: return True
        if self.changed_on_disk_dialog_shown_after_last_change:
            return True

        if self.document.get_deleted_on_disk():
            self.deleted_on_disk_dialog_shown_after_last_save = True
            self.document.content.set_modified(True)
            DialogLocator.get_dialog('document_deleted_on_disk').run({'document': self.document})
        elif self.document.get_changed_on_disk():
            self.changed_on_disk_dialog_shown_after_last_change = True
            DialogLocator.get_dialog('document_changed_on_disk').run({'document': self.document}, self.changed_on_disk_cb)

        return self.continue_save_date_loop

    def changed_on_disk_cb(self, do_reload):
        if do_reload:
            self.document.populate_from_filename()
            self.document.content.set_modified(False)
        else:
            self.document.content.set_modified(True)
        self.changed_on_disk_dialog_shown_after_last_change = False
        self.document.update_save_date()



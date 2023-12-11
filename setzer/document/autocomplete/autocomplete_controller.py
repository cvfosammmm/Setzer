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
from gi.repository import Gtk, Gdk

from setzer.app.service_locator import ServiceLocator


class AutocompleteController(object):

    def __init__(self, autocomplete, document):
        self.autocomplete = autocomplete
        self.document = document

        key_controller = Gtk.EventControllerKey()
        key_controller.connect('key-pressed', self.on_keypress)
        key_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.document.view.source_view.add_controller(key_controller)

    def on_keypress(self, controller, keyval, keycode, state):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if keyval in [Gdk.keyval_from_name('Tab'), Gdk.keyval_from_name('ISO_Left_Tab')]:
            if state & modifiers == 0:
                if self.autocomplete.is_active:
                    self.autocomplete.tab()
                    return True
                else:
                    self.autocomplete.activate_if_possible()
                    if self.autocomplete.is_active:
                        return True

        if (state & modifiers, keyval) == (0, Gdk.keyval_from_name('Return')):
            if self.autocomplete.is_active:
                self.autocomplete.submit()
                return True

        if (state & modifiers, keyval) == (0, Gdk.keyval_from_name('Escape')):
            self.autocomplete.deactivate()
            return True

        if (state & modifiers, keyval) == (0, Gdk.keyval_from_name('Down')):
            if self.autocomplete.is_active:
                self.autocomplete.select_next()
                return True

        if (state & modifiers, keyval) == (0, Gdk.keyval_from_name('Up')):
            if self.autocomplete.is_active:
                self.autocomplete.select_previous()
                return True

        if (state & modifiers, keyval) == (0, Gdk.keyval_from_name('Page_Down')):
            if self.autocomplete.is_active:
                self.autocomplete.page_down()
                return True

        if (state & modifiers, keyval) == (0, Gdk.keyval_from_name('Page_Up')):
            if self.autocomplete.is_active:
                self.autocomplete.page_up()
                return True

        return False



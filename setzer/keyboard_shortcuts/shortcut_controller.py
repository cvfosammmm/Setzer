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

from setzer.app.service_locator import ServiceLocator


class ShortcutController(Gtk.ShortcutController):

    def __init__(self):
        Gtk.ShortcutController.__init__(self)

    def create_and_add_shortcut(self, trigger_string, callback):
        shortcut = Gtk.Shortcut()

        shortcut.set_action(Gtk.CallbackAction.new(self.action, callback))
        shortcut.set_trigger(Gtk.ShortcutTrigger.parse_string(trigger_string))

        self.add_shortcut(shortcut)

    def action(self, a, b, callback):
        callback()
        return True



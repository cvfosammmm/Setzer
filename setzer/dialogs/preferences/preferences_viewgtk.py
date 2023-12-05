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
from gi.repository import Gdk

from setzer.dialogs.helpers.dialog_viewgtk import DialogView


class Preferences(DialogView):

    def __init__(self, main_window):
        DialogView.__init__(self, main_window)

        self.set_can_focus(False)
        self.set_size_request(400, 250)
        self.set_default_size(400, 250)
        self.headerbar.set_title_widget(Gtk.Label.new(_('Preferences')))

        self.notebook = Gtk.Notebook()
        self.notebook.set_show_tabs(True)
        self.notebook.set_vexpand(True)
        self.topbox.append(self.notebook)



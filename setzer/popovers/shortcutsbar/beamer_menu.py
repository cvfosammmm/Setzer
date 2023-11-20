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
from gi.repository import GLib

from setzer.popovers.helpers.popover_menu_builder import MenuBuilder
from setzer.popovers.helpers.popover import Popover


class BeamerMenu(object):

    def __init__(self, popover_manager):
        self.view = BeamerMenuView(popover_manager)


class BeamerMenuView(Popover):

    def __init__(self, popover_manager):
        Popover.__init__(self, popover_manager)

        self.set_width(288)

        self.add_action_button('main', '\\usetheme', 'win.insert-after-packages', GLib.Variant('as', ['\\usetheme{•}']))
        self.add_action_button('main', _('Hide Navigation'), 'win.insert-after-packages', GLib.Variant('as', ['\\beamertemplatenavigationsymbolsempty']))
        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
        self.add_insert_symbol_item('main', _('Title Page'), ['\\begin{frame}\n\t\\titlepage\n\\end{frame}'])
        self.add_insert_symbol_item('main', _('Table of Contents'), ['\\begin{frame}\n\t\\tableofcontents\n\\end{frame}'])
        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
        self.add_before_after_item('main', _('Frame'), ['\\begin{frame}\n\t', '\n\\end{frame}'])
        self.add_before_after_item('main', _('Frame with Title'), ['\\begin{frame}\n\t\\frametitle{•}\n\n\t', '\n\\end{frame}'])
        self.add_before_after_item('main', _('\\frametitle'), ['\\frametitle{', '}'])



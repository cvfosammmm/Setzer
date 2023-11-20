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


class QuotesMenu(object):

    def __init__(self, popover_manager):
        self.view = QuotesMenuView(popover_manager)


class QuotesMenuView(Popover):

    def __init__(self, popover_manager):
        Popover.__init__(self, popover_manager)
        self.get_style_context().add_class('menu-own-quotes-symbolic')

        self.set_width(288)

        self.add_before_after_item('main', _('Primary Quotes') + ' (`` ... \'\')', ['``', '\'\''])
        self.add_before_after_item('main', _('Secondary Quotes') + ' (` ... \')', ['`', '\''])
        self.add_before_after_item('main', _('German Quotes') + ' (\\glqq ... \\grqq{})', ['\\glqq ', '\\grqq{}'])
        self.add_before_after_item('main', _('German Single Quotes') + ' (\\glq ... \\grq{})', ['\\glq ', '\\grq{}'])
        self.add_before_after_item('main', _('French Quotes') + ' (\\flqq ... \\frqq{})', ['\\flqq ', '\\frqq{}'])
        self.add_before_after_item('main', _('French Single Quotes') + ' (\\flq ... \\frq{})', ['\\flq ', '\\frq{}'])
        self.add_before_after_item('main', _('German Alt Quotes') + ' (\\frqq ... \\flqq{})', ['\\frqq ', '\\flqq{}'])
        self.add_before_after_item('main', _('German Alt Single Quotes') + ' (\\frq ... \\frq{})', ['\\frq ', '\\flq{}'])



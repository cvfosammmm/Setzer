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

from setzer.popovers.helpers.popover_menu_builder import MenuBuilder
from setzer.popovers.helpers.popover import Popover


class NewDocumentView(Popover):

    def __init__(self, popover_manager):
        Popover.__init__(self, popover_manager)

        self.set_width(252)

        self.button_latex = MenuBuilder.create_button(_('New LaTeX Document'), shortcut=_('Ctrl') + '+N')
        self.button_latex.set_action_name('win.new-latex-document')
        self.add_closing_button(self.button_latex)

        self.button_bibtex = MenuBuilder.create_button(_('New BibTeX Document'))
        self.button_bibtex.set_action_name('win.new-bibtex-document')
        self.add_closing_button(self.button_bibtex)



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


class BibliographyMenu(object):

    def __init__(self, popover_manager):
        self.view = BibliographyMenuView(popover_manager)


class BibliographyMenuView(Popover):

    def __init__(self, popover_manager):
        Popover.__init__(self, popover_manager)

        self.set_width(288)

        self.add_action_button('main', _('Include BibTeX File') + '...', 'win.include-bibtex-file')
        self.add_action_button('main', _('Include \'natbib\' Package'), 'win.add-packages', GLib.Variant('as', ['natbib']))
        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
        self.add_insert_symbol_item('main', _('Citation'), ['\\cite{•}'])
        self.add_insert_symbol_item('main', _('Citation with Page Number'), ['\\cite[•]{•}'])
        self.add_menu_button(_('Natbib Citations'), 'natbib_citations')
        self.add_action_button('main', _('Include non-cited BibTeX Entries with \'\\nocite\''), 'win.insert-before-document-end', GLib.Variant('as', ['\\nocite{*}']))

        # natbib submenu
        self.add_page('natbib_citations', _('Natbib Citations'))
        self.add_insert_symbol_item('natbib_citations', _('Abbreviated'), ['\\citet{•}'])
        self.add_insert_symbol_item('natbib_citations', _('Abbreviated with Brackets'), ['\\citep{•}'])
        self.add_insert_symbol_item('natbib_citations', _('Detailed'), ['\\citet*{•}'])
        self.add_insert_symbol_item('natbib_citations', _('Detailed with Brackets'), ['\\citep*{•}'])
        self.add_insert_symbol_item('natbib_citations', _('Alternative 1'), ['\\citealt{•}'])
        self.add_insert_symbol_item('natbib_citations', _('Alternative 2'), ['\\citealp{•}'])
        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL), 'natbib_citations')
        self.add_insert_symbol_item('natbib_citations', _('Cite Author'), ['\\citeauthor{•}'])
        self.add_insert_symbol_item('natbib_citations', _('Cite Author Detailed'), ['\\citeauthor*{•}'])
        self.add_insert_symbol_item('natbib_citations', _('Cite Year'), ['\\citeyear{•}'])
        self.add_insert_symbol_item('natbib_citations', _('Cite Year with Brackets'), ['\\citeyearpar{•}'])



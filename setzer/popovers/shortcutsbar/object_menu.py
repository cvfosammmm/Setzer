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


class ObjectMenu(object):

    def __init__(self, popover_manager):
        self.view = ObjectMenuView(popover_manager)


class ObjectMenuView(Popover):

    def __init__(self, popover_manager):
        Popover.__init__(self, popover_manager)
        self.get_style_context().add_class('menu-own-quotes-symbolic')

        self.set_width(288)

        self.add_insert_symbol_item('main', _('Figure (image inside freestanding block)'), ['\\begin{figure}\n\t\\begin{center}\n\t\t\\includegraphics[scale=1]{•}\n\t\t\\caption{•}\n\t\\end{center}\n\\end{figure}'])
        self.add_insert_symbol_item('main', _('Inline Image'), ['\\includegraphics[scale=1]{•}'])
        self.add_menu_button(_('Code Listing'), 'code_listing')
        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
        self.add_before_after_item('main', _('Url (\\url)'), ['\\url{', '}'])
        self.add_before_after_item('main', _('Hyperlink (\\href)'), ['\\href{•}{', '}'])

        # code listing submenu
        self.add_page('code_listing', _('Code Listing'))
        self.add_action_button('code_listing', _('Include \'listings\' Package'), 'win.add-packages', GLib.Variant('as', ['listings']))
        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL), 'code_listing')
        self.add_before_after_item('code_listing', 'Python', ['\\lstset{language=Python}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        self.add_before_after_item('code_listing', 'C', ['\\lstset{language=C}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        self.add_before_after_item('code_listing', 'C++', ['\\lstset{language=C++}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        self.add_before_after_item('code_listing', 'Java', ['\\lstset{language=Java}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        self.add_before_after_item('code_listing', 'Perl', ['\\lstset{language=Perl}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        self.add_before_after_item('code_listing', 'PHP', ['\\lstset{language=PHP}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        self.add_before_after_item('code_listing', 'Ruby', ['\\lstset{language=Ruby}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        self.add_before_after_item('code_listing', 'TeX', ['\\lstset{language=TeX}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL), 'code_listing')
        self.add_before_after_item('code_listing', _('Other Language'), ['\\lstset{language=•}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        self.add_before_after_item('code_listing', _('Plain Text'), ['\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])



#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017, 2018 Robert Griesel
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
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GLib

import setzer.workspace.sidebar.sidebar_viewgtk as sidebar_view
from setzer.app.service_locator import ServiceLocator

import math


class Sidebar(object):
    ''' Init and controll sidebar '''
    
    def __init__(self, workspace):
        self.view = ServiceLocator.get_main_window().sidebar
        self.workspace = workspace

        # tabbed pages: name, icon name, tooltip, widget
        self.pages = list()
        self.pages.append(['greek_letters', 'own-symbols-greek-letters-symbolic', _('Greek Letters'), 
                           'sidebar_view.SidebarPageSymbolsList("greek_letters", 25)'])
        self.pages.append(['arrows', 'own-symbols-arrows-symbolic', _('Arrows'), 
                           'sidebar_view.SidebarPageSymbolsList("arrows", 48)'])
        self.pages.append(['relations', 'own-symbols-relations-symbolic', _('Relations'), 
                           'sidebar_view.SidebarPageSymbolsList("relations", 39)'])
        self.pages.append(['operators', 'own-symbols-operators-symbolic', _('Operators'), 
                           'sidebar_view.SidebarPageSymbolsList("operators", 47)'])
        self.pages.append(['misc_math', 'own-symbols-misc-math-symbolic', _('Misc. Math'), 
                           'sidebar_view.SidebarPageSymbolsList("misc_math", 42)'])
        self.pages.append(['misc_text', 'own-symbols-misc-text-symbolic', _('Misc. Symbols'), 
                           'sidebar_view.SidebarPageSymbolsList("misc_text", 38)'])
        self.page_views = list()
        self.init_page_stack()

        self.view.show_all()

    def init_page_stack(self):
        self.tab_buttons = list()
        for page in self.pages:
            if len(self.tab_buttons) == 0:
                button = Gtk.RadioToolButton()
            else:
                button = Gtk.RadioToolButton.new_from_widget(self.tab_buttons[0])
            button.set_icon_name(page[1])
            button.set_focus_on_click(False)
            button.set_tooltip_text(page[2])
            if len(self.tab_buttons) == 0:
                button.get_style_context().add_class('first')

            self.tab_buttons.append(button)
            self.view.tabs.insert(button, -1)
            page_view = eval(page[3])
            self.view.stack.add_named(page_view, page[0])
            self.init_symbols_page(page_view)
            self.page_views.append(page_view)
            page_view.connect('size-allocate', self.on_stack_size_allocate)
            button.connect('clicked', self.on_tab_button_clicked, page[0])
            page_view.flowbox.connect('button-press-event', self.on_flowbox_clicked, page_view.symbols)

    def init_symbols_page(self, page_view):
        for symbol in page_view.symbols:
            image = symbol[5]
            image.set_size_request(page_view.symbol_width + 11, -1)

    '''
    *** signal handlers for buttons in sidebar
    '''
    
    def on_tab_button_clicked(self, button, page_name):
        self.view.stack.set_visible_child_name(page_name)

    def on_flowbox_clicked(self, flowbox, event, symbols_list):
        child = flowbox.get_child_at_pos(event.x, event.y)

        if child != None and self.workspace.active_document != None:
            self.workspace.get_active_document().insert_text_at_cursor(symbols_list[child.get_index()][1])
            self.workspace.get_active_document().content.scroll_cursor_onscreen()

        return True

    '''
    *** manage borders of images
    '''

    def on_stack_size_allocate(self, symbol_page, allocation, data=None):
        if symbol_page.size != (allocation.width, allocation.height):
            symbol_page.size = (allocation.width, allocation.height)
            if isinstance(symbol_page, sidebar_view.SidebarPageSymbolsList):
                width_with_border = symbol_page.symbol_width + 11
                width_avail = allocation.width
                symbols_per_line = width_avail // width_with_border
                number_of_lines = math.ceil(len(symbol_page.symbols) / symbols_per_line)

                height_with_border = symbol_page.symbols[0][5].get_preferred_height()[0]
                for line_no in range(1, number_of_lines):
                    # get max for each element
                    max_height = 0
                    for el_no in range(0, symbols_per_line):
                        try:
                            symbol = symbol_page.symbols[(line_no * symbols_per_line) + 1 + el_no]
                        except IndexError:
                            el_height = 0
                        else:
                            el_height = symbol[5].get_preferred_height()[0]
                            if symbol[5].get_style_context().has_class('no_bottom_border'):
                                el_height += 1
                        if el_height > max_height: max_height = el_height
                    height_with_border += max_height
                height_avail = (allocation.height + 1) # +1px for removed child borders
                for number, image in enumerate(symbol_page.symbols):
                    if (number % symbols_per_line) == (symbols_per_line - 1):
                        image[5].get_style_context().add_class('no_right_border')
                    else:
                        image[5].get_style_context().remove_class('no_right_border')
                    if (number >= (number_of_lines - 1) * symbols_per_line) and (height_avail <= height_with_border):
                        image[5].get_style_context().add_class('no_bottom_border')
                    else:
                        image[5].get_style_context().remove_class('no_bottom_border')



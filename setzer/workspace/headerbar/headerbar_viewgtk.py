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
from gi.repository import Gio

import setzer.workspace.document_switcher.document_switcher_viewgtk as document_switcher_viewgtk
from setzer.helpers.popover_menu_builder import MenuBuilder


class HeaderBar(Gtk.HeaderBar):
    ''' Title bar of the app, contains global controls '''

    def __init__(self):
        Gtk.HeaderBar.__init__(self)

        # open documents button
        self.open_document_blank_button = Gtk.Button.new_with_label(_('Open') + '...')
        self.open_document_blank_button.set_tooltip_text(_('Open a document') + ' (' + _('Ctrl') + '+O)')
        self.open_document_blank_button.set_action_name('win.open-document-dialog')

        self.button_latex = MenuBuilder.create_action_button(_('New LaTeX Document'), _('Ctrl') + '+N')
        self.button_bibtex = MenuBuilder.create_action_button(_('New BibTeX Document'))

        self.new_document_popover = MenuBuilder.create_menu()
        box = self.new_document_popover.get_child()

        MenuBuilder.add_button(box, self.button_latex)
        MenuBuilder.add_button(box, self.button_bibtex)

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.append(Gtk.Image.new_from_icon_name('document-new-symbolic'))
        box.append(Gtk.Image.new_from_icon_name('pan-down-symbolic'))
        box.set_size_request(40, -1)

        self.new_document_button = Gtk.MenuButton()
        self.new_document_button.set_child(box)
        self.new_document_button.set_can_focus(False)
        self.new_document_button.set_tooltip_text(_('Create a new document'))
        self.new_document_button.get_style_context().add_class('new-document-menu-button')
        self.new_document_button.set_popover(self.new_document_popover)

        self.pack_start(self.open_document_blank_button)
        self.pack_start(self.new_document_button)

        # workspace menu
        self.session_file_buttons = list()
        self.insert_workspace_menu()

        # save document button
        self.save_document_button = Gtk.Button.new_with_label(_('Save'))
        self.save_document_button.set_can_focus(False)
        self.save_document_button.set_tooltip_text(_('Save the current document') + ' (' + _('Ctrl') + '+S)')
        self.save_document_button.set_action_name('win.save')
        self.pack_end(self.save_document_button)

        # title / open documents popover
        self.center_widget = document_switcher_viewgtk.OpenDocsButton()
        self.set_title_widget(self.center_widget)

    def insert_workspace_menu(self):
        box_main = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        box_session = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        self.button_save_as = MenuBuilder.create_action_button(_('Save Document As') + '...', _('Shift') + '+' + _('Ctrl') + '+S')
        self.button_save_all = MenuBuilder.create_action_button(_('Save All Documents'))
        self.button_session = MenuBuilder.create_menu_button(_('Session'))
        self.button_about = MenuBuilder.create_action_button(_('About'))
        self.button_close_all = MenuBuilder.create_action_button(_('Close All Documents'))
        self.button_close_active = MenuBuilder.create_action_button(_('Close Document'), _('Ctrl') + '+W')
        self.button_quit = MenuBuilder.create_action_button(_('Quit'), _('Ctrl') + '+Q')

        MenuBuilder.add_button(box_main, self.button_save_as)
        MenuBuilder.add_button(box_main, self.button_save_all)
        MenuBuilder.add_separator(box_main)
        MenuBuilder.add_button(box_main, self.button_session)
        MenuBuilder.add_separator(box_main)
        MenuBuilder.add_button(box_main, self.button_about)
        MenuBuilder.add_separator(box_main)
        MenuBuilder.add_button(box_main, self.button_close_all)
        MenuBuilder.add_button(box_main, self.button_close_active)
        MenuBuilder.add_button(box_main, self.button_quit)

        stack = Gtk.Stack()
        stack.set_vhomogeneous(False)
        stack.add_named(box_main, 'main')
        stack.add_named(box_session, 'session')

        self.hamburger_popover = Gtk.Popover()
        self.hamburger_popover.set_child(stack)

        self.menu_button = Gtk.MenuButton()
        image = Gtk.Image.new_from_icon_name('open-menu-symbolic')
        self.menu_button.set_child(image)
        self.menu_button.set_can_focus(False)
        self.menu_button.set_popover(self.hamburger_popover)
        self.pack_end(self.menu_button)

        # session submenu
        self.button_session_header = MenuBuilder.create_header_button(_('Session'))

        MenuBuilder.add_button(box_session, self.button_session_header)

        self.session_explaination = Gtk.Label.new(_('Save the list of open documents in a session file\nand restore it later, a convenient way to work\non multiple projects.'))
        self.session_explaination.set_xalign(0)
        self.session_explaination.get_style_context().add_class('explaination')
        self.session_explaination.set_margin_top(8)
        self.session_explaination.set_margin_bottom(11)
        box_session.append(self.session_explaination)

        self.button_restore_session = MenuBuilder.create_action_button(_('Restore Previous Session') + '...')
        self.button_save_session = MenuBuilder.create_action_button(_('Save Current Session') + '...')

        MenuBuilder.add_button(box_session, self.button_restore_session)
        MenuBuilder.add_button(box_session, self.button_save_session)

        self.session_box_separator = Gtk.Separator()
        box_session.append(self.session_box_separator)
        self.session_box_separator.hide()

        self.prev_sessions_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        box_session.append(self.prev_sessions_box)

        def show_page(button, page_name, transition_type):
            self.hamburger_popover.get_child().set_transition_type(transition_type)
            self.hamburger_popover.get_child().set_visible_child_name(page_name)

        self.button_session.connect('clicked', show_page, 'session', Gtk.StackTransitionType.SLIDE_RIGHT)
        self.button_session_header.connect('clicked', show_page, 'main', Gtk.StackTransitionType.SLIDE_LEFT)



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
import setzer.workspace.document_chooser.document_chooser_viewgtk as document_chooser_viewgtk
from setzer.helpers.popover_menu_builder import MenuBuilder


class HeaderBar(Gtk.HeaderBar):
    ''' Title bar of the app, contains global controls '''

    def __init__(self):
        Gtk.HeaderBar.__init__(self)

        # open document buttons
        self.open_document_blank_button = Gtk.Button.new_with_label(_('Open') + '...')
        self.open_document_blank_button.set_tooltip_text(_('Open a document') + ' (' + _('Ctrl') + '+O)')
        self.open_document_blank_button.set_action_name('win.open-document-dialog')

        self.document_chooser = document_chooser_viewgtk.DocumentChooser()
        self.open_document_button_label = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 12)
        self.open_document_button_label.append(Gtk.Label.new(_('Open')))
        self.open_document_button_label.append(Gtk.Image.new_from_icon_name('pan-down-symbolic'))
        self.open_document_button = Gtk.MenuButton()
        self.open_document_button.set_tooltip_text(_('Open a document') + ' (' + _('Shift') + '+' + _('Ctrl') + '+O)')
        self.open_document_button.set_child(self.open_document_button_label)
        self.open_document_button.set_popover(self.document_chooser)

        # new document buttons
        self.button_latex = MenuBuilder.create_action_button(_('New LaTeX Document'), _('Ctrl') + '+N')
        self.button_bibtex = MenuBuilder.create_action_button(_('New BibTeX Document'))

        self.new_document_popover = MenuBuilder.create_menu()

        MenuBuilder.add_widget(self.new_document_popover, self.button_latex)
        MenuBuilder.add_widget(self.new_document_popover, self.button_bibtex)

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 12)
        box.append(Gtk.Image.new_from_icon_name('document-new-symbolic'))
        box.append(Gtk.Image.new_from_icon_name('pan-down-symbolic'))

        self.new_document_button = Gtk.MenuButton()
        self.new_document_button.set_child(box)
        self.new_document_button.set_can_focus(False)
        self.new_document_button.set_tooltip_text(_('Create a new document'))
        self.new_document_button.get_style_context().add_class('new-document-menu-button')
        self.new_document_button.set_popover(self.new_document_popover)

        self.pack_start(self.open_document_button)
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
        self.hamburger_popover = MenuBuilder.create_menu()

        self.button_save_as = MenuBuilder.create_action_button(_('Save Document As') + '...', _('Shift') + '+' + _('Ctrl') + '+S')
        self.button_save_all = MenuBuilder.create_action_button(_('Save All Documents'))
        self.button_session = MenuBuilder.create_menu_button(_('Session'))
        self.button_session.connect('clicked', self.hamburger_popover.show_page, 'session', Gtk.StackTransitionType.SLIDE_RIGHT)
        self.button_about = MenuBuilder.create_action_button(_('About'))
        self.button_close_all = MenuBuilder.create_action_button(_('Close All Documents'))
        self.button_close_active = MenuBuilder.create_action_button(_('Close Document'), _('Ctrl') + '+W')
        self.button_quit = MenuBuilder.create_action_button(_('Quit'), _('Ctrl') + '+Q')

        MenuBuilder.add_widget(self.hamburger_popover, self.button_save_as)
        MenuBuilder.add_widget(self.hamburger_popover, self.button_save_all)
        MenuBuilder.add_separator(self.hamburger_popover)
        MenuBuilder.add_widget(self.hamburger_popover, self.button_session)
        MenuBuilder.add_separator(self.hamburger_popover)
        MenuBuilder.add_widget(self.hamburger_popover, self.button_about)
        MenuBuilder.add_separator(self.hamburger_popover)
        MenuBuilder.add_widget(self.hamburger_popover, self.button_close_all)
        MenuBuilder.add_widget(self.hamburger_popover, self.button_close_active)
        MenuBuilder.add_widget(self.hamburger_popover, self.button_quit)

        box_session = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        self.menu_button = Gtk.MenuButton()
        image = Gtk.Image.new_from_icon_name('open-menu-symbolic')
        self.menu_button.set_child(image)
        self.menu_button.set_can_focus(False)
        self.menu_button.set_popover(self.hamburger_popover)
        self.pack_end(self.menu_button)

        # session submenu
        MenuBuilder.add_page(self.hamburger_popover, 'session', _('Session'))

        self.session_explaination = Gtk.Label.new(_('Save the list of open documents in a session file\nand restore it later, a convenient way to work\non multiple projects.'))
        self.session_explaination.set_xalign(0)
        self.session_explaination.get_style_context().add_class('explaination')
        self.session_explaination.set_margin_top(8)
        self.session_explaination.set_margin_bottom(11)

        self.button_restore_session = MenuBuilder.create_action_button(_('Restore Previous Session') + '...')
        self.button_save_session = MenuBuilder.create_action_button(_('Save Current Session') + '...')

        self.session_box_separator = Gtk.Separator()
        self.session_box_separator.hide()

        self.prev_sessions_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        MenuBuilder.add_widget(self.hamburger_popover, self.session_explaination, pagename='session')
        MenuBuilder.add_widget(self.hamburger_popover, self.button_restore_session, pagename='session')
        MenuBuilder.add_widget(self.hamburger_popover, self.button_save_session, pagename='session')
        MenuBuilder.add_widget(self.hamburger_popover, self.session_box_separator, pagename='session')
        MenuBuilder.add_widget(self.hamburger_popover, self.prev_sessions_box, pagename='session')



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
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gio

import setzer.workspace.document_switcher.document_switcher_viewgtk as document_switcher_viewgtk
from setzer.app.service_locator import ServiceLocator


class HeaderBar(Gtk.HeaderBar):
    ''' Title bar of the app, contains global controls '''

    def __init__(self):
        Gtk.HeaderBar.__init__(self)
        self.pmb = ServiceLocator.get_popover_menu_builder()

        self.set_show_close_button(True)

        # open documents button
        self.open_document_blank_button = Gtk.Button.new_with_label(_('Open') + '...')
        self.open_document_blank_button.set_tooltip_text(_('Open a document') + ' (' + _('Ctrl') + '+O)')
        self.open_document_blank_button.set_action_name('win.open-document-dialog')
        self.pack_start(self.open_document_blank_button)

        popover = Gtk.PopoverMenu()
        stack = popover.get_child()
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_action_button(box, _('New LaTeX Document'), 'win.new-latex-document', keyboard_shortcut=_('Ctrl') + '+N')
        self.pmb.add_action_button(box, _('New BibTeX Document'), 'win.new-bibtex-document')
        stack.add_named(box, 'main')
        box.show_all()

        box = Gtk.HBox()
        box.pack_start(Gtk.Image.new_from_icon_name('document-new-symbolic', Gtk.IconSize.MENU), False, False, 0)
        box.pack_end(Gtk.Image.new_from_icon_name('pan-down-symbolic', Gtk.IconSize.MENU), False, False, 0)
        box.set_size_request(40, -1)

        self.new_document_button = Gtk.MenuButton()
        self.new_document_button.add(box)
        self.new_document_button.set_use_popover(True)
        self.new_document_button.set_can_focus(False)
        self.new_document_button.set_tooltip_text(_('Create a new document'))
        self.new_document_button.get_style_context().add_class('new-document-menu-button')
        self.new_document_button.set_popover(popover)

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
        self.set_custom_title(self.center_widget)

    def insert_workspace_menu(self):
        popover = Gtk.PopoverMenu()

        self.menu_button = Gtk.MenuButton()
        image = Gtk.Image.new_from_icon_name('open-menu-symbolic', Gtk.IconSize.BUTTON)
        self.menu_button.set_image(image)
        self.menu_button.set_can_focus(False)
        self.menu_button.set_popover(popover)
        self.pack_end(self.menu_button)

        # session submenu
        self.session_box = Gtk.VBox()
        self.pmb.set_box_margin(self.session_box)
        self.pmb.add_header_button(self.session_box, _('Session'))
        self.session_explaination = Gtk.Label(_('Save the list of open documents in a session file\nand restore it later, a convenient way to work\non multiple projects.'))
        self.session_explaination.set_xalign(0)
        self.session_explaination.get_style_context().add_class('explaination')
        self.session_explaination.set_margin_top(8)
        self.session_explaination.set_margin_bottom(11)
        self.session_box.pack_start(self.session_explaination, False, False, 0)
        self.pmb.add_action_button(self.session_box, _('Restore Previous Session') + '...', 'win.restore-session', [''])
        self.pmb.add_action_button(self.session_box, _('Save Current Session') + '...', 'win.save-session')
        self.session_box_separator = Gtk.SeparatorMenuItem()
        self.session_box_separator.show_all()
        self.session_box.show_all()

        GLib.idle_add(self.populate_workspace_menu, priority=GLib.PRIORITY_LOW)

    def populate_workspace_menu(self):
        popover = self.menu_button.get_popover()
        stack = popover.get_child()

        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_action_button(box, _('Save Document As') + '...', 'win.save-as', keyboard_shortcut=_('Shift') + '+' + _('Ctrl') + '+S')
        self.pmb.add_action_button(box, _('Save All Documents'), 'win.save-all')
        self.pmb.add_separator(box)
        self.pmb.add_menu_button(box, _('Session'), 'session')
        self.pmb.add_separator(box)
        self.pmb.add_action_button(box, _('About'), 'win.show-about-dialog')
        self.pmb.add_separator(box)
        self.pmb.add_action_button(box, _('Close All Documents'), 'win.close-all-documents')
        self.pmb.add_action_button(box, _('Close Document'), 'win.close-active-document', keyboard_shortcut=_('Ctrl') + '+W')
        self.pmb.add_action_button(box, _('Quit'), 'win.quit', keyboard_shortcut=_('Ctrl') + '+Q')
        stack.add_named(box, 'main')
        box.show_all()

        # session submenu
        stack.add_named(self.session_box, 'session')



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
gi.require_version('Handy', '1')
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import Handy

import setzer.workspace.document_switcher.document_switcher_viewgtk as document_switcher_viewgtk
import setzer.workspace.document_chooser.document_chooser_viewgtk as document_chooser_viewgtk
from setzer.app.service_locator import ServiceLocator


class HeaderBar(Handy.HeaderBar):
    ''' Title bar of the app, contains global controls '''

    def __init__(self):
        Handy.HeaderBar.__init__(self)
        self.pmb = ServiceLocator.get_popover_menu_builder()

        self.set_show_close_button(True)

        # sidebar toggles
        box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.document_structure_toggle = Gtk.ToggleButton()
        self.document_structure_toggle.set_image(Gtk.Image.new_from_icon_name('document-structure-symbolic', Gtk.IconSize.MENU))
        self.document_structure_toggle.set_can_focus(False)
        self.document_structure_toggle.set_tooltip_text(_('Toggle document structure') + ' (F2)')
        box.pack_start(self.document_structure_toggle, False, False, 0)
        self.symbols_toggle = Gtk.ToggleButton()
        self.symbols_toggle.set_image(Gtk.Image.new_from_icon_name('own-symbols-misc-text-symbolic', Gtk.IconSize.MENU))
        self.symbols_toggle.set_can_focus(False)
        self.symbols_toggle.set_tooltip_text(_('Toggle symbols') + ' (F3)')
        box.pack_start(self.symbols_toggle, False, False, 0)
        box.get_style_context().add_class('linked')
        self.pack_start(box)

        # open documents button
        self.document_chooser = document_chooser_viewgtk.DocumentChooser()
        self.open_document_button_label = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.open_document_button_label.pack_start(Gtk.Label(_('Open')), False, False, 0)
        self.open_document_button_label.pack_start(Gtk.Image.new_from_icon_name('pan-down-symbolic', Gtk.IconSize.MENU), False, False, 0)
        self.open_document_button = Gtk.MenuButton()
        self.open_document_button.set_can_focus(False)
        self.open_document_button.set_tooltip_text(_('Open a document') + ' (' + _('Shift') + '+' + _('Ctrl') + '+O)')
        self.open_document_button.set_use_popover(True)
        self.open_document_button.add(self.open_document_button_label)
        self.open_document_button.get_style_context().add_class('text-button')
        self.open_document_button.get_style_context().add_class('image-button')
        self.open_document_button.set_popover(self.document_chooser)
        self.pack_start(self.open_document_button)
        self.open_document_blank_button = Gtk.Button.new_with_label(_('Open') + '...')
        self.open_document_blank_button.set_tooltip_text(_('Open a document') + ' (' + _('Ctrl') + '+O)')
        self.open_document_blank_button.set_action_name('win.open-document-dialog')
        self.pack_start(self.open_document_blank_button)

        popover = Gtk.PopoverMenu()
        stack = popover.get_child()
        box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.pmb.set_box_margin(box)
        self.pmb.add_action_button(box, _('New LaTeX Document'), 'win.new-latex-document', keyboard_shortcut=_('Ctrl') + '+N')
        self.pmb.add_action_button(box, _('New BibTeX Document'), 'win.new-bibtex-document')
        stack.add_named(box, 'main')
        box.show_all()

        box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
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

        # help and preview toggles
        box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.preview_toggle = Gtk.ToggleButton()
        self.preview_toggle.set_image(Gtk.Image.new_from_icon_name('view-paged-symbolic', Gtk.IconSize.MENU))
        self.preview_toggle.set_can_focus(False)
        self.preview_toggle.set_tooltip_text(_('Toggle preview') + ' (F9)')
        box.pack_start(self.preview_toggle, False, False, 0)
        self.help_toggle = Gtk.ToggleButton()
        self.help_toggle.set_image(Gtk.Image.new_from_icon_name('help-browser-symbolic', Gtk.IconSize.MENU))
        self.help_toggle.set_can_focus(False)
        self.help_toggle.set_tooltip_text(_('Toggle help') + ' (F1)')
        box.pack_start(self.help_toggle, False, False, 0)
        box.get_style_context().add_class('linked')
        self.pack_end(box)
        
        # build button wrapper
        self.build_wrapper = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.pack_end(self.build_wrapper)

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
        self.session_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
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

        box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.pmb.set_box_margin(box)
        self.pmb.add_action_button(box, _('Save Document As') + '...', 'win.save-as', keyboard_shortcut=_('Shift') + '+' + _('Ctrl') + '+S')
        self.pmb.add_action_button(box, _('Save All Documents'), 'win.save-all')
        self.pmb.add_separator(box)
        self.pmb.add_menu_button(box, _('Session'), 'session')
        self.pmb.add_separator(box)
        self.pmb.add_menu_button(box, _('View'), 'view')
        self.pmb.add_menu_button(box, _('Tools'), 'tools')
        self.pmb.add_separator(box)
        self.pmb.add_action_button(box, _('Preferences'), 'win.show-preferences-dialog')
        self.pmb.add_separator(box)
        self.pmb.add_action_button(box, _('Keyboard Shortcuts'), 'win.show-shortcuts-window', keyboard_shortcut=_('Ctrl') + '+?')
        self.pmb.add_action_button(box, _('About'), 'win.show-about-dialog')
        self.pmb.add_separator(box)
        self.pmb.add_action_button(box, _('Close All Documents'), 'win.close-all-documents')
        self.pmb.add_action_button(box, _('Close Document'), 'win.close-active-document', keyboard_shortcut=_('Ctrl') + '+W')
        self.pmb.add_action_button(box, _('Quit'), 'win.quit', keyboard_shortcut=_('Ctrl') + '+Q')
        stack.add_named(box, 'main')
        box.show_all()

        # view submenu
        box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, _('View'))
        self.pmb.add_action_button(box, _('Dark Mode'), 'win.toggle-dark-mode')
        self.pmb.add_action_button(box, _('Invert Colors in .pdf-Preview'), 'win.toggle-invert-pdf')
        stack.add_named(box, 'view')
        box.show_all()

        # session submenu
        stack.add_named(self.session_box, 'session')

        # tools submenu
        box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, _('Tools'))
        self.pmb.add_action_button(box, _('Check Spelling') + '...', 'win.spellchecking')
        self.pmb.add_action_button(box, _('Automatic Spellchecking'), 'win.toggle-spellchecking')
        self.pmb.add_action_button(box, _('Set Spellchecking Language') + '...', 'win.set-spellchecking-language')
        stack.add_named(box, 'tools')
        box.show_all()



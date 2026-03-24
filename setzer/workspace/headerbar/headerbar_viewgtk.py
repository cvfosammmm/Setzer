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
from gi.repository import Gtk, GLib, Gio, Pango

from setzer.popovers.helpers.popover_menu_builder import MenuBuilder
from setzer.app.service_locator import ServiceLocator
from setzer.popovers.popover_manager import PopoverManager
from setzer.keyboard_shortcuts.keybind_parser import KeybindParser


class HeaderBar(Gtk.HeaderBar):

    def __init__(self):
        Gtk.HeaderBar.__init__(self)

        # sidebar toggles
        self.document_structure_toggle = Gtk.ToggleButton()
        self.document_structure_toggle.set_child(Gtk.Image.new_from_icon_name('document-structure-symbolic'))
        self.document_structure_toggle.set_can_focus(False)
        doc_structure_shortcut = KeybindParser.to_display(KeybindParser.get_shortcut('shortcut_document_structure_toggle', 'app'))
        self.document_structure_toggle.set_tooltip_text(_('Toggle document structure') + ' (' + doc_structure_shortcut + ')')

        self.symbols_toggle = Gtk.ToggleButton()
        self.symbols_toggle.set_child(Gtk.Image.new_from_icon_name('own-symbols-misc-text-symbolic'))
        self.symbols_toggle.set_can_focus(False)
        symbols_shortcut = KeybindParser.to_display(KeybindParser.get_shortcut('shortcut_symbols_toggle', 'app'))
        self.symbols_toggle.set_tooltip_text(_('Toggle symbols') + ' (' + symbols_shortcut + ')')

        self.sidebar_toggles_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.sidebar_toggles_box.append(self.document_structure_toggle)
        self.sidebar_toggles_box.append(self.symbols_toggle)
        self.sidebar_toggles_box.get_style_context().add_class('linked')

        self.pack_start(self.sidebar_toggles_box)

        # open document buttons
        self.open_document_blank_button = Gtk.Button.new_with_label(_('Open') + '...')
        open_doc_shortcut = KeybindParser.to_display(KeybindParser.get_shortcut('open-document-dialog', 'app'))
        self.open_document_blank_button.set_tooltip_text(_('Open a document') + ' (' + open_doc_shortcut + ')')
        self.open_document_blank_button.set_action_name('win.open-document-dialog')

        self.open_document_popover = PopoverManager.create_popover('open_document')
        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 12)
        box.append(Gtk.Label.new(_('Open')))
        box.append(Gtk.Image.new_from_icon_name('pan-down-symbolic'))
        self.open_document_button = PopoverManager.create_popover_button('open_document')
        self.open_document_button.set_child(box)
        self.open_document_button.set_can_focus(False)
        show_recent_shortcut = KeybindParser.to_display(KeybindParser.get_shortcut('shortcut_show_document_chooser', 'app'))
        self.open_document_button.set_tooltip_text(_('Show recent documents') + ' (' + show_recent_shortcut + ')')

        # new document
        self.new_document_popover = PopoverManager.create_popover('new_document')
        self.new_document_button = PopoverManager.create_popover_button('new_document')
        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 12)
        box.append(Gtk.Image.new_from_icon_name('document-new-symbolic'))
        box.append(Gtk.Image.new_from_icon_name('pan-down-symbolic'))
        self.new_document_button.set_child(box)
        self.new_document_button.set_can_focus(False)
        self.new_document_button.set_tooltip_text(_('Create a new document'))
        self.new_document_button.get_style_context().add_class('new-document-menu-button')

        self.pack_start(self.open_document_button)
        self.pack_start(self.open_document_blank_button)
        self.pack_start(self.new_document_button)

        # workspace menu
        self.session_file_buttons = list()
        self.hamburger_popover = PopoverManager.create_popover('hamburger_menu')
        self.menu_button = PopoverManager.create_popover_button('hamburger_menu')
        self.menu_button.set_child(Gtk.Image.new_from_icon_name('open-menu-symbolic'))
        self.menu_button.set_can_focus(False)
        main_menu_shortcut = KeybindParser.to_display(KeybindParser.get_shortcut('shortcut_show_hamburger', 'app'))
        self.menu_button.set_tooltip_text(_('Main Menu') + ' (' + main_menu_shortcut + ')')
        self.pack_end(self.menu_button)

        # save document button
        self.save_document_button = Gtk.Button.new_with_label(_('Save'))
        self.save_document_button.set_can_focus(False)
        save_shortcut = KeybindParser.to_display(KeybindParser.get_shortcut('save', 'app'))
        self.save_document_button.set_tooltip_text(_('Save the current document') + ' (' + save_shortcut + ')')
        self.save_document_button.set_action_name('win.save')
        self.pack_end(self.save_document_button)

        # help and preview toggles
        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.preview_toggle = Gtk.ToggleButton()
        self.preview_toggle.set_child(Gtk.Image.new_from_icon_name('view-paged-symbolic'))
        self.preview_toggle.set_can_focus(False)
        preview_shortcut = KeybindParser.to_display(KeybindParser.get_shortcut('shortcut_preview', 'app'))
        self.preview_toggle.set_tooltip_text(_('Toggle preview') + ' (' + preview_shortcut + ')')
        box.append(self.preview_toggle)
        self.help_toggle = Gtk.ToggleButton()
        self.help_toggle.set_child(Gtk.Image.new_from_icon_name('help-browser-symbolic'))
        self.help_toggle.set_can_focus(False)
        help_shortcut = KeybindParser.to_display(KeybindParser.get_shortcut('shortcut_help', 'app'))
        self.help_toggle.set_tooltip_text(_('Toggle help') + ' (' + help_shortcut + ')')
        box.append(self.help_toggle)
        box.get_style_context().add_class('linked')
        self.pack_end(box)

        # build button wrapper
        self.build_wrapper = Gtk.CenterBox()
        self.build_wrapper.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.pack_end(self.build_wrapper)

        # title / open documents popover
        self.open_docs_popover = PopoverManager.create_popover('document_switcher')

        self.document_name_label = Gtk.Label()
        self.document_name_label.get_style_context().add_class('title')
        self.document_name_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.document_folder_label = Gtk.Label()
        self.document_folder_label.get_style_context().add_class('subtitle')
        self.document_folder_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.document_arrow = Gtk.Image.new_from_icon_name('pan-down-symbolic')
        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        vbox.append(self.document_name_label)
        vbox.append(self.document_folder_label)
        hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        hbox.append(vbox)
        hbox.append(self.document_arrow)
        hbox.set_valign(Gtk.Align.CENTER)

        self.center_button = PopoverManager.create_popover_button('document_switcher')
        self.center_button.get_style_context().add_class('flat')
        self.center_button.get_style_context().add_class('open-docs-popover-button')
        show_open_docs_shortcut = KeybindParser.to_display(KeybindParser.get_shortcut('shortcut_show_open_docs', 'app'))
        self.center_button.set_tooltip_text(_('Show open documents') + ' (' + show_open_docs_shortcut + ')')
        self.center_button.set_can_focus(False)
        self.center_button.set_child(hbox)
        self.center_button.set_valign(Gtk.Align.FILL)

        self.center_label_welcome = Gtk.Label.new(_('Welcome to Setzer'))
        self.center_label_welcome.get_style_context().add_class('title')
        self.center_label_welcome.set_valign(Gtk.Align.FILL)

        self.center_widget = Gtk.Stack()
        self.center_widget.set_valign(Gtk.Align.FILL)
        self.center_widget.add_named(self.center_button, 'button')
        self.center_widget.add_named(self.center_label_welcome, 'welcome')

        self.set_title_widget(self.center_widget)



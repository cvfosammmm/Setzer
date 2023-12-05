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


class HamburgerMenuView(Popover):

    def __init__(self, popover_manager):
        Popover.__init__(self, popover_manager)

        self.set_width(306)

        self.button_save_as = MenuBuilder.create_button(_('Save Document As') + '...', shortcut=_('Shift') + '+' + _('Ctrl') + '+S')
        self.button_save_as.set_action_name('win.save-as')
        self.add_closing_button(self.button_save_as)

        self.button_save_all = MenuBuilder.create_button(_('Save All Documents'))
        self.button_save_all.set_action_name('win.save-all')
        self.add_closing_button(self.button_save_all)

        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))

        self.add_menu_button(_('Session'), 'session')

        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))

        self.button_preferences = MenuBuilder.create_button(_('Preferences'))
        self.button_preferences.set_action_name('win.show-preferences-dialog')
        self.add_closing_button(self.button_preferences)

        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))

        self.button_shortcuts = MenuBuilder.create_button(_('Keyboard Shortcuts'), shortcut=_('Ctrl') + '+?')
        self.button_shortcuts.set_action_name('win.show-shortcuts-dialog')
        self.add_closing_button(self.button_shortcuts)

        self.button_about = MenuBuilder.create_button(_('About'))
        self.button_about.set_action_name('win.show-about-dialog')
        self.add_closing_button(self.button_about)

        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))

        self.button_close_all = MenuBuilder.create_button(_('Close All Documents'))
        self.button_close_all.set_action_name('win.close-all-documents')
        self.add_closing_button(self.button_close_all)

        self.button_close_active = MenuBuilder.create_button(_('Close Document'), shortcut=_('Ctrl') + '+W')
        self.button_close_active.set_action_name('win.close-active-document')
        self.add_closing_button(self.button_close_active)

        self.button_quit = MenuBuilder.create_button(_('Quit'), shortcut=_('Ctrl') + '+Q')
        self.button_quit.set_action_name('win.quit')
        self.add_closing_button(self.button_quit)

        # session submenu
        self.add_page('session', _('Session'))

        self.session_explaination = Gtk.Label.new(_('Save the list of open documents in a session file\nand restore it later, a convenient way to work\non multiple projects.'))
        self.session_explaination.set_xalign(0)
        self.session_explaination.get_style_context().add_class('explaination')
        self.session_explaination.set_margin_top(8)
        self.session_explaination.set_margin_bottom(11)

        self.button_restore_session = MenuBuilder.create_button(_('Restore Previous Session') + '...')
        self.button_save_session = MenuBuilder.create_button(_('Save Current Session') + '...')
        self.button_save_session.set_action_name('win.save-session')

        self.session_box_separator = Gtk.Separator()
        self.session_box_separator.set_visible(False)

        self.prev_sessions_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        self.add_widget(self.session_explaination, pagename='session')
        self.add_widget(self.button_restore_session, pagename='session')
        self.register_button_for_keyboard_navigation(self.button_restore_session, pagename='session')
        self.add_closing_button(self.button_save_session, pagename='session')
        self.add_widget(self.session_box_separator, pagename='session')
        self.add_widget(self.prev_sessions_box, pagename='session')



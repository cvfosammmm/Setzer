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
from gi.repository import Gtk, Gdk, GLib

from setzer.popovers.helpers.popover_menu_builder import MenuBuilder


class Popover(Gtk.Box):

    def __init__(self, popover_manager):
        Gtk.Box.__init__(self)
        self.set_focusable(True)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_halign(Gtk.Align.START)
        self.set_valign(Gtk.Align.START)
        self.get_style_context().add_class('popover')

        self.popover_manager = popover_manager

        self.key_controller = Gtk.EventControllerKey()
        self.key_controller.connect('key-pressed', self.on_keypress)
        self.add_controller(self.key_controller)

        self.width = 0

        self.selected_button_id = {'main': None}
        self.buttons_by_id = {'main': list()}

        self.arrow = Gtk.DrawingArea()
        self.arrow.get_style_context().add_class('arrow')
        self.arrow_box = Gtk.CenterBox()
        self.arrow_box.set_start_widget(self.arrow)

        self.arrow_border = Gtk.DrawingArea()
        self.arrow_border.get_style_context().add_class('arrow-border')
        self.arrow_border_box = Gtk.CenterBox()
        self.arrow_border_box.set_start_widget(self.arrow_border)

        self.stack = Gtk.Stack()
        self.stack.set_vhomogeneous(False)

        self.content_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.content_box.get_style_context().add_class('content')
        self.content_box.append(self.arrow_border_box)
        self.content_box.append(self.stack)

        self.append(self.arrow_box)
        self.append(self.content_box)

        self.add_page('main')

    def on_keypress(self, controller, keyval, keycode, state):
        modifiers = Gtk.accelerator_get_default_mod_mask()

        if (state & modifiers, keyval) == (0, Gdk.keyval_from_name('Escape')):
            self.popover_manager.popdown()

        if (state & modifiers, keyval) == (0, Gdk.keyval_from_name('Return')):
            self.activate_selected_button()

        if (state & modifiers, keyval) == (Gdk.ModifierType.ALT_MASK, Gdk.keyval_from_name('Right')):
            self.activate_selected_menu_button()

        if (state & modifiers, keyval) == (Gdk.ModifierType.ALT_MASK, Gdk.keyval_from_name('Left')):
            if self.stack.get_visible_child_name() != 'main':
                self.show_page(None, 'main', Gtk.StackTransitionType.SLIDE_LEFT)

        if (state & modifiers, keyval) == (0, Gdk.keyval_from_name('Down')):
            self.select_next_button()

        if (state & modifiers, keyval) == (0, Gdk.keyval_from_name('Tab')):
            self.select_next_button()

        if (state & modifiers, keyval) == (0, Gdk.keyval_from_name('Up')):
            self.select_previous_button()

        if (state & modifiers, keyval) == (Gdk.ModifierType.SHIFT_MASK, Gdk.keyval_from_name('ISO_Left_Tab')):
            self.select_previous_button()

        return True

    def add_page(self, pagename='main', label=None):
        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.stack.add_named(box, pagename)

        if label != None:
            button_box = Gtk.CenterBox()
            button_box.set_orientation(Gtk.Orientation.HORIZONTAL)
            button_box.set_center_widget(Gtk.Label.new(label))
            button_box.set_start_widget(Gtk.Image.new_from_icon_name('pan-start-symbolic'))

            button = Gtk.Button()
            button.set_child(button_box)
            button.get_style_context().add_class('header')
            button.connect('clicked', self.show_page, 'main', Gtk.StackTransitionType.SLIDE_LEFT)

            self.register_button_for_keyboard_navigation(button, pagename)
            self.add_widget(button, pagename)

    def add_menu_button(self, title, menu_name):
        button = MenuBuilder.create_menu_button(title)
        button.connect('clicked', self.show_page, menu_name, Gtk.StackTransitionType.SLIDE_RIGHT)
        self.register_button_for_keyboard_navigation(button, 'main')
        self.add_widget(button)

    def add_before_after_item(self, pagename, title, commands, icon=None, shortcut=None):
        button = MenuBuilder.create_button(title, icon_name=icon, shortcut=shortcut)
        button.set_action_name('win.insert-before-after')
        button.set_action_target_value(GLib.Variant('as', commands))
        self.add_closing_button(button, pagename)

    def add_insert_symbol_item(self, pagename, title, command, icon=None, shortcut=None):
        button = MenuBuilder.create_button(title, icon_name=icon, shortcut=shortcut)
        button.set_action_name('win.insert-symbol')
        button.set_action_target_value(GLib.Variant('as', command))
        self.add_closing_button(button, pagename)

    def add_action_button(self, pagename, title, action_name, parameter=None, icon=None, shortcut=None):
        button = MenuBuilder.create_button(title, icon_name=icon, shortcut=shortcut)
        button.set_action_name(action_name)
        if parameter != None:
            button.set_action_target_value(parameter)
        self.add_closing_button(button, pagename)
        return button

    def add_closing_button(self, button, pagename='main'):
        self.register_button_for_keyboard_navigation(button, pagename)
        self.add_widget(button, pagename)
        button.connect('clicked', self.on_closing_button_click)

    def on_closing_button_click(self, button):
        self.popover_manager.popdown()

    def add_widget(self, widget, pagename='main'):
        box = self.stack.get_child_by_name(pagename)
        box.append(widget)

    def register_button_for_keyboard_navigation(self, button, pagename='main'):
        if pagename not in self.buttons_by_id:
            self.selected_button_id[pagename] = None
            self.buttons_by_id[pagename] = list()
        button.set_can_focus(False)
        motion_controller = Gtk.EventControllerMotion()
        motion_controller.connect('enter', self.button_on_motion)
        motion_controller.connect('motion', self.button_on_motion)
        motion_controller.connect('leave', self.button_on_leave)
        button.add_controller(motion_controller)
        self.buttons_by_id[pagename].append(button)

    def button_on_motion(self, controller, x, y):
        pagename = self.stack.get_visible_child_name()
        try:
            button_id = self.buttons_by_id[pagename].index(controller.get_widget())
        except ValueError: pass
        else:
            self.set_selected_button(pagename, button_id)

    def button_on_leave(self, controller):
        pagename = self.stack.get_visible_child_name()
        try:
            button_id = self.buttons_by_id[pagename].index(controller.get_widget())
        except ValueError: pass
        else:
            if self.selected_button_id[pagename] == button_id and controller.get_widget().get_sensitive():
                self.set_selected_button(pagename, None)

    def set_width(self, width):
        self.width = width
        self.set_size_request(width, -1)

    def show_page(self, button, pagename, transition_type):
        self.stack.set_transition_type(transition_type)
        self.stack.set_visible_child_name(pagename)
        self.set_selected_button(pagename, None)

    def activate_selected_button(self):
        pagename = self.stack.get_visible_child_name()
        button_id = self.selected_button_id[pagename]
        if button_id != None:
            button = self.buttons_by_id[pagename][button_id]
            button.activate()

    def activate_selected_menu_button(self):
        pagename = self.stack.get_visible_child_name()
        button_id = self.selected_button_id[pagename]
        if button_id != None:
            button = self.buttons_by_id[pagename][button_id]
            if button.has_css_class('menu'):
                button.activate()

    def select_next_button(self):
        pagename = self.stack.get_visible_child_name()
        button_id = self.selected_button_id[pagename]
        no_buttons = len(self.buttons_by_id[pagename])
        if button_id == None:
            buttons = range(no_buttons)
        else:
            buttons = list(range(((button_id + 1) % no_buttons), no_buttons)) + list(range((button_id + 1) % no_buttons))
        for button_id in buttons:
            if self.buttons_by_id[pagename][button_id].get_sensitive():
                self.set_selected_button(pagename, button_id)
                break

    def select_previous_button(self):
        pagename = self.stack.get_visible_child_name()
        button_id = self.selected_button_id[pagename]
        no_buttons = len(self.buttons_by_id[pagename])
        if button_id == None:
            buttons = range(no_buttons)
        else:
            buttons = list(range((button_id % no_buttons), no_buttons)) + list(range(button_id % no_buttons))
        for button_id in reversed(buttons):
            if self.buttons_by_id[pagename][button_id].get_sensitive():
                self.set_selected_button(pagename, button_id)
                break

    def set_selected_button(self, pagename, button_id):
        for button in self.buttons_by_id[pagename]:
            button.get_style_context().remove_class('highlight')

        self.selected_button_id[pagename] = button_id
        if button_id != None:
            self.buttons_by_id[pagename][button_id].get_style_context().add_class('highlight')



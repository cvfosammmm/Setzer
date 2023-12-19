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

from setzer.popovers.new_document.new_document import NewDocument
from setzer.popovers.document_chooser.document_chooser import DocumentChooser
from setzer.popovers.document_switcher.document_switcher import DocumentSwitcher
from setzer.popovers.hamburger_menu.hamburger_menu import HamburgerMenu
from setzer.popovers.shortcutsbar.math_menu import MathMenu
from setzer.popovers.shortcutsbar.beamer_menu import BeamerMenu
from setzer.popovers.shortcutsbar.bibliography_menu import BibliographyMenu
from setzer.popovers.shortcutsbar.document_menu import DocumentMenu
from setzer.popovers.shortcutsbar.object_menu import ObjectMenu
from setzer.popovers.shortcutsbar.quotes_menu import QuotesMenu
from setzer.popovers.shortcutsbar.text_menu import TextMenu
from setzer.popovers.preview_zoom_level.preview_zoom_level import PreviewZoomLevel
from setzer.popovers.context_menu.context_menu import ContextMenu
from setzer.popovers.helpers.popover_button import PopoverButton


class PopoverManager():

    popovers = dict()
    popover_buttons = dict()
    current_popover_name = None
    main_window = None
    workspace = None
    popoverlay = None
    inbetween = Gtk.DrawingArea()

    connected_functions = dict() # observers' functions to be called when change codes are emitted

    def init(main_window, workspace):
        PopoverManager.main_window = main_window
        PopoverManager.workspace = workspace
        PopoverManager.popoverlay = main_window.popoverlay
        PopoverManager.popoverlay.add_overlay(PopoverManager.inbetween)

        controller_click = Gtk.GestureClick()
        controller_click.connect('pressed', PopoverManager.on_click_inbetween)
        controller_click.set_button(1)
        PopoverManager.inbetween.add_controller(controller_click)

        PopoverManager.inbetween.set_can_target(False)

    def create_popover(name):
        popover = None
        if name == 'new_document': popover = NewDocument(PopoverManager)
        if name == 'open_document': popover = DocumentChooser(PopoverManager, PopoverManager.workspace)
        if name == 'document_switcher': popover = DocumentSwitcher(PopoverManager, PopoverManager.workspace)
        if name == 'hamburger_menu': popover = HamburgerMenu(PopoverManager, PopoverManager.workspace)
        if name == 'beamer_menu': popover = BeamerMenu(PopoverManager)
        if name == 'bibliography_menu': popover = BibliographyMenu(PopoverManager)
        if name == 'document_menu': popover = DocumentMenu(PopoverManager)
        if name == 'math_menu': popover = MathMenu(PopoverManager)
        if name == 'object_menu': popover = ObjectMenu(PopoverManager)
        if name == 'quotes_menu': popover = QuotesMenu(PopoverManager)
        if name == 'text_menu': popover = TextMenu(PopoverManager)
        if name == 'preview_zoom_level': popover = PreviewZoomLevel(PopoverManager, PopoverManager.workspace)
        if name == 'context_menu': popover = ContextMenu(PopoverManager, PopoverManager.workspace)

        PopoverManager.popovers[name] = popover
        return popover

    def create_popover_button(name):
        popover_button = PopoverButton(name, PopoverManager)
        PopoverManager.popover_buttons[name] = popover_button
        return popover_button

    def popup_at_button(name):
        if PopoverManager.current_popover_name == name: return
        if PopoverManager.current_popover_name != None: PopoverManager.popdown()

        button = PopoverManager.popover_buttons[name]
        allocation = button.compute_bounds(PopoverManager.main_window).out_bounds

        x = allocation.origin.x + allocation.size.width / 2
        y = allocation.origin.y + allocation.size.height

        popover = PopoverManager.popovers[name]
        window_width = PopoverManager.main_window.get_width()
        arrow_width = 10
        arrow_border_width = 36
        if x - popover.view.width / 2 < 0:
            popover.view.set_margin_start(0)
            popover.view.arrow.set_margin_start(x - arrow_width / 2)
            popover.view.arrow_border.set_margin_start(x - arrow_border_width / 2)
        elif x - popover.view.width / 2 > window_width - popover.view.width:
            popover.view.set_margin_start(window_width - popover.view.width)
            popover.view.arrow.set_margin_start(x - window_width + popover.view.width - arrow_width / 2)
            popover.view.arrow_border.set_margin_start(x - window_width + popover.view.width - arrow_border_width / 2)
        else:
            popover.view.set_margin_start(x - popover.view.width / 2)
            popover.view.arrow.set_margin_start(popover.view.width / 2 - arrow_width / 2)
            popover.view.arrow_border.set_margin_start(popover.view.width / 2 - arrow_border_width / 2)
        popover.view.set_margin_top(max(0, y))

        PopoverManager.current_popover_name = name
        PopoverManager.popoverlay.add_overlay(popover.view)
        PopoverManager.inbetween.set_can_target(True)

        popover.view.grab_focus()
        button.set_active(True)

        PopoverManager.add_change_code('popup', name)

    def popdown():
        if PopoverManager.current_popover_name == None: return

        name = PopoverManager.current_popover_name
        popover = PopoverManager.popovers[name]

        PopoverManager.popoverlay.remove_overlay(popover.view)
        PopoverManager.current_popover_name = None
        PopoverManager.inbetween.set_can_target(False)

        popover.view.show_page(None, 'main', Gtk.StackTransitionType.NONE)
        if name in PopoverManager.popover_buttons:
            PopoverManager.popover_buttons[name].set_active(False)

        document = PopoverManager.workspace.get_active_document()
        if document != None:
            document.source_view.grab_focus()

        PopoverManager.add_change_code('popdown', name)

    def on_click_inbetween(controller, n_press, x, y):
        PopoverManager.popdown()

    def add_change_code(change_code, parameter=None):
        if change_code in PopoverManager.connected_functions:
            for callback in PopoverManager.connected_functions[change_code]:
                if parameter != None:
                    callback(parameter)
                else:
                    callback()

    def connect(change_code, callback):
        if change_code in PopoverManager.connected_functions:
            PopoverManager.connected_functions[change_code].add(callback)
        else:
            PopoverManager.connected_functions[change_code] = {callback}

    def disconnect(change_code, callback):
        if change_code in PopoverManager.connected_functions:
            PopoverManager.connected_functions[change_code].discard(callback)
            if len(PopoverManager.connected_functions[change_code]) == 0:
                del(PopoverManager.connected_functions[change_code])



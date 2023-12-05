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
from gi.repository import Gtk, GLib
from gi.repository import Gdk, GdkPixbuf

import os

import setzer.widgets.filechooser_button.filechooser_button as filechooser_button
from setzer.dialogs.helpers.dialog_viewgtk import DialogView


class IncludeBibTeXFileView(DialogView):

    def __init__(self, main_window):
        DialogView.__init__(self, main_window)

        self.set_default_size(400, 300)
        self.set_can_focus(False)
        self.get_style_context().add_class('include-bibtex-file-dialog')
        self.headerbar.set_show_title_buttons(False)
        self.headerbar.set_title_widget(Gtk.Label.new(_('Include BibTeX file')))
        self.topbox.set_size_request(400, -1)

        self.cancel_button = Gtk.Button.new_with_mnemonic(_('_Cancel'))
        self.cancel_button.set_can_focus(False)
        self.headerbar.pack_start(self.cancel_button)

        self.include_button = Gtk.Button.new_with_mnemonic(_('_Include'))
        self.include_button.set_can_focus(False)
        self.include_button.get_style_context().add_class('suggested-action')
        self.headerbar.pack_end(self.include_button)

        self.content = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.content.set_margin_start(18)
        self.content.set_margin_end(18)
        label = Gtk.Label.new(_('BibTeX file to include'))
        label.set_xalign(0)
        label.set_margin_bottom(3)
        label.set_margin_top(18)
        self.content.append(label)
        self.file_chooser_button = filechooser_button.FilechooserButton(self)
        self.file_chooser_button.set_title(_('Select a BibTeX File'))
        self.content.append(self.file_chooser_button.view)

        label = Gtk.Label.new(_('Bibliography style'))
        label.set_xalign(0)
        label.set_margin_bottom(3)
        label.set_margin_top(18)
        self.content.append(label)

        self.style_switcher = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.style_switcher.get_style_context().add_class('linked')
        self.style_buttons = dict()
        self.content.append(self.style_switcher)

        self.natbib_style_switcher = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.natbib_style_switcher.get_style_context().add_class('linked')
        self.natbib_style_buttons = dict()
        self.content.append(self.natbib_style_switcher)

        self.natbib_option = Gtk.CheckButton.new_with_label(_('Show bibliography styles for the \'natbib\' package'))
        self.natbib_option.set_margin_top(18)
        self.natbib_option.set_can_focus(False)
        self.content.append(self.natbib_option)

        self.preview_stack_wrapper_wrapper = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.preview_stack_wrapper = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.preview_stack_wrapper.get_style_context().add_class('stack-wrapper')
        self.preview_stack_wrapper.set_margin_top(18)
        self.preview_stack_wrapper.set_margin_bottom(18)
        self.preview_stack = Gtk.Stack()
        self.preview_stack_wrapper.append(self.preview_stack)
        self.preview_stack_wrapper_wrapper.append(self.preview_stack_wrapper)
        self.content.append(self.preview_stack_wrapper_wrapper)

        self.natbib_preview_stack_wrapper_wrapper = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.natbib_preview_stack_wrapper = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.natbib_preview_stack_wrapper.get_style_context().add_class('stack-wrapper')
        self.natbib_preview_stack_wrapper.set_margin_top(18)
        self.natbib_preview_stack_wrapper.set_margin_bottom(18)
        self.natbib_preview_stack = Gtk.Stack()
        self.natbib_preview_stack_wrapper.append(self.natbib_preview_stack)
        self.natbib_preview_stack_wrapper_wrapper.append(self.natbib_preview_stack_wrapper)
        self.content.append(self.natbib_preview_stack_wrapper_wrapper)

        self.content.set_vexpand(True)
        self.topbox.append(self.content)



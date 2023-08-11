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
gi.require_version('GtkSource', '5')
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Pango
from gi.repository import GtkSource

import os, os.path
import shutil
import xml.etree.ElementTree as ET

from setzer.app.service_locator import ServiceLocator
from setzer.app.font_manager import FontManager


class PageFontColor(object):

    def __init__(self, preferences, settings, main_window):
        self.view = PageFontColorView()
        self.preferences = preferences
        self.settings = settings
        self.main_window = main_window

    def init(self):
        self.update_switchers()
        self.view.style_switcher.set_active_id(self.settings.get_value('preferences', 'color_scheme'))
        self.view.style_switcher.connect('changed', self.on_style_switcher_changed)

        self.update_font_color_preview()

        source_language_manager = ServiceLocator.get_source_language_manager()
        source_language = source_language_manager.get_language('latex')
        self.view.source_buffer.set_language(source_language)
        self.update_font_color_preview()

        self.view.font_chooser_button.set_font(self.settings.get_value('preferences', 'font_string'))
        self.view.font_chooser_button.connect('font-set', self.on_font_set)
        self.view.option_use_system_font.set_active(self.settings.get_value('preferences', 'use_system_font'))
        self.view.font_chooser_revealer.set_reveal_child(not self.view.option_use_system_font.get_active())
        self.view.option_use_system_font.connect('toggled', self.on_use_system_font_toggled)

    def on_use_system_font_toggled(self, button):
        self.view.font_chooser_revealer.set_reveal_child(not button.get_active())
        self.settings.set_value('preferences', 'use_system_font', button.get_active())

    def on_font_set(self, button):
        if button.get_font_size() < 6 * Pango.SCALE:
            font_desc = button.get_font_desc()
            font_desc.set_size(6 * Pango.SCALE)
            button.set_font_desc(font_desc)
        elif button.get_font_size() > 24 * Pango.SCALE:
            font_desc = button.get_font_desc()
            font_desc.set_size(24 * Pango.SCALE)
            button.set_font_desc(font_desc)
            
        self.settings.set_value('preferences', 'font_string', button.get_font())

    def on_style_switcher_changed(self, switcher):
        value = switcher.get_active_id()
        if value != None:
            self.settings.set_value('preferences', 'color_scheme', value)
            self.update_font_color_preview()

    def get_scheme_id_from_file(self, pathname):
        tree = ET.parse(pathname)
        root = tree.getroot()
        return root.attrib['id']

    def get_scheme_filename_from_id(self, scheme_id):
        directory_pathname = os.path.join(ServiceLocator.get_config_folder(), 'syntax_schemes')
        for filename in os.listdir(directory_pathname):
            tree = ET.parse(os.path.join(directory_pathname, filename))
            root = tree.getroot()
            if root.attrib['id'] == scheme_id:
                return os.path.join(directory_pathname, filename)

    def update_switchers(self):
        active_id = self.settings.get_value('preferences', 'color_scheme')
        set_active_id = False
        for name in ['default']:
            self.view.style_switcher.append(name, name)
        directory_pathname = os.path.join(ServiceLocator.get_config_folder(), 'syntax_schemes')
        if os.path.isdir(directory_pathname):
            for filename in os.listdir(directory_pathname):
                name = self.get_scheme_id_from_file(os.path.join(directory_pathname, filename))
                if name == active_id: set_active_id = True
                self.view.style_switcher.append(name, name)
        if set_active_id:
            self.view.style_switcher.set_active_id(active_id)
        else:
            self.view.style_switcher.set_active_id('default')

    def update_font_color_preview(self):
        source_style_scheme_manager = ServiceLocator.get_source_style_scheme_manager()
        name = self.settings.get_value('preferences', 'color_scheme')
        source_style_scheme_light = source_style_scheme_manager.get_scheme(name)
        self.view.source_buffer.set_style_scheme(source_style_scheme_light)


class PageFontColorView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.set_margin_start(18)
        self.set_margin_end(18)
        self.set_margin_top(18)
        self.set_margin_bottom(18)
        self.get_style_context().add_class('preferences-page')

        label = Gtk.Label()
        label.set_markup('<b>' + _('Font') + '</b>')
        label.set_xalign(0)
        label.set_margin_bottom(6)
        self.append(label)

        font_string = FontManager.get_system_font()
        self.option_use_system_font = Gtk.CheckButton.new_with_label(_('Use the system fixed width font (' + font_string + ')'))
        self.option_use_system_font.set_margin_bottom(18)
        self.append(self.option_use_system_font)

        self.font_chooser_revealer = Gtk.Revealer()
        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        label = Gtk.Label()
        label.set_markup(_('Set Editor Font:'))
        label.set_xalign(0)
        label.set_margin_bottom(6)
        vbox.append(label)

        self.font_chooser_button = Gtk.FontButton()
        self.font_chooser_button.set_margin_bottom(18)
        hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        hbox.append(self.font_chooser_button)
        vbox.append(hbox)
        self.font_chooser_revealer.set_child(vbox)
        self.append(self.font_chooser_revealer)

        label = Gtk.Label()
        label.set_markup('<b>' + _('Color Scheme') + '</b>')
        label.set_xalign(0)
        label.set_margin_bottom(6)
        self.append(label)

        self.style_switcher = Gtk.ComboBoxText()
        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.set_margin_bottom(18)
        box.append(self.style_switcher)
        self.append(box)

        label = Gtk.Label()
        label.set_markup('<b>' + _('Preview') + '</b>')
        label.set_xalign(0)
        label.set_margin_bottom(6)
        self.append(label)

        self.preview_wrapper = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.preview_wrapper.get_style_context().add_class('preview')
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_min_content_height(162)
        self.source_view = GtkSource.View()
        self.source_view.set_editable(False)
        self.source_view.set_cursor_visible(False)
        self.source_view.set_monospace(True)
        self.source_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.source_view.set_show_line_numbers(False)
        self.source_view.set_highlight_current_line(False)
        scrolled_window.set_child(self.source_view)
        self.source_buffer = self.source_view.get_buffer()
        self.source_buffer.set_highlight_matching_brackets(False)
        self.source_buffer.set_text('''% Syntax highlighting preview
\\documentclass[letterpaper,11pt]{article}
\\usepackage{amsmath}
\\usepackage{amssymb}
\\begin{document}
\\section{Preview}
This is a \\textit{preview}, for $x, y \in \mathbb{R}: x \leq y$ or $x > y$.
\\end{document}''')
        self.source_buffer.place_cursor(self.source_buffer.get_start_iter())
        self.preview_wrapper.append(scrolled_window)
        self.append(self.preview_wrapper)



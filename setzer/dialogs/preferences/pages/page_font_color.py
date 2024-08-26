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
        self.view.style_switcher.connect('child-activated', self.on_style_switcher_changed)
        self.view.option_recolor_pdf.set_active(self.settings.get_value('preferences', 'recolor_pdf'))
        self.view.option_recolor_pdf.connect('toggled', self.on_recolor_pdf_option_toggled)

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

    def on_recolor_pdf_option_toggled(self, button):
        self.settings.set_value('preferences', 'recolor_pdf', button.get_active())

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

    def on_style_switcher_changed(self, switcher, child_widget):
        style_scheme_preview = child_widget.get_child()
        value = style_scheme_preview.get_scheme().get_name()
        if value != None:
            self.settings.set_value('preferences', 'color_scheme', value)
            self.update_font_color_preview()

    def get_scheme_id_from_file(self, pathname):
        tree = ET.parse(pathname)
        root = tree.getroot()
        return root.attrib['id']

    def update_switchers(self):
        names = ['default', 'default-dark']
        dirname = os.path.join(ServiceLocator.get_config_folder(), 'themes')
        if os.path.isdir(dirname):
            names += [self.get_scheme_id_from_file(os.path.join(dirname, file)) for file in os.listdir(dirname)]
        for name in names:
            self.view.style_switcher.add_style(name)

        active_id = self.settings.get_value('preferences', 'color_scheme')
        if active_id in names: self.view.style_switcher.select_style(active_id)
        else: self.view.style_switcher.select_style('default')

    def update_font_color_preview(self):
        source_style_scheme_manager = ServiceLocator.get_source_style_scheme_manager()
        name = self.settings.get_value('preferences', 'color_scheme')
        source_style_scheme_light = source_style_scheme_manager.get_scheme(name)
        self.view.source_buffer.set_style_scheme(source_style_scheme_light)


class PageFontColorView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.set_margin_top(18)
        self.get_style_context().add_class('preferences-page')

        label = Gtk.Label()
        label.set_markup('<b>' + _('Font') + '</b>')
        label.set_xalign(0)
        label.set_margin_start(18)
        label.set_margin_bottom(6)
        self.append(label)

        font_string = FontManager.get_system_font()
        self.option_use_system_font = Gtk.CheckButton.new_with_label(_('Use the system fixed width font (' + font_string + ')'))
        self.option_use_system_font.set_margin_start(18)
        self.option_use_system_font.set_margin_bottom(18)
        self.append(self.option_use_system_font)

        self.font_chooser_revealer = Gtk.Revealer()
        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        vbox.set_margin_start(18)
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
        label.set_margin_start(18)
        label.set_margin_bottom(7)
        self.append(label)

        self.style_switcher = StyleSwitcher()
        self.style_switcher.set_margin_start(18)
        self.style_switcher.set_margin_bottom(18)
        self.append(self.style_switcher)

        label = Gtk.Label()
        label.set_markup('<b>' + _('Options') + '</b>')
        label.set_xalign(0)
        label.set_margin_start(18)
        label.set_margin_bottom(6)
        self.append(label)

        self.option_recolor_pdf = Gtk.CheckButton.new_with_label(_('Show .pdf in theme colors'))
        self.option_recolor_pdf.set_margin_start(18)
        self.option_recolor_pdf.set_margin_bottom(18)
        self.append(self.option_recolor_pdf)

        self.preview_wrapper = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.preview_wrapper.get_style_context().add_class('preview')
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_max_content_height(240)
        scrolled_window.set_propagate_natural_height(True)
        self.source_view = GtkSource.View()
        self.source_view.set_editable(False)
        self.source_view.set_cursor_visible(False)
        self.source_view.set_monospace(True)
        self.source_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.source_view.set_show_line_numbers(False)
        self.source_view.set_highlight_current_line(False)
        self.source_view.set_left_margin(0)
        scrolled_window.set_child(self.source_view)
        self.source_buffer = self.source_view.get_buffer()
        self.source_buffer.set_highlight_matching_brackets(False)
        self.source_buffer.set_text('''% Syntax highlighting preview
\\documentclass[letterpaper,11pt]{article}
\\usepackage{amsmath}
\\usepackage{amssymb}
\\begin{document}
\\section{Preview}
This is a \\textit{preview}, for $x, y \\in \\mathbb{R}: x \\leq y$ or $x > y$.
\\end{document}''')
        self.source_buffer.place_cursor(self.source_buffer.get_start_iter())
        self.preview_wrapper.append(scrolled_window)
        self.append(self.preview_wrapper)


class StyleSwitcher(Gtk.FlowBox):

    def __init__(self):
        Gtk.FlowBox.__init__(self)
        self.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.set_row_spacing(6)
        self.set_activate_on_single_click(True)
        self.get_style_context().add_class('theme_previews')

        self.positions = dict()
        self.current_max = 0
        self.current_index = None

        self.connect('selected-children-changed', self.on_child_activated)

    def add_style(self, name):
        style_manager = ServiceLocator.get_source_style_scheme_manager()
        widget = GtkSource.StyleSchemePreview.new(style_manager.get_scheme(name))
        self.append(widget)
        self.positions[name] = self.current_max
        self.current_max += 1

    def select_style(self, name):
        self.select_child(self.get_child_at_index(self.positions[name]))

    def on_child_activated(self, switcher):
        if self.current_index != None:
            self.get_child_at_index(self.current_index).get_child().set_selected(False)

        child_widget = self.get_selected_children()[0]
        name = child_widget.get_child().get_scheme().get_name()
        child_widget.get_child().set_selected(True)
        self.current_index = self.positions[name]



#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017, 2018 Robert Griesel
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
gi.require_version('GtkSource', '4')
from gi.repository import Gtk
from gi.repository import GtkSource

from setzer.app.service_locator import ServiceLocator


class PageFontColor(object):

    def __init__(self, preferences, settings):
        self.view = PageFontColorView()
        self.preferences = preferences
        self.settings = settings

    def init(self):
        for button in self.view.style_switcher.get_children():
            name = button.get_child().get_children()[0].get_text()
            button.connect('toggled', self.preferences.on_radio_button_toggle, 'syntax_scheme', name)
            button.set_active(self.settings.get_value('preferences', 'syntax_scheme') == name)

        for button in self.view.style_switcher_dark_mode.get_children():
            name = button.get_child().get_children()[0].get_text()
            button.connect('toggled', self.preferences.on_radio_button_toggle, 'syntax_scheme_dark_mode', name)
            button.set_active(self.settings.get_value('preferences', 'syntax_scheme_dark_mode') == name)

        self.view.style_switcher_label_light.connect('clicked', self.set_style_switcher_page, 'light')
        self.view.style_switcher_label_dark.connect('clicked', self.set_style_switcher_page, 'dark')

        source_language_manager = ServiceLocator.get_source_language_manager()
        source_language = source_language_manager.get_language('latex')
        self.view.source_buffer.set_language(source_language)
        self.update_font_color_preview()

        if ServiceLocator.get_is_dark_mode():
            self.view.style_switcher_label_dark.clicked()

    def set_style_switcher_page(self, button, pagename):
        self.view.style_switcher_label_light.get_style_context().remove_class('active')
        self.view.style_switcher_label_dark.get_style_context().remove_class('active')
        button.get_style_context().add_class('active')
        self.view.style_switcher_stack.set_visible_child_name(pagename)
        self.update_font_color_preview()

    def update_font_color_preview(self):
        source_style_scheme_manager = ServiceLocator.get_source_style_scheme_manager()
        name = self.settings.get_value('preferences', 'syntax_scheme')
        source_style_scheme_light = source_style_scheme_manager.get_scheme(name)
        name = self.settings.get_value('preferences', 'syntax_scheme_dark_mode')
        source_style_scheme_dark = source_style_scheme_manager.get_scheme(name)
        if self.view.style_switcher_label_light.get_style_context().has_class('active'):
            self.view.source_buffer.set_style_scheme(source_style_scheme_light)
            self.view.preview_wrapper.get_style_context().remove_class('light-bg')
            self.view.preview_wrapper.get_style_context().remove_class('dark-bg')
            if ServiceLocator.get_is_dark_mode():
                self.view.preview_wrapper.get_style_context().add_class('light-bg')
        else:
            self.view.source_buffer.set_style_scheme(source_style_scheme_dark)
            self.view.preview_wrapper.get_style_context().remove_class('light-bg')
            self.view.preview_wrapper.get_style_context().remove_class('dark-bg')
            if not ServiceLocator.get_is_dark_mode():
                self.view.preview_wrapper.get_style_context().add_class('dark-bg')


class PageFontColorView(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)

        self.set_margin_start(18)
        self.set_margin_end(18)
        self.set_margin_top(18)
        self.set_margin_bottom(18)
        self.get_style_context().add_class('preferences-page')

        self.style_switcher_label_light = Gtk.Button()
        self.style_switcher_label_light.set_label(_('Light Color Scheme'))
        self.style_switcher_label_light.get_child().set_xalign(0)
        self.style_switcher_label_light.set_margin_bottom(6)
        self.style_switcher_label_light.get_style_context().add_class('style-switcher-label')
        self.style_switcher_label_light.get_style_context().add_class('active')

        self.style_switcher_label_dark = Gtk.Button()
        self.style_switcher_label_dark.set_label(_('Dark Color Scheme'))
        self.style_switcher_label_dark.get_child().set_xalign(0)
        self.style_switcher_label_dark.set_margin_bottom(6)
        self.style_switcher_label_dark.get_style_context().add_class('style-switcher-label')

        self.style_switcher_label_box = Gtk.HBox()
        self.style_switcher_label_box.pack_start(self.style_switcher_label_light, False, False, 0)
        separator = Gtk.Label(' | ')
        separator.set_margin_bottom(6)
        self.style_switcher_label_box.pack_start(separator, False, False, 0)
        self.style_switcher_label_box.pack_start(self.style_switcher_label_dark, False, False, 0)
        self.pack_start(self.style_switcher_label_box, False, False, 0)

        self.style_switcher = Gtk.HBox()
        self.style_switcher.get_style_context().add_class('linked')
        self.style_switcher.set_margin_bottom(18)
        first_button = None
        for name in ['default']:
            button = Gtk.RadioButton()
            if first_button == None: first_button = button
            box = Gtk.HBox()
            box.pack_start(Gtk.Label(name), False, False, 0)
            box.set_margin_right(6)
            box.set_margin_left(4)
            button.add(box)
            button.set_mode(False)
            button.join_group(first_button)
            self.style_switcher.pack_start(button, False, False, 0)

        self.style_switcher_dark_mode = Gtk.HBox()
        self.style_switcher_dark_mode.get_style_context().add_class('linked')
        self.style_switcher_dark_mode.set_margin_bottom(18)
        first_button = None
        for name in ['default-dark']:
            button = Gtk.RadioButton()
            if first_button == None: first_button = button
            box = Gtk.HBox()
            box.pack_start(Gtk.Label(name), False, False, 0)
            box.set_margin_right(6)
            box.set_margin_left(4)
            button.add(box)
            button.set_mode(False)
            button.join_group(first_button)
            self.style_switcher_dark_mode.pack_start(button, False, False, 0)

        self.style_switcher_stack = Gtk.Stack()
        self.style_switcher_stack.add_named(self.style_switcher, 'light')
        self.style_switcher_stack.add_named(self.style_switcher_dark_mode, 'dark')
        self.pack_start(self.style_switcher_stack, False, False, 0)

        label = Gtk.Label()
        label.set_markup('<b>' + _('Preview') + '</b>')
        label.set_xalign(0)
        label.set_margin_bottom(6)
        self.pack_start(label, False, False, 0)

        self.preview_wrapper = Gtk.VBox()
        self.preview_wrapper.get_style_context().add_class('preview')
        self.source_view = GtkSource.View()
        self.source_view.set_editable(False)
        self.source_view.set_cursor_visible(False)
        self.source_view.set_monospace(True)
        self.source_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.source_view.set_show_line_numbers(False)
        self.source_view.set_highlight_current_line(False)
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
        self.preview_wrapper.pack_start(self.source_view, True, True, 0)
        self.pack_start(self.preview_wrapper, True, True, 0)



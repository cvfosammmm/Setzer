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
gi.require_version('GtkSource', '4')
gi.require_version('Handy', '1')
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Pango
from gi.repository import GtkSource
from gi.repository import Handy

import os, os.path
import shutil
import xml.etree.ElementTree as ET

from setzer.app.service_locator import ServiceLocator


class PageFontColor(object):

    def __init__(self, preferences, settings, main_window):
        self.view = PageFontColorView()
        self.preferences = preferences
        self.settings = settings
        self.main_window = main_window

    def init(self):
        self.update_switchers()
        self.view.style_switcher.set_active_id(self.settings.get_value('preferences', 'syntax_scheme'))
        self.view.style_switcher.connect('changed', self.on_style_switcher_changed, False)
        self.view.style_switcher_dark_mode.set_active_id(self.settings.get_value('preferences', 'syntax_scheme_dark_mode'))
        self.view.style_switcher_dark_mode.connect('changed', self.on_style_switcher_changed, True)

        color_scheme = self.settings.get_value('preferences', 'color_scheme')
        self.view.option_default_theme.set_active(color_scheme == 'default')
        self.view.option_force_light.set_active(color_scheme == 'force_light')
        self.view.option_force_dark.set_active(color_scheme == 'force_dark')
        self.view.option_default_theme.connect('toggled', self.on_color_scheme_switcher_changed, 'default')
        self.view.option_force_light.connect('toggled', self.on_color_scheme_switcher_changed, 'force_light')
        self.view.option_force_dark.connect('toggled', self.on_color_scheme_switcher_changed, 'force_dark')
        self.view.style_switcher_stack.set_visible_child_name('dark' if Handy.StyleManager.get_default().get_dark() else 'light')
        self.update_font_color_preview()
        self.update_remove_button()

        ip_state = self.settings.get_value('preferences', 'invert_pdf')
        self.view.option_invert_preview.set_active(ip_state)
        self.view.option_invert_preview.connect('toggled', self.on_ip_toggle_toggled)

        source_language_manager = ServiceLocator.get_source_language_manager()
        source_language = source_language_manager.get_language('latex')
        self.view.source_buffer.set_language(source_language)
        self.update_font_color_preview()

        self.view.add_scheme_button.connect('clicked', self.on_add_scheme_button_clicked)
        self.view.remove_scheme_button.connect('clicked', self.on_remove_scheme_button_clicked)

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

    def on_style_switcher_changed(self, switcher, is_dark_mode):
        if is_dark_mode:
            field = 'syntax_scheme_dark_mode'
        else:
            field = 'syntax_scheme'
        value = switcher.get_active_id()
        if value != None:
            self.settings.set_value('preferences', field, value)
            self.update_font_color_preview()
        self.update_remove_button()

    def update_remove_button(self):
        if self.view.style_switcher_stack.get_visible_child_name() == 'dark':
            scheme_id = self.view.style_switcher_dark_mode.get_active_id()
        else:
            scheme_id = self.view.style_switcher.get_active_id()
        if scheme_id in ['default', 'default-dark']:
            self.view.remove_scheme_button.set_sensitive(False)
        else:
            self.view.remove_scheme_button.set_sensitive(True)

    def on_add_scheme_button_clicked(self, button):
        dialog = AddSchemeDialog(self.main_window)
        pathname = dialog.run()
        if pathname != None:
            destination = os.path.join(ServiceLocator.get_config_folder(), 'syntax_schemes', os.path.basename(pathname))
            shutil.copyfile(pathname, destination)
            ServiceLocator.get_source_style_scheme_manager().force_rescan()
            self.update_switchers()
            scheme_id = self.get_scheme_id_from_file(destination)
            if ServiceLocator.get_is_dark_mode():
                self.view.style_switcher_dark_mode.set_active_id(scheme_id)
            else:
                self.view.style_switcher.set_active_id(scheme_id)

    def on_remove_scheme_button_clicked(self, button):
        if self.view.style_switcher_stack.get_visible_child_name() == 'dark':
            scheme_id = self.view.style_switcher_dark_mode.get_active_id()
        else:
            scheme_id = self.view.style_switcher.get_active_id()
        if not scheme_id in ['default', 'default-dark']:
            dialog = ReplaceConfirmationDialog(self.main_window)
            filename = self.get_scheme_filename_from_id(scheme_id)
            if dialog.run(scheme_id):
                os.remove(filename)
                self.update_switchers()

    def on_color_scheme_switcher_changed(self, switcher, value):
        if switcher.get_active():
            workspace = ServiceLocator.get_workspace()
            workspace.set_color_scheme(value)

            new_state = Handy.StyleManager.get_default().get_dark()
            workspace.actions.change_color_scheme_action.set_state(GLib.Variant.new_boolean(new_state))

            self.view.style_switcher_stack.set_visible_child_name('dark' if new_state else 'light')
            self.update_font_color_preview()
            self.update_remove_button()

    def on_ip_toggle_toggled(self, button):
        workspace = ServiceLocator.get_workspace()
        new_state = not workspace.actions.toggle_invert_pdf_action.get_state().get_boolean()
        workspace.actions.toggle_invert_pdf_action.set_state(GLib.Variant.new_boolean(new_state))
        workspace.set_invert_pdf(new_state)

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
        active_id = self.settings.get_value('preferences', 'syntax_scheme')
        active_id_dark_mode = self.settings.get_value('preferences', 'syntax_scheme_dark_mode')
        set_active_id = False
        set_active_id_dark_mode = False
        self.view.style_switcher.remove_all()
        for name in ['default']:
            self.view.style_switcher.append(name, name)
        self.view.style_switcher_dark_mode.remove_all()
        for name in ['default-dark']:
            self.view.style_switcher_dark_mode.append(name, name)
        directory_pathname = os.path.join(ServiceLocator.get_config_folder(), 'syntax_schemes')
        if os.path.isdir(directory_pathname):
            for filename in os.listdir(directory_pathname):
                name = self.get_scheme_id_from_file(os.path.join(directory_pathname, filename))
                if name == active_id: set_active_id = True
                if name == active_id_dark_mode: set_active_id_dark_mode = True
                self.view.style_switcher.append(name, name)
                self.view.style_switcher_dark_mode.append(name, name)
        if set_active_id:
            self.view.style_switcher.set_active_id(active_id)
        else:
            self.view.style_switcher.set_active_id('default')
        if set_active_id_dark_mode:
            self.view.style_switcher_dark_mode.set_active_id(active_id_dark_mode)
        else:
            self.view.style_switcher_dark_mode.set_active_id('default-dark')
        self.update_remove_button()

    def update_font_color_preview(self):
        source_style_scheme_manager = ServiceLocator.get_source_style_scheme_manager()
        name = self.settings.get_value('preferences', 'syntax_scheme')
        source_style_scheme_light = source_style_scheme_manager.get_scheme(name)
        name = self.settings.get_value('preferences', 'syntax_scheme_dark_mode')
        source_style_scheme_dark = source_style_scheme_manager.get_scheme(name)
        if self.view.style_switcher_stack.get_visible_child_name() == 'light':
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


class PageFontColorView(Gtk.ScrolledWindow):

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.set_size_request(-1, 500)

        self.box = Gtk.VBox()
        self.add(self.box)

        self.box.set_margin_start(18)
        self.box.set_margin_end(18)
        self.box.set_margin_top(18)
        self.box.set_margin_bottom(18)
        self.box.get_style_context().add_class('preferences-page')

        label = Gtk.Label()
        label.set_markup('<b>' + _('Font') + '</b>')
        label.set_xalign(0)
        label.set_margin_bottom(6)
        self.box.pack_start(label, False, False, 0)

        font_manager = ServiceLocator.get_font_manager()
        font_string = font_manager.get_system_font()
        self.option_use_system_font = Gtk.CheckButton(_('Use the system fixed width font (' + font_string + ')'))
        self.option_use_system_font.set_margin_bottom(18)
        self.box.pack_start(self.option_use_system_font, False, False, 0)

        self.font_chooser_revealer = Gtk.Revealer()
        vbox = Gtk.VBox()
        label = Gtk.Label()
        label.set_markup(_('Set Editor Font:'))
        label.set_xalign(0)
        label.set_margin_bottom(6)
        vbox.pack_start(label, False, False, 0)

        self.font_chooser_button = Gtk.FontButton()
        self.font_chooser_button.set_margin_bottom(18)
        hbox = Gtk.HBox()
        hbox.pack_start(self.font_chooser_button, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)
        self.font_chooser_revealer.add(vbox)
        self.box.pack_start(self.font_chooser_revealer, False, False, 0)

        label = Gtk.Label()
        label.set_markup('<b>' + _('UI Colors') + '</b>')
        label.set_xalign(0)
        label.set_margin_bottom(6)
        self.box.pack_start(label, False, False, 0)

        vbox = Gtk.HBox()
        self.option_default_theme = Gtk.RadioButton(_('Default'))
        self.option_default_theme.set_margin_right(12)
        self.option_force_light = Gtk.RadioButton.new_with_label_from_widget(self.option_default_theme, _('Light Theme'))
        self.option_force_light.set_margin_right(12)
        self.option_force_dark = Gtk.RadioButton.new_with_label_from_widget(self.option_default_theme, _('Dark Theme'))
        vbox.pack_start(self.option_default_theme, False, False, 0)
        vbox.pack_start(self.option_force_light, False, False, 0)
        vbox.pack_start(self.option_force_dark, False, False, 0)
        self.box.pack_start(vbox, False, False, 0)

        self.option_invert_preview = Gtk.CheckButton(_('Invert Colors in .pdf-Preview'))
        self.option_invert_preview.set_margin_top(3)
        self.box.pack_start(self.option_invert_preview, False, False, 0)

        label = Gtk.Label()
        label.set_markup('<b>' + _('Editor Colors') + '</b>')
        label.set_xalign(0)
        label.set_margin_top(18)
        label.set_margin_bottom(6)
        self.box.pack_start(label, False, False, 0)

        self.style_switcher = Gtk.ComboBoxText()
        self.style_switcher_dark_mode = Gtk.ComboBoxText()

        self.style_switcher_stack = Gtk.Stack()
        self.style_switcher_stack.add_named(self.style_switcher, 'light')
        self.style_switcher_stack.add_named(self.style_switcher_dark_mode, 'dark')
        box = Gtk.HBox()
        box.set_margin_bottom(18)
        box.pack_start(self.style_switcher_stack, False, False, 0)
        self.box.pack_start(box, False, False, 0)

        box = Gtk.HBox()
        box.set_margin_bottom(18)
        self.remove_scheme_button = Gtk.Button()
        self.remove_scheme_button.set_label(_('Remove active scheme'))
        box.pack_end(self.remove_scheme_button, False, False, 0)
        self.add_scheme_button = Gtk.Button()
        self.add_scheme_button.set_label(_('Add from file...'))
        box.pack_start(self.add_scheme_button, False, False, 0)
        self.box.pack_start(box, False, False, 0)

        label = Gtk.Label()
        label.set_markup('<b>' + _('Preview') + '</b>')
        label.set_xalign(0)
        label.set_margin_bottom(6)
        self.box.pack_start(label, False, False, 0)

        self.preview_wrapper = Gtk.VBox()
        self.preview_wrapper.get_style_context().add_class('preview')
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_min_content_height(162)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        self.source_view = GtkSource.View()
        self.source_view.set_editable(False)
        self.source_view.set_cursor_visible(False)
        self.source_view.set_monospace(True)
        self.source_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.source_view.set_show_line_numbers(False)
        self.source_view.set_highlight_current_line(False)
        scrolled_window.add(self.source_view)
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
        self.preview_wrapper.pack_start(scrolled_window, True, True, 0)
        self.box.pack_start(self.preview_wrapper, True, True, 0)


class AddSchemeDialog(object):
    ''' File chooser for adding syntax schemes '''

    def __init__(self, main_window):
        self.main_window = main_window

    def run(self):
        self.setup()
        response = self.view.run()
        if response == Gtk.ResponseType.OK:
            return_value = self.view.get_filename()
        else:
            return_value = None
        self.view.hide()
        del(self.view)
        return return_value

    def setup(self):
        self.action = Gtk.FileChooserAction.OPEN
        self.buttons = (_('_Cancel'), Gtk.ResponseType.CANCEL, _('_Add Scheme'), Gtk.ResponseType.OK)
        self.view = Gtk.FileChooserDialog(_('Add Scheme'), self.main_window, self.action, self.buttons)

        headerbar = self.view.get_header_bar()
        if headerbar != None:
            for widget in headerbar.get_children():
                if isinstance(widget, Gtk.Button) and widget.get_label() == _('_Add Scheme'):
                    widget.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
                    widget.set_can_default(True)
                    widget.grab_default()

        file_filter1 = Gtk.FileFilter()
        file_filter1.add_pattern('*.xml')
        file_filter1.set_name(_('Color Scheme Files'))
        self.view.add_filter(file_filter1)

        self.view.set_select_multiple(False)

        self.main_window.headerbar.document_chooser.popdown()


class ReplaceConfirmationDialog(object):
    ''' This dialog shows a warning when users want to delete a syntax scheme. '''

    def __init__(self, main_window):
        self.main_window = main_window

    def run(self, name):
        self.setup(name)
        response = self.view.run()
        if response == Gtk.ResponseType.YES:
            return_value = True
        else:
            return_value = False
        self.view.hide()
        del(self.view)
        return return_value

    def setup(self, name):
        self.view = Gtk.MessageDialog(self.main_window, 0, Gtk.MessageType.QUESTION)

        question = _('Removing syntax scheme »{name}«.')
        self.view.set_property('text', question.format(name=name))
        self.view.format_secondary_markup(_('Do you really want to do this?'))

        self.view.add_buttons(_('_Cancel'), Gtk.ResponseType.CANCEL, _('_Yes, remove it'), Gtk.ResponseType.YES)
        self.view.set_default_response(Gtk.ResponseType.YES)



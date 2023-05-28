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
gi.require_version('Xdp', '1.0')
from gi.repository import Gtk, Xdp

import os
import subprocess


class PageBuildSystem(object):

    def __init__(self, preferences, settings):
        self.view = PageBuildSystemView()
        self.preferences = preferences
        self.settings = settings
        self.latex_interpreters = list()
        self.latexmk_available = False

    def init(self):
        self.view.option_cleanup_build_files.set_active(self.settings.get_value('preferences', 'cleanup_build_files'))
        self.view.option_cleanup_build_files.connect('toggled', self.preferences.on_check_button_toggle, 'cleanup_build_files')

        self.view.option_autoshow_build_log_errors.set_active(self.settings.get_value('preferences', 'autoshow_build_log') == 'errors')
        self.view.option_autoshow_build_log_errors_warnings.set_active(self.settings.get_value('preferences', 'autoshow_build_log') == 'errors_warnings')
        self.view.option_autoshow_build_log_all.set_active(self.settings.get_value('preferences', 'autoshow_build_log') == 'all')

        self.view.option_autoshow_build_log_errors.connect('toggled', self.preferences.on_radio_button_toggle, 'autoshow_build_log', 'errors')
        self.view.option_autoshow_build_log_errors_warnings.connect('toggled', self.preferences.on_radio_button_toggle, 'autoshow_build_log', 'errors_warnings')
        self.view.option_autoshow_build_log_all.connect('toggled', self.preferences.on_radio_button_toggle, 'autoshow_build_log', 'all')

        self.view.option_system_commands_disable.set_active(self.settings.get_value('preferences', 'build_option_system_commands') == 'disable')
        self.view.option_system_commands_restricted.set_active(self.settings.get_value('preferences', 'build_option_system_commands') == 'restricted')
        self.view.option_system_commands_full.set_active(self.settings.get_value('preferences', 'build_option_system_commands') == 'enable')

        self.view.option_system_commands_disable.connect('toggled', self.preferences.on_radio_button_toggle, 'build_option_system_commands', 'disable')
        self.view.option_system_commands_restricted.connect('toggled', self.preferences.on_radio_button_toggle, 'build_option_system_commands', 'restricted')
        self.view.option_system_commands_full.connect('toggled', self.preferences.on_radio_button_toggle, 'build_option_system_commands', 'enable')

        self.setup_latex_interpreters()

    def setup_latex_interpreters(self):
        self.latex_interpreters = list()
        for interpreter in ['xelatex', 'pdflatex', 'lualatex', 'tectonic']:
            self.view.option_latex_interpreter[interpreter].hide()
            arguments = [interpreter, '--version']
            try:
                process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except FileNotFoundError:
                pass
            else:
                process.wait()
                if process.returncode == 0:
                    self.latex_interpreters.append(interpreter)

        self.latexmk_available = False
        arguments = ['latexmk', '--version']
        try:
            process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError:
            pass
        else:
            process.wait()
            if process.returncode == 0:
                self.latexmk_available = True

        if len(self.latex_interpreters) == 0:
            self.view.no_interpreter_label.show_all()
        else:
            self.view.no_interpreter_label.hide()
            if self.settings.get_value('preferences', 'latex_interpreter') not in self.latex_interpreters:
                self.settings.set_value('preferences', 'latex_interpreter', self.latex_interpreters[0])

            if self.latexmk_available:
                self.view.option_use_latexmk.show_all()
            else:
                self.view.option_use_latexmk.hide()
                self.settings.set_value('preferences', 'use_latexmk', False)
            self.view.option_use_latexmk.set_active(self.settings.get_value('preferences', 'use_latexmk'))
            self.view.option_use_latexmk.connect('toggled', self.preferences.on_check_button_toggle, 'use_latexmk')

            for interpreter in self.latex_interpreters:
                self.view.option_latex_interpreter[interpreter].show_all()
                self.view.option_latex_interpreter[interpreter].set_active(interpreter == self.settings.get_value('preferences', 'latex_interpreter'))
            for interpreter in self.latex_interpreters:
                self.view.option_latex_interpreter[interpreter].connect('toggled', self.preferences.on_interpreter_changed, 'latex_interpreter', interpreter)
            
            self.view.option_latex_interpreter['tectonic'].connect('toggled', self.on_use_tectonic_toggled)
            self.view.latexmk_enable_revealer.set_reveal_child(not self.view.option_latex_interpreter['tectonic'].get_active())
            self.view.shell_escape_revealer.set_reveal_child(not self.view.option_latex_interpreter['tectonic'].get_active())
            self.view.tectonic_warning_revealer.set_reveal_child(self.view.option_latex_interpreter['tectonic'].get_active())

    def on_use_tectonic_toggled(self, button):
        self.view.latexmk_enable_revealer.set_reveal_child(not button.get_active())
        self.view.shell_escape_revealer.set_reveal_child(not button.get_active())
        self.view.tectonic_warning_revealer.set_reveal_child(button.get_active())

class PageBuildSystemView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self, orientation = Gtk.Orientation.VERTICAL)

        self.set_margin_start(18)
        self.set_margin_end(18)
        self.set_margin_top(18)
        self.set_margin_bottom(18)
        self.get_style_context().add_class('preferences-page')

        label = Gtk.Label()
        label.set_markup('<b>' + _('LaTeX Interpreter') + '</b>')
        label.set_xalign(0)
        label.set_margin_bottom(6)
        self.pack_start(label, False, False, 0)

        self.no_interpreter_label = Gtk.Label()
        self.no_interpreter_label.set_line_wrap(True)
        if Xdp.Portal().running_under_flatpak():
            self.no_interpreter_label.set_markup(_('''No LaTeX interpreter found. To install interpreters in Flatpak, open a terminal and run the following command:

    flatpak install org.freedesktop.Sdk.Extension.texlive'''))
        else:
            self.no_interpreter_label.set_markup(_('No LaTeX interpreter found. For instructions on installing LaTeX see <a href="https://en.wikibooks.org/wiki/LaTeX/Installation">https://en.wikibooks.org/wiki/LaTeX/Installation</a>'))
        self.no_interpreter_label.set_xalign(0)
        self.no_interpreter_label.set_margin_bottom(6)
        self.pack_start(self.no_interpreter_label, False, False, 0)

        self.option_latex_interpreter = dict()
        self.option_latex_interpreter['xelatex'] = Gtk.RadioButton('XeLaTeX')
        self.option_latex_interpreter['xelatex'].set_margin_right(12)
        self.option_latex_interpreter['pdflatex'] = Gtk.RadioButton.new_with_label_from_widget(self.option_latex_interpreter['xelatex'], 'PdfLaTeX')
        self.option_latex_interpreter['pdflatex'].set_margin_right(12)
        self.option_latex_interpreter['lualatex'] = Gtk.RadioButton.new_with_label_from_widget(self.option_latex_interpreter['xelatex'], 'LuaLaTeX')
        self.option_latex_interpreter['lualatex'].set_margin_right(12)
        self.option_latex_interpreter['tectonic'] = Gtk.RadioButton.new_with_label_from_widget(self.option_latex_interpreter['xelatex'], 'Tectonic')
        self.option_latex_interpreter['tectonic'].set_margin_right(12)

        self.hbox1 = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.hbox1.pack_start(self.option_latex_interpreter['xelatex'], False, False, 0)
        self.hbox1.pack_start(self.option_latex_interpreter['pdflatex'], False, False, 0)
        self.hbox1.pack_start(self.option_latex_interpreter['lualatex'], False, False, 0)
        self.hbox1.pack_start(self.option_latex_interpreter['tectonic'], False, False, 0)
        self.pack_start(self.hbox1, False, False, 0)

        self.tectonic_warning_revealer = Gtk.Revealer()
        self.tectonic_warning_revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)
        label = Gtk.Label()
        label.set_line_wrap(True)
        label.set_markup(_('Please note: the Tectonic backend uses only the V1 command-line interface. Tectonic.toml configuration files are ignored.'))
        label.set_xalign(0)
        label.set_margin_top(6)
        label.get_style_context().add_class('description')
        self.tectonic_warning_revealer.add(label)
        self.pack_start(self.tectonic_warning_revealer, False, False, 0)


        label = Gtk.Label()
        label.set_markup('<b>' + _('Options') + '</b>')
        label.set_xalign(0)
        label.set_margin_top(18)
        label.set_margin_bottom(6)
        self.pack_start(label, False, False, 0)
        self.option_cleanup_build_files = Gtk.CheckButton(_('Automatically remove helper files (.log, .dvi, ...) after building .pdf.'))
        self.pack_start(self.option_cleanup_build_files, False, False, 0)

        self.latexmk_enable_revealer = Gtk.Revealer()
        self.latexmk_enable_revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)
        self.option_use_latexmk = Gtk.CheckButton(_('Use Latexmk'))
        self.latexmk_enable_revealer.add(self.option_use_latexmk)
        self.pack_start(self.latexmk_enable_revealer, False, False, 0)

        label = Gtk.Label()
        label.set_markup('<b>' + _('Automatically show build log ..') + ' </b>')
        label.set_xalign(0)
        label.set_margin_top(18)
        label.set_margin_bottom(6)
        self.pack_start(label, False, False, 0)
        self.option_autoshow_build_log_errors = Gtk.RadioButton(_('.. only when errors occurred.'))
        self.option_autoshow_build_log_errors_warnings = Gtk.RadioButton.new_with_label_from_widget(self.option_autoshow_build_log_errors, _('.. on errors and warnings.'))
        self.option_autoshow_build_log_all = Gtk.RadioButton.new_with_label_from_widget(self.option_autoshow_build_log_errors, _('.. on errors, warnings and badboxes.'))
        self.pack_start(self.option_autoshow_build_log_errors, False, False, 0)
        self.pack_start(self.option_autoshow_build_log_errors_warnings, False, False, 0)
        self.pack_start(self.option_autoshow_build_log_all, False, False, 0)
    
        self.shell_escape_revealer = Gtk.Revealer()
        self.shell_escape_revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)
        self.vbox1 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        label = Gtk.Label()
        label.set_markup('<b>' + _('Embedded system commands') + '</b>')
        label.set_xalign(0)
        label.set_margin_top(18)
        label.set_margin_bottom(6)
        self.vbox1.pack_start(label, False, False, 0)
        label = Gtk.Label()
        label.set_line_wrap(True)
        label.set_markup(_('Warning: enable this only if you have to. It can cause security problems when building files from untrusted sources.'))
        label.set_xalign(0)
        label.set_margin_bottom(9)
        label.get_style_context().add_class('description')
        self.vbox1.pack_start(label, False, False, 0)
        self.option_system_commands_disable = Gtk.RadioButton(_('Disable') + ' (' + _('recommended') + ')')
        self.option_system_commands_restricted = Gtk.RadioButton.new_with_label_from_widget(self.option_system_commands_disable, _('Enable restricted \\write18{SHELL COMMAND}'))
        self.option_system_commands_full = Gtk.RadioButton.new_with_label_from_widget(self.option_system_commands_disable, _('Fully enable \\write18{SHELL COMMAND}'))
        self.vbox1.pack_start(self.option_system_commands_disable, False, False, 0)
        self.vbox1.pack_start(self.option_system_commands_restricted, False, False, 0)
        self.vbox1.pack_start(self.option_system_commands_full, False, False, 0)

        self.shell_escape_revealer.add(self.vbox1)
        self.pack_start(self.shell_escape_revealer, False, False, 0)

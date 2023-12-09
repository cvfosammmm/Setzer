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
gi.require_version('Xdp', '1.0')
from gi.repository import Gtk, Xdp

import subprocess, os


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
            self.view.option_latex_interpreter[interpreter].set_visible(False)
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
            self.view.no_interpreter_label.set_visible(True)
        else:
            self.view.no_interpreter_label.set_visible(False)
            if self.settings.get_value('preferences', 'latex_interpreter') not in self.latex_interpreters:
                self.settings.set_value('preferences', 'latex_interpreter', self.latex_interpreters[0])

            if self.latexmk_available:
                self.view.option_use_latexmk.set_visible(True)
            else:
                self.view.option_use_latexmk.set_visible(False)
                self.settings.set_value('preferences', 'use_latexmk', False)
            self.view.option_use_latexmk.set_active(self.settings.get_value('preferences', 'use_latexmk'))
            self.view.option_use_latexmk.connect('toggled', self.preferences.on_check_button_toggle, 'use_latexmk')

            for interpreter in self.view.option_latex_interpreter:
                if interpreter in self.latex_interpreters:
                    self.view.option_latex_interpreter[interpreter].set_visible(True)
                    self.view.option_latex_interpreter[interpreter].set_active(interpreter == self.settings.get_value('preferences', 'latex_interpreter'))
                    self.view.option_latex_interpreter[interpreter].connect('toggled', self.preferences.on_interpreter_changed, 'latex_interpreter', interpreter)
                else:
                    self.view.option_latex_interpreter[interpreter].set_visible(False)

            self.view.option_latex_interpreter['tectonic'].connect('toggled', self.on_use_tectonic_toggled)
        self.update_tectonic_element_visibility()

    def on_use_tectonic_toggled(self, button):
        self.update_tectonic_element_visibility()

    def update_tectonic_element_visibility(self):
        if 'tectonic' in self.latex_interpreters and self.view.option_latex_interpreter['tectonic'].get_active():
            self.view.tectonic_warning_label.set_visible(True)
            self.view.option_use_latexmk.set_visible(False)
            self.view.shell_escape_box.set_visible(False)
        else:
            self.view.tectonic_warning_label.set_visible(False)
            self.view.option_use_latexmk.set_visible(True)
            self.view.shell_escape_box.set_visible(True)

class PageBuildSystemView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.set_margin_start(18)
        self.set_margin_end(18)
        self.set_margin_top(18)
        self.set_margin_bottom(18)
        self.get_style_context().add_class('preferences-page')

        label = Gtk.Label()
        label.set_markup('<b>' + _('LaTeX Interpreter') + '</b>')
        label.set_xalign(0)
        label.set_margin_bottom(6)
        self.append(label)

        self.no_interpreter_label = Gtk.Label()
        self.no_interpreter_label.set_wrap(True)
        if Xdp.Portal().running_under_flatpak():
            self.no_interpreter_label.set_markup(_('''No LaTeX interpreter found. To install interpreters in Flatpak, open a terminal and run the following command:
flatpak install org.freedesktop.Sdk.Extension.texlive'''))
        else:
            self.no_interpreter_label.set_markup(_('No LaTeX interpreter found. For instructions on installing LaTeX see <a href="https://en.wikibooks.org/wiki/LaTeX/Installation">https://en.wikibooks.org/wiki/LaTeX/Installation</a>'))
        self.no_interpreter_label.set_xalign(0)
        self.no_interpreter_label.set_margin_bottom(6)
        self.append(self.no_interpreter_label)

        self.option_latex_interpreter = dict()
        self.option_latex_interpreter['xelatex'] = Gtk.CheckButton.new_with_label('XeLaTeX')
        self.option_latex_interpreter['xelatex'].set_margin_end(12)
        self.option_latex_interpreter['pdflatex'] = Gtk.CheckButton.new_with_label('PdfLaTeX')
        self.option_latex_interpreter['pdflatex'].set_margin_end(12)
        self.option_latex_interpreter['pdflatex'].set_group(self.option_latex_interpreter['xelatex'])
        self.option_latex_interpreter['lualatex'] = Gtk.CheckButton.new_with_label('LuaLaTeX')
        self.option_latex_interpreter['lualatex'].set_margin_end(12)
        self.option_latex_interpreter['lualatex'].set_group(self.option_latex_interpreter['xelatex'])
        self.option_latex_interpreter['tectonic'] = Gtk.CheckButton.new_with_label('Tectonic')
        self.option_latex_interpreter['tectonic'].set_margin_end(12)
        self.option_latex_interpreter['tectonic'].set_group(self.option_latex_interpreter['xelatex'])

        self.hbox1 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox1.append(self.option_latex_interpreter['xelatex'])
        self.hbox1.append(self.option_latex_interpreter['pdflatex'])
        self.hbox1.append(self.option_latex_interpreter['lualatex'])
        self.hbox1.append(self.option_latex_interpreter['tectonic'])
        self.append(self.hbox1)

        self.tectonic_warning_label = Gtk.Label()
        self.tectonic_warning_label.set_wrap(True)
        self.tectonic_warning_label.set_markup(_('Please note: the Tectonic backend uses only the V1 command-line interface. Tectonic.toml configuration files are ignored.'))
        self.tectonic_warning_label.set_xalign(0)
        self.tectonic_warning_label.set_margin_top(6)
        self.tectonic_warning_label.get_style_context().add_class('description')

        self.append(self.tectonic_warning_label)

        label = Gtk.Label()
        label.set_markup('<b>' + _('Options') + '</b>')
        label.set_xalign(0)
        label.set_margin_top(18)
        label.set_margin_bottom(6)
        self.append(label)
        self.option_cleanup_build_files = Gtk.CheckButton.new_with_label(_('Automatically remove helper files (.log, .dvi, …) after building .pdf.'))
        self.append(self.option_cleanup_build_files)

        self.option_use_latexmk = Gtk.CheckButton.new_with_label(_('Use Latexmk'))
        self.append(self.option_use_latexmk)

        label = Gtk.Label()
        label.set_markup('<b>' + _('Automatically show build log ..') + ' </b>')
        label.set_xalign(0)
        label.set_margin_top(18)
        label.set_margin_bottom(6)
        self.append(label)
        self.option_autoshow_build_log_errors = Gtk.CheckButton.new_with_label(_('.. only when errors occurred.'))
        self.option_autoshow_build_log_errors_warnings = Gtk.CheckButton.new_with_label(_('.. on errors and warnings.'))
        self.option_autoshow_build_log_errors_warnings.set_group(self.option_autoshow_build_log_errors)
        self.option_autoshow_build_log_all = Gtk.CheckButton.new_with_label(_('.. on errors, warnings and badboxes.'))
        self.option_autoshow_build_log_all.set_group(self.option_autoshow_build_log_errors)
        self.append(self.option_autoshow_build_log_errors)
        self.append(self.option_autoshow_build_log_errors_warnings)
        self.append(self.option_autoshow_build_log_all)

        label_header = Gtk.Label()
        label_header.set_markup('<b>' + _('Embedded system commands') + '</b>')
        label_header.set_xalign(0)
        label_header.set_margin_top(18)
        label_header.set_margin_bottom(6)

        label_explainer = Gtk.Label()
        label_explainer.set_wrap(True)
        label_explainer.set_markup(_('Warning: enable this only if you have to. It can cause security problems when building files from untrusted sources.'))
        label_explainer.set_xalign(0)
        label_explainer.set_margin_bottom(9)
        label_explainer.get_style_context().add_class('description')
        self.option_system_commands_disable = Gtk.CheckButton.new_with_label(_('Disable') + ' (' + _('recommended') + ')')
        self.option_system_commands_restricted = Gtk.CheckButton.new_with_label(_('Enable restricted \\write18{SHELL COMMAND}'))
        self.option_system_commands_restricted.set_group(self.option_system_commands_disable)
        self.option_system_commands_full = Gtk.CheckButton.new_with_label(_('Fully enable \\write18{SHELL COMMAND}'))
        self.option_system_commands_full.set_group(self.option_system_commands_disable)

        self.shell_escape_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.shell_escape_box.append(label_header)
        self.shell_escape_box.append(label_explainer)
        self.shell_escape_box.append(self.option_system_commands_disable)
        self.shell_escape_box.append(self.option_system_commands_restricted)
        self.shell_escape_box.append(self.option_system_commands_full)

        self.append(self.shell_escape_box)



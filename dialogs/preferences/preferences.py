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


from dialogs.dialog import Dialog
import dialogs.preferences.preferences_viewgtk as view


class PreferencesDialog(Dialog):

    def __init__(self, main_window, settings):
        self.main_window = main_window
        self.settings = settings

    def run(self):
        self.setup()
        self.view.run()
        del(self.view)

    def setup(self):
        self.view = view.Preferences(self.main_window)

        self.view.option_cleanup_build_files.set_active(self.settings.get_value('preferences', 'cleanup_build_files'))
        self.view.option_cleanup_build_files.connect('toggled', self.on_check_button_toggle, 'cleanup_build_files')

        self.view.option_autoshow_build_log_errors.set_active(self.settings.get_value('preferences', 'autoshow_build_log') == 'errors')
        self.view.option_autoshow_build_log_errors_warnings.set_active(self.settings.get_value('preferences', 'autoshow_build_log') == 'errors_warnings')
        self.view.option_autoshow_build_log_all.set_active(self.settings.get_value('preferences', 'autoshow_build_log') == 'all')

        self.view.option_autoshow_build_log_errors.connect('toggled', self.on_radio_button_toggle, 'autoshow_build_log', 'errors')
        self.view.option_autoshow_build_log_errors_warnings.connect('toggled', self.on_radio_button_toggle, 'autoshow_build_log', 'errors_warnings')
        self.view.option_autoshow_build_log_all.connect('toggled', self.on_radio_button_toggle, 'autoshow_build_log', 'all')

        self.view.option_latex_interpreter_latexmk.set_active(self.settings.get_value('preferences', 'latex_interpreter') == 'latexmk')
        self.view.option_latex_interpreter_pdflatex.set_active(self.settings.get_value('preferences', 'latex_interpreter') == 'pdflatex')
        self.view.option_latex_interpreter_xelatex.set_active(self.settings.get_value('preferences', 'latex_interpreter') == 'xelatex')
        self.view.option_latex_interpreter_lualatex.set_active(self.settings.get_value('preferences', 'latex_interpreter') == 'lualatex')
        self.view.option_latex_interpreter_latexmk.connect('toggled', self.on_interpreter_changed, 'latex_interpreter', 'latexmk')
        self.view.option_latex_interpreter_pdflatex.connect('toggled', self.on_interpreter_changed, 'latex_interpreter', 'pdflatex')
        self.view.option_latex_interpreter_xelatex.connect('toggled', self.on_interpreter_changed, 'latex_interpreter', 'xelatex')
        self.view.option_latex_interpreter_lualatex.connect('toggled', self.on_interpreter_changed, 'latex_interpreter', 'lualatex')

    def on_check_button_toggle(self, button, preference_name):
        self.settings.set_value('preferences', preference_name, button.get_active())
        
    def on_radio_button_toggle(self, button, preference_name, value):
        self.settings.set_value('preferences', preference_name, value)

    def text_deleted(self, buffer, position, n_chars, preference_name):
        self.settings.set_value('preferences', preference_name, buffer.get_text())

    def text_inserted(self, buffer, position, chars, n_chars, preference_name):
        self.settings.set_value('preferences', preference_name, buffer.get_text())

    def on_interpreter_changed(self, button, preference_name, value):
        self.settings.set_value('preferences', preference_name, value)



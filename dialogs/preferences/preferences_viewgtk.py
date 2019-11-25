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
from gi.repository import Gtk
from gi.repository import Gdk


class Preferences(object):
    ''' Preferences dialog. '''

    def __init__(self, main_window):
        builder = Gtk.Builder.new_from_string('<?xml version="1.0" encoding="UTF-8"?><interface><object class="GtkDialog" id="dialog"><property name="use-header-bar">1</property></object></interface>', -1)

        self.dialog = builder.get_object('dialog')
        self.dialog.set_destroy_with_parent(True)
        self.dialog.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.dialog.set_modal(True)
        self.dialog.set_transient_for(main_window)
        self.dialog.set_can_focus(False)
        self.dialog.set_size_request(400, 250)
        self.dialog.set_default_size(400, 250)
        
        self.headerbar = self.dialog.get_header_bar()
        self.headerbar.set_title('Preferences')

        self.topbox = self.dialog.get_content_area()
        self.topbox.set_border_width(0)

        self.notebook = Gtk.Notebook()
        self.notebook.set_show_tabs(True)
        self.notebook.set_show_border(False)
        self.topbox.pack_start(self.notebook, True, True, 0)

        self.build_page_build_system()
        self.build_page_editor()

        self.notebook.append_page(self.page_build_system, Gtk.Label('Build System'))
        self.notebook.append_page(self.page_editor, Gtk.Label('Editor'))
        
        self.dialog.show_all()

    def build_page_editor(self):
        self.page_editor = Gtk.VBox()
        self.page_editor.set_margin_start(18)
        self.page_editor.set_margin_end(18)
        self.page_editor.set_margin_top(18)
        self.page_editor.set_margin_bottom(18)
        self.page_editor.get_style_context().add_class('preferences-page')

        label = Gtk.Label()
        label.set_markup('<b>Tab Stops</b>')
        label.set_xalign(0)
        label.set_margin_bottom(6)
        self.page_editor.pack_start(label, False, False, 0)

        self.option_spaces_instead_of_tabs = Gtk.CheckButton('Insert spaces instead of tabs')
        self.page_editor.pack_start(self.option_spaces_instead_of_tabs, False, False, 0)

        label = Gtk.Label()
        label.set_markup('Set Tab Width:')
        label.set_xalign(0)
        label.set_margin_top(18)
        label.set_margin_bottom(6)
        self.page_editor.pack_start(label, False, False, 0)
        box = Gtk.HBox()
        self.tab_width_spinbutton = Gtk.SpinButton.new_with_range(1, 8, 1)
        box.pack_start(self.tab_width_spinbutton, False, False, 0)
        self.page_editor.pack_start(box, False, False, 0)

        label = Gtk.Label()
        label.set_markup('<b>Line Numbers</b>')
        label.set_xalign(0)
        label.set_margin_top(18)
        label.set_margin_bottom(6)
        self.page_editor.pack_start(label, False, False, 0)
        self.option_show_line_numbers = Gtk.CheckButton('Show line numbers')
        self.page_editor.pack_start(self.option_show_line_numbers, False, False, 0)

        label = Gtk.Label()
        label.set_markup('<b>Line Wrapping</b>')
        label.set_xalign(0)
        label.set_margin_top(18)
        label.set_margin_bottom(6)
        self.page_editor.pack_start(label, False, False, 0)
        self.option_line_wrapping = Gtk.CheckButton('Enable line wrapping')
        self.page_editor.pack_start(self.option_line_wrapping, False, False, 0)

    def build_page_build_system(self):
        self.page_build_system = Gtk.VBox()
        self.page_build_system.set_margin_start(18)
        self.page_build_system.set_margin_end(18)
        self.page_build_system.set_margin_top(18)
        self.page_build_system.set_margin_bottom(18)
        self.page_build_system.get_style_context().add_class('preferences-page')

        label = Gtk.Label()
        label.set_markup('<b>LaTeX Interpreter</b>')
        label.set_xalign(0)
        label.set_margin_bottom(6)
        self.page_build_system.pack_start(label, False, False, 0)
        self.option_latex_interpreter_latexmk = Gtk.RadioButton('Latexmk')
        self.option_latex_interpreter_pdflatex = Gtk.RadioButton.new_with_label_from_widget(self.option_latex_interpreter_latexmk, 'PdfLaTeX')
        self.option_latex_interpreter_xelatex = Gtk.RadioButton.new_with_label_from_widget(self.option_latex_interpreter_latexmk, 'XeLaTeX')
        self.option_latex_interpreter_lualatex = Gtk.RadioButton.new_with_label_from_widget(self.option_latex_interpreter_latexmk, 'LuaLaTeX')

        hbox1 = Gtk.HBox()
        hbox1.pack_start(self.option_latex_interpreter_latexmk, True, True, 0)
        hbox1.pack_start(self.option_latex_interpreter_pdflatex, True, True, 0)
        hbox1.pack_start(self.option_latex_interpreter_xelatex, True, True, 0)
        hbox1.pack_start(self.option_latex_interpreter_lualatex, True, True, 0)
        self.page_build_system.pack_start(hbox1, False, False, 0)

        label = Gtk.Label()
        label.set_markup('<b>Options</b>')
        label.set_xalign(0)
        label.set_margin_top(18)
        label.set_margin_bottom(6)
        self.page_build_system.pack_start(label, False, False, 0)
        self.option_cleanup_build_files = Gtk.CheckButton('Automatically remove helper files (.log, .dvi, ...) after building .pdf.')
        self.page_build_system.pack_start(self.option_cleanup_build_files, False, False, 0)

        label = Gtk.Label()
        label.set_markup('<b>Automatically show build log ..</b>')
        label.set_xalign(0)
        label.set_margin_top(18)
        label.set_margin_bottom(6)
        self.page_build_system.pack_start(label, False, False, 0)
        self.option_autoshow_build_log_errors = Gtk.RadioButton('.. only when errors occurred.')
        self.option_autoshow_build_log_errors_warnings = Gtk.RadioButton.new_with_label_from_widget(self.option_autoshow_build_log_errors, '.. on errors and warnings.')
        self.option_autoshow_build_log_all = Gtk.RadioButton.new_with_label_from_widget(self.option_autoshow_build_log_errors, '.. on errors, warnings and badboxes.')
        self.page_build_system.pack_start(self.option_autoshow_build_log_errors, False, False, 0)
        self.page_build_system.pack_start(self.option_autoshow_build_log_errors_warnings, False, False, 0)
        self.page_build_system.pack_start(self.option_autoshow_build_log_all, False, False, 0)
    
    def run(self):
        return self.dialog.run()
        
    def response(self, args):
        self.dialog.response(args)
        
    def __del__(self):
        self.dialog.destroy()
        



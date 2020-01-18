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
from gi.repository import GLib
from gi.repository import Gio


class ShortcutsBar(Gtk.HBox):

    def __init__(self):
        Gtk.HBox.__init__(self)
        self.get_style_context().add_class('shortcutsbar')

        self.current_bottom = None

        self.create_top_toolbar()
        self.populate_top_toolbar()
        self.create_right_toolbar()
        self.populate_right_toolbar()
        self.pack_start(self.top_icons, True, True, 0)
        self.pack_end(self.right_icons, False, False, 0)

    def create_top_toolbar(self):
        self.top_icons = Gtk.Toolbar()
        self.top_icons.set_style(Gtk.ToolbarStyle.ICONS)
        self.top_icons.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.top_icons.set_icon_size(Gtk.IconSize.SMALL_TOOLBAR)
        
    def create_right_toolbar(self):
        self.right_icons = Gtk.Toolbar()
        self.right_icons.set_style(Gtk.ToolbarStyle.ICONS)
        self.right_icons.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.right_icons.set_icon_size(Gtk.IconSize.SMALL_TOOLBAR)
        
    def populate_right_toolbar(self):
        self.button_build_log = Gtk.ToggleToolButton()
        self.button_build_log.set_icon_name('utilities-system-monitor-symbolic')
        self.button_build_log.set_tooltip_text('Build log (F8)')
        self.right_icons.insert(self.button_build_log, 0)

    def populate_top_toolbar(self):
        self.italic_button = Gtk.ToolButton()
        self.italic_button.set_icon_name('format-text-italic-symbolic')
        self.italic_button.set_label('Italic Text')
        self.italic_button.set_action_name('win.insert-before-after')
        self.italic_button.set_action_target_value(GLib.Variant('as', ['\\textit{', '}']))
        self.italic_button.set_focus_on_click(False)
        self.italic_button.set_tooltip_text('Italic (Ctrl+I)')
        self.top_icons.insert(self.italic_button, 0)

        self.bold_button = Gtk.ToolButton()
        self.bold_button.set_icon_name('format-text-bold-symbolic')
        self.bold_button.set_label('Bold Text')
        self.bold_button.set_action_name('win.insert-before-after')
        self.bold_button.set_action_target_value(GLib.Variant('as', ['\\textbf{', '}']))
        self.bold_button.set_focus_on_click(False)
        self.bold_button.set_tooltip_text('Bold (Ctrl+B)')
        self.top_icons.insert(self.bold_button, 0)

        self.insert_quotes_button()
        self.insert_math_button()
        self.insert_text_button()
        self.insert_object_button()
        self.insert_bibliography_button()

    def insert_bibliography_button(self):
        popover = Gtk.PopoverMenu()
        stack = popover.get_child()

        box = Gtk.VBox()
        self.set_box_margin(box)
        self.add_action_button(box, 'Include BibTeX File...', 'win.include-bibtex-file')
        self.add_action_button(box, 'Include \'natbib\' Package', 'win.add-packages', ['natbib'])
        self.add_separator(box)
        for citation_style in [('Citation', '\\cite{•}'), ('Citation with Page Number', '\\cite[•]{•}')]:
            self.add_action_button(box, citation_style[0], 'win.insert-symbol', [citation_style[1]])
        self.add_menu_button(box, 'Natbib Citations', 'natbib_citations')
        self.add_action_button(box, 'Include non-cited BibTeX Entries with \'\\nocite\'', 'win.insert-before-document-end', ['\\nocite{*}'])
        stack.add_named(box, 'main')
        box.show_all()

        # natbib submenu
        box = Gtk.VBox()
        self.set_box_margin(box)
        self.add_header_button(box, 'Natbib Citations')
        for citation_style in [('Abbreviated', '\\citet{•}'), ('Abbreviated with Brackets', '\\citep{•}'), ('Detailed', '\\citet*{•}'), ('Detailed with Brackets', '\\citep*{•}'), ('Alternative 1', '\\citealt{•}'), ('Alternative 2', '\\citealp{•}')]:
            self.add_action_button(box, citation_style[0], 'win.insert-symbol', [citation_style[1]])
        self.add_separator(box)
        for citation_style in [('Cite Author', '\\citeauthor{•}'), ('Cite Author Detailed', '\\citeauthor*{•}'), ('Cite Year', '\\citeyear{•}'), ('Cite Year with Brackets', '\\citeyearpar{•}')]:
            self.add_action_button(box, citation_style[0], 'win.insert-symbol', [citation_style[1]])
        stack.add_named(box, 'natbib_citations')
        box.show_all()

        self.bibliography_button = Gtk.MenuButton()
        self.bibliography_button.set_image(Gtk.Image.new_from_icon_name('view-dual-symbolic', Gtk.IconSize.MENU))
        self.bibliography_button.set_focus_on_click(False)
        self.bibliography_button.set_tooltip_text('Bibliography')
        self.bibliography_button.get_style_context().add_class('flat')
        self.bibliography_button.set_popover(popover)

        button_wrapper = Gtk.ToolItem()
        button_wrapper.add(self.bibliography_button)
        self.top_icons.insert(button_wrapper, 0)

    def insert_text_button(self):
        popover = Gtk.PopoverMenu()
        stack = popover.get_child()

        box = Gtk.VBox()
        self.set_box_margin(box)
        self.add_action_button(box, 'Footnote', 'win.insert-before-after', ['\\footnote{', '}'])
        self.add_separator(box)
        self.add_menu_button(box, 'Font Styles', 'font_styles')
        self.add_menu_button(box, 'Font Sizes', 'font_sizes')
        stack.add_named(box, 'main')
        box.show_all()

        # font styles submenu
        box = Gtk.VBox()
        self.set_box_margin(box)
        self.add_header_button(box, 'Font Styles')
        for font_style in [('Emphasis (\\emph)', 'emph'), ('Italics (\\textit)', 'textit'), ('Slanted (\\textsl)', 'textsl'), ('Bold (\\textbf)', 'textbf'), ('Typewriter (\\texttt)', 'texttt'), ('Small Caps (\\textsc)', 'textsc'), ('Sans Serif (\\textsf)', 'textsf'), ('Underline (\\underline)', 'underline')]:
            self.add_action_button(box, font_style[0], 'win.insert-before-after', ['\\' + font_style[1] + '{', '}'])
        stack.add_named(box, 'font_styles')
        box.show_all()

        # font sizes submenu
        box = Gtk.VBox()
        self.set_box_margin(box)
        self.add_header_button(box, 'Font Sizes')
        for font_size in ['tiny', 'scriptsize', 'footnotesize', 'small', 'normalsize', 'large', 'Large', 'LARGE', 'huge', 'Huge']:
            self.add_action_button(box, font_size, 'win.insert-before-after', ['{\\' + font_size + ' ', '}'])
        stack.add_named(box, 'font_sizes')
        box.show_all()

        self.text_button = Gtk.MenuButton()
        self.text_button.set_image(Gtk.Image.new_from_icon_name('text-symbolic', Gtk.IconSize.MENU))
        self.text_button.set_focus_on_click(False)
        self.text_button.set_tooltip_text('Text')
        self.text_button.get_style_context().add_class('flat')
        self.text_button.set_popover(popover)

        button_wrapper = Gtk.ToolItem()
        button_wrapper.add(self.text_button)
        self.top_icons.insert(button_wrapper, 0)

    def insert_quotes_button(self):
        popover = Gtk.PopoverMenu()
        stack = popover.get_child()

        box = Gtk.VBox()
        self.set_box_margin(box)
        for item in [('Primary Quotes (`` ... \'\')', ['``', '\'\'']), ('Secondary Quotes (` ... \')', ['`', '\'']), ('German Quotes (\\glqq ... \\grqq{})', ['\\glqq ', '\\grqq{}']), ('German Single Quotes (\\glq ... \\grq{})', ['\\glq ', '\\grq{}']), ('French Quotes (\\flqq ... \\frqq{})', ['\\flqq ', '\\frqq{}']), ('French Single Quotes (\\flq ... \\frq{})', ['\\flq ', '\\frq{}']), ('German Alt Quotes (\\frqq ... \\flqq{})', ['\\frqq ', '\\flqq{}']), ('German Alt Single Quotes (\\frq ... \\frq{})', ['\\frq ', '\\flq{}'])]:
            self.add_action_button(box, item[0], 'win.insert-before-after', item[1])
        stack.add_named(box, 'main')
        box.show_all()

        button_wrapper = Gtk.ToolItem()
        self.quotes_button = Gtk.MenuButton()
        self.quotes_button.set_direction(Gtk.ArrowType.DOWN)
        self.quotes_button.set_image(Gtk.Image.new_from_icon_name('own-quotes-symbolic', Gtk.IconSize.MENU))
        self.quotes_button.set_popover(popover)
        self.quotes_button.set_focus_on_click(False)
        self.quotes_button.set_tooltip_text('Quotes (Ctrl+")')
        self.quotes_button.get_style_context().add_class('flat')
        button_wrapper.add(self.quotes_button)
        self.quotes_button.get_popover().get_style_context().add_class('menu-own-quotes-symbolic')
        self.top_icons.insert(button_wrapper, 0)

    def insert_math_button(self):
        popover = Gtk.PopoverMenu()
        stack = popover.get_child()

        # main menu
        box = Gtk.VBox()
        self.set_box_margin(box)
        self.add_action_button(box, 'Include AMS Packages', 'win.add-packages', ['amsmath', 'amssymb', 'amsfonts', 'amsthm'])
        self.add_separator(box)
        self.add_action_button(box, 'Inline Math Section ($ ... $)', 'win.insert-before-after', ['$ ', ' $'], keyboard_shortcut='Ctrl+Shift+M')
        self.add_action_button(box, 'Display Math Section (\\[ ... \\])', 'win.insert-before-after', ['\\[ ', ' \\]'], keyboard_shortcut='Alt+Shift+M')
        self.add_menu_button(box, 'Math Environments', 'math_environments')
        self.add_separator(box)
        self.add_action_button(box, 'Subscript (_{})', 'win.insert-before-after', ['_{', '}'], keyboard_shortcut='Ctrl+Shift+D')
        self.add_action_button(box, 'Superscript (^{})', 'win.insert-before-after', ['^{', '}'], keyboard_shortcut='Ctrl+Shift+U')
        self.add_action_button(box, 'Fraction (\\frac)', 'win.insert-symbol', ['\\frac{•}{•}'], keyboard_shortcut='Alt+Shift+F')
        self.add_action_button(box, 'Square Root (\\sqrt)', 'win.insert-before-after', ['\\sqrt{', '}'], keyboard_shortcut='Ctrl+Shift+Q')
        self.add_action_button(box, '\\left', 'win.insert-symbol', ['\\left •'], keyboard_shortcut='Ctrl+Shift+L')
        self.add_action_button(box, '\\right', 'win.insert-symbol', ['\\right •'], keyboard_shortcut='Ctrl+Shift+R')
        self.add_separator(box)
        self.add_menu_button(box, 'Math Functions', 'math_functions')
        self.add_menu_button(box, 'Math Font Styles', 'math_font_styles')
        self.add_menu_button(box, 'Math Stacking Symbols', 'math_stacking_symbols')
        self.add_menu_button(box, 'Math Accents', 'math_accents')
        self.add_menu_button(box, 'Math Spaces', 'math_spaces')
        stack.add_named(box, 'main')
        box.show_all()

        # submenu: math environments
        box = Gtk.VBox()
        self.set_box_margin(box)
        self.add_header_button(box, 'Math Environments')
        for environment in ['equation', 'equation*', 'align', 'align*', 'alignat', 'alignat*', 'flalign', 'flalign*', 'gather', 'gather*', 'multline', 'multline*']:
            self.add_action_button(box, environment, 'win.insert-before-after', ['\\begin{' + environment + '}\n\t', '\n\\end{' + environment + '}'], keyboard_shortcut=('Ctrl+Shift+N' if environment == 'equation' else None))
        self.add_separator(box)
        for environment in ['cases', 'split']:
            self.add_action_button(box, environment, 'win.insert-before-after', ['\\begin{' + environment + '}\n\t', '\n\\end{' + environment + '}'])
        stack.add_named(box, 'math_environments')
        box.show_all()

        # submenu: math functions
        box = Gtk.VBox()
        self.set_box_margin(box)
        self.add_header_button(box, 'Math Functions')
        hbox = Gtk.HBox()
        vbox = Gtk.VBox()
        for math_function in ['arccos', 'arcsin', 'arctan', 'cos', 'cosh', 'cot', 'coth', 'csc', 'deg', 'det', 'dim', 'exp', 'gcd', 'hom', 'inf']:
            self.add_action_button(vbox, '\\' + math_function, 'win.insert-symbol', ['\\' + math_function + ' '])
        hbox.pack_start(vbox, True, True, 0)
        vbox = Gtk.VBox()
        for math_function in ['ker', 'lg', 'lim', 'liminf', 'limsup', 'ln', 'log', 'max', 'min', 'sec', 'sin', 'sinh', 'sup', 'tan', 'tanh']:
            self.add_action_button(vbox, '\\' + math_function, 'win.insert-symbol', ['\\' + math_function + ' '])
        hbox.pack_start(vbox, True, True, 0)
        box.pack_start(hbox, False, False, 0)
        stack.add_named(box, 'math_functions')
        box.show_all()

        # submenu: math font styles
        box = Gtk.VBox()
        self.set_box_margin(box)
        self.add_header_button(box, 'Math Font Styles')
        for math_function in [('Roman', 'mathrm'), ('Italic', 'mathit'), ('Bold', 'mathbf'), ('Sans Serif', 'mathsf'), ('Typewriter', 'mathtt'), ('Calligraphic', 'mathcal'), ('Blackboard Bold', 'mathbb'), ('Fraktur', 'mathfrak')]:
            self.add_action_button(box, math_function[0] + ' (\\' + math_function[1] + ')', 'win.insert-before-after', ['\\' + math_function[1] + '{', '}'])
        stack.add_named(box, 'math_font_styles')
        box.show_all()

        # submenu: math stacking symbols
        box = Gtk.VBox()
        self.set_box_margin(box)
        self.add_header_button(box, 'Math Stacking Symbols')
        for math_stacking_symbol in ['overline', 'underline', 'overbrace', 'underbrace', 'overleftarrow', 'overrightarrow']:
            self.add_action_button(box, '\\' + math_stacking_symbol + '{}', 'win.insert-before-after', ['\\' + math_stacking_symbol + '{', '}'])
        for math_stacking_symbol in ['stackrel', 'overset', 'underset']:
            self.add_action_button(box, '\\' + math_stacking_symbol + '{}{}', 'win.insert-before-after', ['\\' + math_stacking_symbol + '{•}{', '}'])
        stack.add_named(box, 'math_stacking_symbols')
        box.show_all()

        # submenu: math accents
        box = Gtk.VBox()
        self.set_box_margin(box)
        self.add_header_button(box, 'Math Accents')
        for math_accent in ['acute', 'grave', 'tilde', 'bar', 'vec', 'hat', 'check', 'breve', 'dot', 'ddot']:
            self.add_action_button(box, '\\' + math_accent + '{}', 'win.insert-before-after', ['\\' + math_accent + '{', '}'])
        stack.add_named(box, 'math_accents')
        box.show_all()

        # submenu: math spaces
        box = Gtk.VBox()
        self.set_box_margin(box)
        self.add_header_button(box, 'Math Spaces')
        for math_space in [('\\!', 'Negative'), ('\\,', 'Thin'), ('\\:', 'Medium'), ('\\;', 'Thick'), ('\\ ', 'Interword'), ('\\enspace ', 'Enspace'), ('\\quad ', 'One Quad'), ('\\qquad ', 'Two Quads')]:
            self.add_action_button(box, math_space[1], 'win.insert-symbol', [math_space[0]])
        stack.add_named(box, 'math_spaces')
        box.show_all()

        self.math_button = Gtk.MenuButton()
        self.math_button.set_image(Gtk.Image.new_from_icon_name('own-math-menu-symbolic', Gtk.IconSize.MENU))
        self.math_button.set_focus_on_click(False)
        self.math_button.set_tooltip_text('Math')
        self.math_button.get_style_context().add_class('flat')
        self.math_button.set_popover(popover)

        button_wrapper = Gtk.ToolItem()
        button_wrapper.add(self.math_button)
        self.top_icons.insert(button_wrapper, 0)

    def insert_object_button(self):
        popover = Gtk.PopoverMenu()
        stack = popover.get_child()

        # main menu
        box = Gtk.VBox()
        self.set_box_margin(box)
        self.add_action_button(box, 'Figure (image inside freestanding block)', 'win.insert-symbol', ['\\begin{figure}\n\t\\begin{center}\n\t\t\\includegraphics[scale=1]{•}\n\t\t\\caption{•}\n\t\\end{center}\n\\end{figure}'])
        self.add_action_button(box, 'Inline Image', 'win.insert-symbol', ['\\includegraphics[scale=1]{•}'])
        self.add_menu_button(box, 'Code Listing', 'code_listing')
        self.add_menu_button(box, 'List Environments', 'list_environments')
        stack.add_named(box, 'main')
        box.show_all()

        # code listing submenu
        box = Gtk.VBox()
        self.set_box_margin(box)
        self.add_header_button(box, 'Code Listing')
        self.add_action_button(box, 'Include \'listings\' Package', 'win.add-packages', ['listings'])
        self.add_separator(box)
        for language in ['Python', 'C', 'C++', 'Java', 'Perl', 'PHP', 'Ruby', 'TeX']:
            self.add_action_button(box, language, 'win.insert-before-after', ['\\lstset{language=' + language + '}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        self.add_separator(box)
        self.add_action_button(box, 'Other Language', 'win.insert-before-after', ['\\lstset{language=•}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        self.add_action_button(box, 'Plain Text', 'win.insert-before-after', ['\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        stack.add_named(box, 'code_listing')
        box.show_all()

        # list environments submenu
        box = Gtk.VBox()
        self.set_box_margin(box)
        self.add_header_button(box, 'List Environments')
        for list_type in [['Bulleted List (itemize)', 'itemize'], ['Numbered List (enumerate)', 'enumerate'], ['List with Bold Labels (description)', 'description']]:
            self.add_action_button(box, list_type[0], 'win.insert-before-after', ['\\begin{' + list_type[1] + '}\n\t', '\n\\end{' + list_type[1] + '}'])
        self.add_separator(box)
        self.add_action_button(box, 'List Item', 'win.insert-symbol', ['\\item •'], keyboard_shortcut='Ctrl+Shift+I')
        stack.add_named(box, 'list_environments')
        box.show_all()

        button_wrapper = Gtk.ToolItem()
        self.insert_object_button = Gtk.MenuButton()
        self.insert_object_button.set_direction(Gtk.ArrowType.DOWN)
        self.insert_object_button.set_image(Gtk.Image.new_from_icon_name('own-insert-object-symbolic', Gtk.IconSize.MENU))
        self.insert_object_button.set_popover(popover)
        self.insert_object_button.set_focus_on_click(False)
        self.insert_object_button.set_tooltip_text('Objects')
        self.insert_object_button.get_style_context().add_class('flat')
        button_wrapper.add(self.insert_object_button)
        self.insert_object_button.get_popover().get_style_context().add_class('menu-insert-object-symbolic')
        self.top_icons.insert(button_wrapper, 0)
        
    def set_box_margin(self, box):
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_left(10)
        box.set_margin_right(10)

    def add_action_button(self, box, label, action_name, action_parameter=None, keyboard_shortcut=None):
        model_button = Gtk.ModelButton()
        if action_parameter:
            model_button.set_detailed_action_name(Gio.Action.print_detailed_name(action_name, GLib.Variant('as', action_parameter)))
        else:
            model_button.set_action_name(action_name)
        if keyboard_shortcut != None:
            description = Gtk.Label(label)
            description.set_halign(Gtk.Align.START)
            shortcut = Gtk.Label(keyboard_shortcut)
            shortcut.get_style_context().add_class('keyboard-shortcut')
            button_box = Gtk.HBox()
            button_box.pack_start(description, True, True, 0)
            button_box.pack_end(shortcut, False, False, 0)
            model_button.remove(model_button.get_child())
            model_button.add(button_box)
        else:
            model_button.set_label(label)
            model_button.get_child().set_halign(Gtk.Align.START)
        box.pack_start(model_button, False, False, 0)

    def add_menu_button(self, box, label, menu_name):
        model_button = Gtk.ModelButton()
        model_button.set_property('menu-name', menu_name)
        model_button.set_label(label)
        model_button.get_child().set_halign(Gtk.Align.START)
        box.pack_start(model_button, False, False, 0)

    def add_header_button(self, box, label):
        model_button = Gtk.ModelButton()
        model_button.set_property('centered', True)
        model_button.set_property('menu-name', 'main')
        model_button.set_label(label)
        model_button.set_property('inverted', True)
        box.pack_start(model_button, False, False, 0)

    def add_separator(self, box):
        separator = Gtk.SeparatorMenuItem()
        box.pack_start(separator, False, False, 0)



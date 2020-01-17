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
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_left(10)
        box.set_margin_right(10)

        model_button = Gtk.ModelButton()
        model_button.set_action_name('win.include-bibtex-file')
        model_button.set_label('Include BibTeX File...')
        model_button.get_child().set_halign(Gtk.Align.START)
        box.pack_start(model_button, False, False, 0)

        model_button = Gtk.ModelButton()
        model_button.set_detailed_action_name(Gio.Action.print_detailed_name('win.add-packages', GLib.Variant('as', ['natbib'])))
        model_button.set_label('Include \'natbib\' Package')
        model_button.get_child().set_halign(Gtk.Align.START)
        box.pack_start(model_button, False, False, 0)

        separator = Gtk.SeparatorMenuItem()
        box.pack_start(separator, False, False, 0)

        for citation_style in [('Citation', '\\cite{•}'), ('Citation with Page Number', '\\cite[•]{•}')]:
            model_button = Gtk.ModelButton()
            model_button.set_detailed_action_name(Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', [citation_style[1]])))
            model_button.set_label(citation_style[0])
            model_button.get_child().set_halign(Gtk.Align.START)

        model_button = Gtk.ModelButton()
        model_button.set_property('menu-name', 'natbib_citations')
        model_button.set_label('Natbib Citations')
        model_button.get_child().set_halign(Gtk.Align.START)
        box.pack_start(model_button, False, False, 0)

        model_button = Gtk.ModelButton()
        model_button.set_detailed_action_name(Gio.Action.print_detailed_name('win.insert-before-document-end', GLib.Variant('as', ['\\nocite{*}'])))
        model_button.set_label('Include non-cited BibTeX Entries with \'\\nocite\'')
        model_button.get_child().set_halign(Gtk.Align.START)
        box.pack_start(model_button, False, False, 0)

        stack.add_named(box, 'main')
        box.show_all()

        # natbib submenu

        box = Gtk.VBox()
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_left(10)
        box.set_margin_right(10)

        model_button = Gtk.ModelButton()
        model_button.set_property('centered', True)
        model_button.set_property('inverted', True)
        model_button.set_property('menu-name', 'main')
        model_button.set_label('Natbib Citations')
        box.pack_start(model_button, False, False, 0)

        for citation_style in [('Abbreviated', '\\citet{•}'), ('Abbreviated with Brackets', '\\citep{•}'), ('Detailed', '\\citet*{•}'), ('Detailed with Brackets', '\\citep*{•}'), ('Alternative 1', '\\citealt{•}'), ('Alternative 2', '\\citealp{•}')]:
            model_button = Gtk.ModelButton()
            model_button.set_detailed_action_name(Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', [citation_style[1]])))
            model_button.set_label(citation_style[0])
            model_button.get_child().set_halign(Gtk.Align.START)

        separator = Gtk.SeparatorMenuItem()
        box.pack_start(separator, False, False, 0)

        for citation_style in [('Cite Author', '\\citeauthor{•}'), ('Cite Author Detailed', '\\citeauthor*{•}'), ('Cite Year', '\\citeyear{•}'), ('Cite Year with Brackets', '\\citeyearpar{•}')]:
            model_button = Gtk.ModelButton()
            model_button.set_detailed_action_name(Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', [citation_style[1]])))
            model_button.set_label(citation_style[0])
            model_button.get_child().set_halign(Gtk.Align.START)

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
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_left(10)
        box.set_margin_right(10)

        model_button = Gtk.ModelButton()
        model_button.set_detailed_action_name(Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['\\footnote{', '}'])))
        model_button.set_label('Footnote')
        model_button.get_child().set_halign(Gtk.Align.START)
        box.pack_start(model_button, False, False, 0)

        separator = Gtk.SeparatorMenuItem()
        box.pack_start(separator, False, False, 0)

        model_button = Gtk.ModelButton()
        model_button.set_property('menu-name', 'font_styles')
        model_button.set_label('Font Styles')
        model_button.get_child().set_halign(Gtk.Align.START)
        box.pack_start(model_button, False, False, 0)

        model_button = Gtk.ModelButton()
        model_button.set_property('menu-name', 'font_sizes')
        model_button.set_label('Font Sizes')
        model_button.get_child().set_halign(Gtk.Align.START)
        box.pack_start(model_button, False, False, 0)

        stack.add_named(box, 'main')
        box.show_all()

        # font styles submenu

        box = Gtk.VBox()
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_left(10)
        box.set_margin_right(10)

        model_button = Gtk.ModelButton()
        model_button.set_property('centered', True)
        model_button.set_property('inverted', True)
        model_button.set_property('menu-name', 'main')
        model_button.set_label('Font Styles')
        box.pack_start(model_button, False, False, 0)

        for font_style in [('Emphasis (\\emph)', 'emph'), ('Italics (\\textit)', 'textit'), ('Slanted (\\textsl)', 'textsl'), ('Bold (\\textbf)', 'textbf'), ('Typewriter (\\texttt)', 'texttt'), ('Small Caps (\\textsc)', 'textsc'), ('Sans Serif (\\textsf)', 'textsf'), ('Underline (\\underline)', 'underline')]:
            model_button = Gtk.ModelButton()
            model_button.set_detailed_action_name(Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['\\' + font_style[1] + '{', '}'])))
            model_button.set_label(font_style[0])
            model_button.get_child().set_halign(Gtk.Align.START)
            box.pack_start(model_button, False, False, 0)

        stack.add_named(box, 'font_styles')
        box.show_all()

        # font sizes submenu

        box = Gtk.VBox()
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_left(10)
        box.set_margin_right(10)

        model_button = Gtk.ModelButton()
        model_button.set_property('centered', True)
        model_button.set_property('inverted', True)
        model_button.set_property('menu-name', 'main')
        model_button.set_label('Font Sizes')
        box.pack_start(model_button, False, False, 0)

        for font_size in ['tiny', 'scriptsize', 'footnotesize', 'small', 'normalsize', 'large', 'Large', 'LARGE', 'huge', 'Huge']:
            model_button = Gtk.ModelButton()
            model_button.set_detailed_action_name(Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['{\\' + font_size + ' ', '}'])))
            model_button.set_label(font_size)
            model_button.get_child().set_halign(Gtk.Align.START)
            box.pack_start(model_button, False, False, 0)

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
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_left(10)
        box.set_margin_right(10)

        for item in [('Primary Quotes (`` ... \'\')', ['``', '\'\'']), ('Secondary Quotes (` ... \')', ['`', '\'']), ('German Quotes (\\glqq ... \\grqq{})', ['\\glqq ', '\\grqq{}']), ('German Single Quotes (\\glq ... \\grq{})', ['\\glq ', '\\grq{}']), ('French Quotes (\\flqq ... \\frqq{})', ['\\flqq ', '\\frqq{}']), ('French Single Quotes (\\flq ... \\frq{})', ['\\flq ', '\\frq{}']), ('German Alt Quotes (\\frqq ... \\flqq{})', ['\\frqq ', '\\flqq{}']), ('German Alt Single Quotes (\\frq ... \\frq{})', ['\\frq ', '\\flq{}'])]:
            model_button = Gtk.ModelButton()
            model_button.set_detailed_action_name(Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', item[1])))
            model_button.set_label(item[0])
            model_button.get_child().set_halign(Gtk.Align.START)
            box.pack_start(model_button, False, False, 0)

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
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_left(10)
        box.set_margin_right(10)

        model_button = Gtk.ModelButton()
        model_button.set_detailed_action_name(Gio.Action.print_detailed_name('win.add-packages', GLib.Variant('as', ['amsmath', 'amssymb', 'amsfonts', 'amsthm'])))
        model_button.set_label('Include AMS Packages')
        model_button.get_child().set_halign(Gtk.Align.START)
        box.pack_start(model_button, False, False, 0)

        separator = Gtk.SeparatorMenuItem()
        box.pack_start(separator, False, False, 0)

        model_button = Gtk.ModelButton()
        model_button.set_detailed_action_name(Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['$ ', ' $'])))
        model_button.set_label('Inline Math Section ($ ... $)')
        model_button.get_child().set_halign(Gtk.Align.START)
        box.pack_start(model_button, False, False, 0)
        model_button = Gtk.ModelButton()
        model_button.set_detailed_action_name(Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['$ ', ' $'])))
        model_button.set_label('Display Math Section (\\[ ... \\])')
        model_button.get_child().set_halign(Gtk.Align.START)
        box.pack_start(model_button, False, False, 0)
        model_button = Gtk.ModelButton()
        model_button.set_property('menu-name', 'math_environments')
        model_button.set_label('Math Environments')
        model_button.get_child().set_halign(Gtk.Align.START)
        box.pack_start(model_button, False, False, 0)

        separator = Gtk.SeparatorMenuItem()
        box.pack_start(separator, False, False, 0)

        model_button = Gtk.ModelButton()
        model_button.set_property('menu-name', 'math_functions')
        model_button.set_label('Math Functions')
        model_button.get_child().set_halign(Gtk.Align.START)
        box.pack_start(model_button, False, False, 0)

        stack.add_named(box, 'main')
        box.show_all()

        # submenu: math environments

        box = Gtk.VBox()
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_left(10)
        box.set_margin_right(10)

        model_button = Gtk.ModelButton()
        model_button.set_property('centered', True)
        model_button.set_property('menu-name', 'main')
        model_button.set_label('Math Environments')
        model_button.set_property('inverted', True)
        box.pack_start(model_button, False, False, 0)

        for environment in ['equation', 'equation*', 'align', 'align*', 'alignat', 'alignat*', 'flalign', 'flalign*', 'gather', 'gather*', 'multline', 'multline*']:
            model_button = Gtk.ModelButton()
            model_button.set_detailed_action_name(Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['\\begin{' + environment + '}\n\t', '\n\\end{' + environment + '}'])))
            model_button.set_label(environment)
            model_button.get_child().set_halign(Gtk.Align.START)
            box.pack_start(model_button, False, False, 0)

        separator = Gtk.SeparatorMenuItem()
        box.pack_start(separator, False, False, 0)

        for environment in ['cases', 'split']:
            model_button = Gtk.ModelButton()
            model_button.set_detailed_action_name(Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['\\begin{' + environment + '}\n\t', '\n\\end{' + environment + '}'])))
            model_button.set_label(environment)
            model_button.get_child().set_halign(Gtk.Align.START)
            box.pack_start(model_button, False, False, 0)

        stack.add_named(box, 'math_environments')
        box.show_all()

        # submenu: math functions

        box = Gtk.VBox()
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_left(10)
        box.set_margin_right(10)

        model_button = Gtk.ModelButton()
        model_button.set_property('centered', True)
        model_button.set_property('menu-name', 'main')
        model_button.set_label('Math Functions')
        model_button.set_property('inverted', True)
        box.pack_start(model_button, False, False, 0)

        hbox = Gtk.HBox()

        vbox = Gtk.VBox()
        for math_function in ['arccos', 'arcsin', 'arctan', 'cos', 'cosh', 'cot', 'coth', 'csc', 'deg', 'det', 'dim', 'exp', 'gcd', 'hom', 'inf']:
            model_button = Gtk.ModelButton()
            model_button.set_detailed_action_name(Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', ['\\' + math_function + ' '])))
            model_button.set_label('\\' + math_function)
            model_button.get_child().set_halign(Gtk.Align.START)
            vbox.pack_start(model_button, False, False, 0)
        hbox.pack_start(vbox, True, True, 0)

        vbox = Gtk.VBox()
        for math_function in ['ker', 'lg', 'lim', 'liminf', 'limsup', 'ln', 'log', 'max', 'min', 'sec', 'sin', 'sinh', 'sup', 'tan', 'tanh']:
            model_button = Gtk.ModelButton()
            model_button.set_detailed_action_name(Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', ['\\' + math_function + ' '])))
            model_button.set_label('\\' + math_function)
            model_button.get_child().set_halign(Gtk.Align.START)
            vbox.pack_start(model_button, False, False, 0)
        hbox.pack_start(vbox, True, True, 0)

        box.pack_start(hbox, False, False, 0)

        stack.add_named(box, 'math_functions')
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
        menu = Gio.Menu()
        section = Gio.Menu()

        section.append_item(Gio.MenuItem.new('Figure (image inside freestanding block)', Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', ['''\\begin{figure}
	\\begin{center}
		\\includegraphics[scale=1]{•}
		\\caption{•}
	\\end{center}
\\end{figure}
''']))))
        section.append_item(Gio.MenuItem.new('Inline Image', Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', ['\\includegraphics[scale=1]{•}']))))

        codeblock_menu = Gio.Menu()
        codeblock_package_section = Gio.Menu()
        item = Gio.MenuItem.new('Include \'listings\' Package', Gio.Action.print_detailed_name('win.add-packages', GLib.Variant('as', ['listings'])))
        codeblock_package_section.append_item(item)
        codeblock_menu.append_section(None, codeblock_package_section)

        codeblock_main_section = Gio.Menu()
        for language in ['Python', 'C', 'C++', 'Java', 'Perl', 'PHP', 'Ruby', 'TeX']:
            codeblock_main_section.append_item(Gio.MenuItem.new(language, Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['''\\lstset{language=''' + language + '''}
\\begin{lstlisting}
    ''', '''
\\end{lstlisting}''']))))
        codeblock_menu.append_section(None, codeblock_main_section)
        codeblock_other_section = Gio.Menu()
        codeblock_other_section.append_item(Gio.MenuItem.new('Other Language', Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['''\\lstset{language=}
\\begin{lstlisting}
    ''', '''
\\end{lstlisting}
''']))))
        codeblock_other_section.append_item(Gio.MenuItem.new('Plain Text', Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['''\\begin{lstlisting}
    ''', '''
\\end{lstlisting}
''']))))
        codeblock_menu.append_section(None, codeblock_other_section)
        section.append_submenu('Code Listing', codeblock_menu)

        list_environments_menu = Gio.Menu()
        list_environments_main_section = Gio.Menu()
        for list_type in [['Bulleted List (itemize)', 'itemize'], ['Numbered List (enumerate)', 'enumerate'], ['List with Bold Labels (description)', 'description']]:
            list_environments_main_section.append_item(Gio.MenuItem.new(list_type[0], Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['\\begin{' + list_type[1] + '}\n\t', '\n\\end{' + list_type[1] + '}']))))
        list_environments_menu.append_section(None, list_environments_main_section)
        item_section = Gio.Menu()
        item_section.append_item(Gio.MenuItem.new('List Item', Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', ['\\item •']))))
        list_environments_menu.append_section(None, item_section)
        section.append_submenu('List Environments', list_environments_menu)

        menu.append_section(None, section)

        button_wrapper = Gtk.ToolItem()
        self.insert_object_button = Gtk.MenuButton()
        self.insert_object_button.set_direction(Gtk.ArrowType.DOWN)
        self.insert_object_button.set_image(Gtk.Image.new_from_icon_name('own-insert-object-symbolic', Gtk.IconSize.MENU))
        self.insert_object_button.set_menu_model(menu)
        self.insert_object_button.set_focus_on_click(False)
        self.insert_object_button.set_use_popover(True)
        self.insert_object_button.set_tooltip_text('Objects')
        self.insert_object_button.get_style_context().add_class('flat')
        button_wrapper.add(self.insert_object_button)
        self.insert_object_button.get_popover().get_style_context().add_class('menu-insert-object-symbolic')
        self.top_icons.insert(button_wrapper, 0)
        


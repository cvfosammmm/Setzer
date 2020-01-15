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
        bibliography_menu = Gio.Menu()

        section = Gio.Menu()
        menu_item = Gio.MenuItem.new('Include BibTeX File...', 'win.include-bibtex-file')
        section.append_item(menu_item)
        menu_item = Gio.MenuItem.new('Include \'natbib\' Package', Gio.Action.print_detailed_name('win.add-packages', GLib.Variant('as', ['natbib'])))
        section.append_item(menu_item)
        bibliography_menu.append_section(None, section)

        section = Gio.Menu()
        menu_item = Gio.MenuItem.new('Citation', Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', ['\\cite{•}'])))
        section.append_item(menu_item)
        menu_item = Gio.MenuItem.new('Citation with Page Number', Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', ['\\cite[•]{•}'])))
        section.append_item(menu_item)
        natbib_submenu = Gio.Menu()
        natbib_submenu1 = Gio.Menu()
        menu_item = Gio.MenuItem.new('Abbreviated', Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', ['\\citet{•}'])))
        natbib_submenu1.append_item(menu_item)
        menu_item = Gio.MenuItem.new('Abbreviated with Brackets', Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', ['\\citep{•}'])))
        natbib_submenu1.append_item(menu_item)
        menu_item = Gio.MenuItem.new('Detailed', Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', ['\\citet*{•}'])))
        natbib_submenu1.append_item(menu_item)
        menu_item = Gio.MenuItem.new('Detailed with Brackets', Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', ['\\citep*{•}'])))
        natbib_submenu1.append_item(menu_item)
        menu_item = Gio.MenuItem.new('Alternative 1', Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', ['\\citealt{•}'])))
        natbib_submenu1.append_item(menu_item)
        menu_item = Gio.MenuItem.new('Alternative 2', Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', ['\\citealp{•}'])))
        natbib_submenu1.append_item(menu_item)
        natbib_submenu.append_section(None, natbib_submenu1)
        natbib_submenu2 = Gio.Menu()
        menu_item = Gio.MenuItem.new('Cite Author', Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', ['\\citeauthor{•}'])))
        natbib_submenu2.append_item(menu_item)
        menu_item = Gio.MenuItem.new('Cite Author Detailed', Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', ['\\citeauthor*{•}'])))
        natbib_submenu2.append_item(menu_item)
        menu_item = Gio.MenuItem.new('Cite Year', Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', ['\\citeyear{•}'])))
        natbib_submenu2.append_item(menu_item)
        menu_item = Gio.MenuItem.new('Cite Year with Brackets', Gio.Action.print_detailed_name('win.insert-symbol', GLib.Variant('as', ['\\citeyearpar{•}'])))
        natbib_submenu2.append_item(menu_item)
        natbib_submenu.append_section(None, natbib_submenu2)
        section.append_submenu('Natbib Citations', natbib_submenu)
        bibliography_menu.append_section(None, section)

        menu_item = Gio.MenuItem.new('Include non-cited BibTeX Entries with \'\\nocite\'', Gio.Action.print_detailed_name('win.insert-before-document-end', GLib.Variant('as', ['\\nocite{*}'])))
        bibliography_menu.append_item(menu_item)

        self.bibliography_button = Gtk.MenuButton()
        self.bibliography_button.set_image(Gtk.Image.new_from_icon_name('view-dual-symbolic', Gtk.IconSize.MENU))
        self.bibliography_button.set_focus_on_click(False)
        self.bibliography_button.set_tooltip_text('Bibliography')
        self.bibliography_button.get_style_context().add_class('flat')
        self.bibliography_button.set_menu_model(bibliography_menu)

        button_wrapper = Gtk.ToolItem()
        button_wrapper.add(self.bibliography_button)
        self.top_icons.insert(button_wrapper, 0)

    def insert_text_button(self):
        text_menu = Gio.Menu()
        menu_item = Gio.MenuItem.new('Footnote', Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['\\footnote{', '}'])))
        text_menu.append_item(menu_item)

        section = Gio.Menu()

        # font styles submenu
        font_size_menu = Gio.Menu()
        for font_style in [('Emphasis (\\emph)', 'emph'), ('Italics (\\textit)', 'textit'), ('Slanted (\\textsl)', 'textsl'), ('Bold (\\textbf)', 'textbf'), ('Typewriter (\\texttt)', 'texttt'), ('Small Caps (\\textsc)', 'textsc'), ('Sans Serif (\\textsf)', 'textsf'), ('Underline (\\underline)', 'underline')]:
            menu_item = Gio.MenuItem.new(font_style[0], Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['\\' + font_style[1] + '{', '}'])))
            font_size_menu.append_item(menu_item)
        section.append_submenu('Font Styles', font_size_menu)

        # font sizes submenu
        font_size_menu = Gio.Menu()
        for font_size in ['tiny', 'scriptsize', 'footnotesize', 'small', 'normalsize', 'large', 'Large', 'LARGE', 'huge', 'Huge']:
            menu_item = Gio.MenuItem.new(font_size, Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['{\\' + font_size + ' ', '}'])))
            font_size_menu.append_item(menu_item)
        section.append_submenu('Font Sizes', font_size_menu)

        text_menu.append_section(None, section)

        self.text_button = Gtk.MenuButton()
        self.text_button.set_image(Gtk.Image.new_from_icon_name('text-symbolic', Gtk.IconSize.MENU))
        self.text_button.set_focus_on_click(False)
        self.text_button.set_tooltip_text('Text')
        self.text_button.get_style_context().add_class('flat')
        self.text_button.set_menu_model(text_menu)

        button_wrapper = Gtk.ToolItem()
        button_wrapper.add(self.text_button)
        self.top_icons.insert(button_wrapper, 0)

    def insert_quotes_button(self):
        self.quotes_menu_data = list()
        self.quotes_menu_data.append({'type': 'item', 'label': 'Primary Quotes (`` ... \'\')', 'action': 'win.insert-before-after', 'target_value': GLib.Variant('as', ['``', '\'\''])})
        self.quotes_menu_data.append({'type': 'item', 'label': 'Secondary Quotes (` ... \')', 'action': 'win.insert-before-after', 'target_value': GLib.Variant('as', ['`', '\''])})
        self.quotes_menu_data.append({'type': 'item', 'label': 'German Quotes (\\glqq ... \\grqq{})', 'action': 'win.insert-before-after', 'target_value': GLib.Variant('as', ['\\glqq ', '\\grqq{}'])})
        self.quotes_menu_data.append({'type': 'item', 'label': 'German Single Quotes (\\glq ... \\grq{})', 'action': 'win.insert-before-after', 'target_value': GLib.Variant('as', ['\\glq ', '\\grq{}'])})
        self.quotes_menu_data.append({'type': 'item', 'label': 'French Quotes (\\flqq ... \\frqq{})', 'action': 'win.insert-before-after', 'target_value': GLib.Variant('as', ['\\flqq ', '\\frqq{}'])})
        self.quotes_menu_data.append({'type': 'item', 'label': 'French Single Quotes (\\flq ... \\frq{})', 'action': 'win.insert-before-after', 'target_value': GLib.Variant('as', ['\\flq ', '\\frq{}'])})
        self.quotes_menu_data.append({'type': 'item', 'label': 'German Alt Quotes (\\frqq ... \\flqq{})', 'action': 'win.insert-before-after', 'target_value': GLib.Variant('as', ['\\frqq ', '\\flqq{}'])})
        self.quotes_menu_data.append({'type': 'item', 'label': 'German Alt Single Quotes (\\frq ... \\frq{})', 'action': 'win.insert-before-after', 'target_value': GLib.Variant('as', ['\\frq ', '\\flq{}'])})
        menu = Gio.Menu()
        section = Gio.Menu()
        for menu_item_data in self.quotes_menu_data:
            if menu_item_data['type'] == 'item':
                menu_item = Gio.MenuItem.new(menu_item_data['label'], Gio.Action.print_detailed_name(menu_item_data['action'], menu_item_data['target_value']))
                section.append_item(menu_item)
            elif menu_item_data['type'] == 'section':
                menu.append_section(None, section)
                section = Gio.Menu()
        menu.append_section(None, section)
        button_wrapper = Gtk.ToolItem()
        self.quotes_button = Gtk.MenuButton()
        self.quotes_button.set_direction(Gtk.ArrowType.DOWN)
        self.quotes_button.set_image(Gtk.Image.new_from_icon_name('own-quotes-symbolic', Gtk.IconSize.MENU))
        self.quotes_button.set_menu_model(menu)
        self.quotes_button.set_focus_on_click(False)
        self.quotes_button.set_use_popover(True)
        self.quotes_button.set_tooltip_text('Quotes (Ctrl+")')
        self.quotes_button.get_style_context().add_class('flat')
        button_wrapper.add(self.quotes_button)
        self.quotes_button.get_popover().get_style_context().add_class('menu-own-quotes-symbolic')
        self.top_icons.insert(button_wrapper, 0)

    def insert_math_button(self):
        math_menu = Gio.Menu()

        # packages
        section = Gio.Menu()
        menu_item = Gio.MenuItem.new('Include AMS Packages', Gio.Action.print_detailed_name('win.add-packages', GLib.Variant('as', ['amsmath', 'amssymb', 'amsfonts', 'amsthm'])))
        section.append_item(menu_item)
        math_menu.append_section(None, section)

        # math environments
        section = Gio.Menu()
        menu_item = Gio.MenuItem.new('Inline Math Section ($ ... $)', Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['$ ', ' $'])))
        section.append_item(menu_item)
        menu_item = Gio.MenuItem.new('Display Math Section (\\[ ... \\])', Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['$ ', ' $'])))
        section.append_item(menu_item)
        math_environments_menu = Gio.Menu()
        subsection = Gio.Menu()
        for environment in ['equation', 'equation*', 'align', 'align*', 'alignat', 'alignat*', 'flalign', 'flalign*', 'gather', 'gather*', 'multline', 'multline*']:
            menu_item = Gio.MenuItem.new(environment, Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['\\begin{' + environment + '}\n\t', '\n\\end{' + environment + '}'])))
            subsection.append_item(menu_item)
        math_environments_menu.append_section(None, subsection)
        subsection = Gio.Menu()
        for environment in ['cases', 'split']:
            menu_item = Gio.MenuItem.new(environment, Gio.Action.print_detailed_name('win.insert-before-after', GLib.Variant('as', ['\\begin{' + environment + '}\n\t', '\n\\end{' + environment + '}'])))
            subsection.append_item(menu_item)
        math_environments_menu.append_section(None, subsection)
        section.append_submenu('Math Environments', math_environments_menu)
        
        math_menu.append_section(None, section)

        self.math_button = Gtk.MenuButton()
        self.math_button.set_image(Gtk.Image.new_from_icon_name('own-math-menu-symbolic', Gtk.IconSize.MENU))
        self.math_button.set_focus_on_click(False)
        self.math_button.set_tooltip_text('Math')
        self.math_button.get_style_context().add_class('flat')
        self.math_button.set_menu_model(math_menu)

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
        


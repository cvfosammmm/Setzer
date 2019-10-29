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
        self.pack_start(self.top_icons, True, True, 0)

    def create_top_toolbar(self):
        self.top_icons = Gtk.Toolbar()
        self.top_icons.set_style(Gtk.ToolbarStyle.ICONS)
        self.top_icons.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.top_icons.set_icon_size(Gtk.IconSize.SMALL_TOOLBAR)
        self.get_style_context().add_class('top')
        
    def populate_top_toolbar(self):
        menu = Gio.Menu()
        section = Gio.Menu()

        section.append_item(Gio.MenuItem.new('Insert Figure (image inside freestanding block)', Gio.Action.print_detailed_name('app.insert-symbol', GLib.Variant('as', ['''\\begin{figure}
    \\begin{center}
        \\includegraphics[scale=1]{}
        \\caption{}
    \\end{center}
\\end{figure}
''']))))
        section.append_item(Gio.MenuItem.new('Insert Inline Image', Gio.Action.print_detailed_name('app.insert-symbol', GLib.Variant('as', ['\\includegraphics[scale=1]{}']))))

        codeblock_menu = Gio.Menu()
        codeblock_main_section = Gio.Menu()
        for language in ['Python', 'C', 'C++', 'Java', 'Perl', 'PHP', 'Ruby', 'TeX']:
            codeblock_main_section.append_item(Gio.MenuItem.new(language, Gio.Action.print_detailed_name('app.insert-symbol', GLib.Variant('as', ['''\\lstset{language=''' + language + '''}
\\begin{lstlisting}

\\end{lstlisting}
''']))))
        codeblock_menu.append_section(None, codeblock_main_section)
        codeblock_other_section = Gio.Menu()
        codeblock_other_section.append_item(Gio.MenuItem.new('Other Language', Gio.Action.print_detailed_name('app.insert-symbol', GLib.Variant('as', ['''\\lstset{language=}
\\begin{lstlisting}

\\end{lstlisting}
''']))))
        codeblock_other_section.append_item(Gio.MenuItem.new('Plain Text', Gio.Action.print_detailed_name('app.insert-symbol', GLib.Variant('as', ['''\\begin{lstlisting}

\\end{lstlisting}
''']))))
        codeblock_menu.append_section(None, codeblock_other_section)
        section.append_submenu('Insert Code Listing', codeblock_menu)

        menu.append_section(None, section)

        button_wrapper = Gtk.ToolItem()
        self.insert_object_button = Gtk.MenuButton()
        self.insert_object_button.set_direction(Gtk.ArrowType.DOWN)
        self.insert_object_button.set_image(Gtk.Image.new_from_icon_name('own-insert-object-symbolic', Gtk.IconSize.MENU))
        self.insert_object_button.set_menu_model(menu)
        self.insert_object_button.set_focus_on_click(False)
        self.insert_object_button.set_use_popover(True)
        self.insert_object_button.set_tooltip_text('Insert object')
        button_wrapper.add(self.insert_object_button)
        self.insert_object_button.get_popover().get_style_context().add_class('menu-insert-object-symbolic')
        self.top_icons.insert(button_wrapper, 0)
        
        self.quotes_menu_data = list()
        self.quotes_menu_data.append({'type': 'item', 'label': 'Primary Quotes (`` ... \'\')', 'action': 'app.insert-before-after', 'target_value': GLib.Variant('as', ['``', '\'\''])})
        self.quotes_menu_data.append({'type': 'item', 'label': 'Secondary Quotes (` ... \')', 'action': 'app.insert-before-after', 'target_value': GLib.Variant('as', ['`', '\''])})
        self.quotes_menu_data.append({'type': 'item', 'label': 'German Quotes (\\glqq ... \\grqq{})', 'action': 'app.insert-before-after', 'target_value': GLib.Variant('as', ['\\glqq ', '\\grqq{}'])})
        self.quotes_menu_data.append({'type': 'item', 'label': 'German Single Quotes (\\glq ... \\grq{})', 'action': 'app.insert-before-after', 'target_value': GLib.Variant('as', ['\\glq ', '\\grq{}'])})
        self.quotes_menu_data.append({'type': 'item', 'label': 'French Quotes (\\flqq ... \\frqq{})', 'action': 'app.insert-before-after', 'target_value': GLib.Variant('as', ['\\flqq ', '\\frqq{}'])})
        self.quotes_menu_data.append({'type': 'item', 'label': 'French Single Quotes (\\flq ... \\frq{})', 'action': 'app.insert-before-after', 'target_value': GLib.Variant('as', ['\\flq ', '\\frq{}'])})
        self.quotes_menu_data.append({'type': 'item', 'label': 'German Alt Quotes (\\frqq ... \\flqq{})', 'action': 'app.insert-before-after', 'target_value': GLib.Variant('as', ['\\frqq ', '\\flqq{}'])})
        self.quotes_menu_data.append({'type': 'item', 'label': 'German Alt Single Quotes (\\frq ... \\frq{})', 'action': 'app.insert-before-after', 'target_value': GLib.Variant('as', ['\\frq ', '\\flq{}'])})
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
        button_wrapper.add(self.quotes_button)
        self.quotes_button.get_popover().get_style_context().add_class('menu-own-quotes-symbolic')
        self.top_icons.insert(button_wrapper, 0)
        
        self.italic_button = Gtk.ToolButton()
        self.italic_button.set_icon_name('format-text-italic-symbolic')
        self.italic_button.set_action_name('app.insert-before-after')
        self.italic_button.set_action_target_value(GLib.Variant('as', ['\\textit{', '}']))
        self.italic_button.set_focus_on_click(False)
        self.italic_button.set_tooltip_text('Italic (Ctrl+I)')
        self.top_icons.insert(self.italic_button, 0)

        self.bold_button = Gtk.ToolButton()
        self.bold_button.set_icon_name('format-text-bold-symbolic')
        self.bold_button.set_action_name('app.insert-before-after')
        self.bold_button.set_action_target_value(GLib.Variant('as', ['\\textbf{', '}']))
        self.bold_button.set_focus_on_click(False)
        self.bold_button.set_tooltip_text('Bold (Ctrl+B)')
        self.top_icons.insert(self.bold_button, 0)

        self.document_wizard_button = Gtk.ToolButton()
        self.document_wizard_button.set_icon_name('own-wizard-symbolic')
        self.document_wizard_button.set_action_name('app.show-document-wizard')
        self.document_wizard_button.set_focus_on_click(False)
        self.document_wizard_button.set_tooltip_text('Create a template document')
        self.top_icons.insert(self.document_wizard_button, 0)



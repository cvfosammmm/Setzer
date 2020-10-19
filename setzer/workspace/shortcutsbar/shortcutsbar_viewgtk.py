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

from setzer.app.service_locator import ServiceLocator


class ShortcutsBar(Gtk.HBox):

    def __init__(self):
        Gtk.HBox.__init__(self)
        self.get_style_context().add_class('shortcutsbar')
        self.pmb = ServiceLocator.get_popover_menu_builder()

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
        self.button_build_log.set_icon_name('build-log-symbolic')
        self.button_build_log.set_tooltip_text(_('Build log') + ' (F8)')
        self.button_build_log.get_child().set_can_focus(False)
        self.right_icons.insert(self.button_build_log, 0)

    def populate_top_toolbar(self):
        self.italic_button = Gtk.ToolButton()
        self.italic_button.set_icon_name('format-text-italic-symbolic')
        self.italic_button.set_label(_('Italic Text'))
        self.italic_button.set_action_name('win.insert-before-after')
        self.italic_button.set_action_target_value(GLib.Variant('as', ['\\textit{', '}']))
        self.italic_button.get_child().set_can_focus(False)
        self.italic_button.set_tooltip_text(_('Italic') + ' (' + _('Ctrl') + '+I)')
        self.top_icons.insert(self.italic_button, 0)

        self.bold_button = Gtk.ToolButton()
        self.bold_button.set_icon_name('format-text-bold-symbolic')
        self.bold_button.set_label(_('Bold Text'))
        self.bold_button.set_action_name('win.insert-before-after')
        self.bold_button.set_action_target_value(GLib.Variant('as', ['\\textbf{', '}']))
        self.bold_button.get_child().set_can_focus(False)
        self.bold_button.set_tooltip_text(_('Bold') + ' (' + _('Ctrl') + '+B)')
        self.top_icons.insert(self.bold_button, 0)

        self.insert_quotes_button()
        self.insert_math_button()
        self.insert_text_button()
        self.insert_object_button()
        self.insert_bibliography_button()
        self.insert_document_button()

    def insert_document_button(self):
        popover = Gtk.PopoverMenu()
        stack = popover.get_child()

        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_action_button(box, '\\documentclass', 'win.insert-symbol', ['\\documentclass[•]{•}'])
        self.pmb.add_action_button(box, _('Add / Remove Packages') + '...', 'win.add-remove-packages-dialog')
        self.pmb.add_menu_button(box, _('Document Info'), 'document_info')
        self.pmb.add_separator(box)
        self.pmb.add_action_button(box, _('Document Environment'), 'win.insert-before-after', ['\\begin{document}\n\t', '\n\\end{document}'])
        self.pmb.add_action_button(box, _('Show Title') + ' (\\maketitle)', 'win.insert-symbol', ['\\maketitle'])
        self.pmb.add_action_button(box, _('Table of Contents'), 'win.insert-symbol', ['\\tableofcontents'])
        self.pmb.add_separator(box)
        self.pmb.add_action_button(box, _('Include LaTeX File') + ' (\\input)...', 'win.include-latex-file')
        stack.add_named(box, 'main')
        box.show_all()

        # document info submenu
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, _('Document Info'))
        self.pmb.add_action_button(box, _('Author'), 'win.insert-symbol', ['\\author{•}'])
        self.pmb.add_action_button(box, _('Title'), 'win.insert-symbol', ['\\title{•}'])
        self.pmb.add_action_button(box, _('Date'), 'win.insert-symbol', ['\\date{•}'])
        self.pmb.add_action_button(box, _('Date Today'), 'win.insert-symbol', ['\\date{\\today}'])
        stack.add_named(box, 'document_info')
        box.show_all()

        self.document_button = Gtk.MenuButton()
        self.document_button.set_image(Gtk.Image.new_from_icon_name('application-x-addon-symbolic', Gtk.IconSize.MENU))
        self.document_button.set_can_focus(False)
        self.document_button.set_tooltip_text(_('Document'))
        self.document_button.get_style_context().add_class('flat')
        self.document_button.set_popover(popover)

        button_wrapper = Gtk.ToolItem()
        button_wrapper.add(self.document_button)
        self.top_icons.insert(button_wrapper, 0)

    def insert_bibliography_button(self):
        popover = Gtk.PopoverMenu()
        stack = popover.get_child()

        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_action_button(box, _('Include BibTeX File') + '...', 'win.include-bibtex-file')
        self.pmb.add_action_button(box, _('Include \'natbib\' Package'), 'win.add-packages', ['natbib'])
        self.pmb.add_separator(box)
        for citation_style in [(_('Citation'), '\\cite{•}'), (_('Citation with Page Number'), '\\cite[•]{•}')]:
            self.pmb.add_action_button(box, citation_style[0], 'win.insert-symbol', [citation_style[1]])
        self.pmb.add_menu_button(box, _('Natbib Citations'), 'natbib_citations')
        self.pmb.add_action_button(box, _('Include non-cited BibTeX Entries with \'\\nocite\''), 'win.insert-before-document-end', ['\\nocite{*}'])
        stack.add_named(box, 'main')
        box.show_all()

        # natbib submenu
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, _('Natbib Citations'))
        for citation_style in [(_('Abbreviated'), '\\citet{•}'), (_('Abbreviated with Brackets'), '\\citep{•}'), (_('Detailed'), '\\citet*{•}'), (_('Detailed with Brackets'), '\\citep*{•}'), (_('Alternative 1'), '\\citealt{•}'), (_('Alternative 2'), '\\citealp{•}')]:
            self.pmb.add_action_button(box, citation_style[0], 'win.insert-symbol', [citation_style[1]])
        self.pmb.add_separator(box)
        for citation_style in [(_('Cite Author'), '\\citeauthor{•}'), (_('Cite Author Detailed'), '\\citeauthor*{•}'), (_('Cite Year'), '\\citeyear{•}'), (_('Cite Year with Brackets'), '\\citeyearpar{•}')]:
            self.pmb.add_action_button(box, citation_style[0], 'win.insert-symbol', [citation_style[1]])
        stack.add_named(box, 'natbib_citations')
        box.show_all()

        self.bibliography_button = Gtk.MenuButton()
        self.bibliography_button.set_image(Gtk.Image.new_from_icon_name('view-dual-symbolic', Gtk.IconSize.MENU))
        self.bibliography_button.set_can_focus(False)
        self.bibliography_button.set_tooltip_text(_('Bibliography'))
        self.bibliography_button.get_style_context().add_class('flat')
        self.bibliography_button.set_popover(popover)

        button_wrapper = Gtk.ToolItem()
        button_wrapper.add(self.bibliography_button)
        self.top_icons.insert(button_wrapper, 0)

    def insert_text_button(self):
        popover = Gtk.PopoverMenu()
        stack = popover.get_child()

        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_menu_button(box, _('Font Styles'), 'font_styles')
        self.pmb.add_menu_button(box, _('Font Sizes'), 'font_sizes')
        self.pmb.add_menu_button(box, _('Alignment'), 'text_alignment')
        self.pmb.add_menu_button(box, _('Vertical Spacing'), 'vertical_spacing')
        self.pmb.add_menu_button(box, _('International Accents'), 'international_accents')
        self.pmb.add_separator(box)
        self.pmb.add_menu_button(box, _('Sectioning'), 'sectioning')
        self.pmb.add_separator(box)
        self.pmb.add_action_button(box, _('Environment'), 'win.insert-before-after', ['\\begin{•}\n\t', '\n\\end{•}'], keyboard_shortcut=_('Ctrl') + '+E')
        self.pmb.add_action_button(box, _('Verbatim Environment'), 'win.insert-before-after', ['\\begin{verbatim}\n\t', '\n\\end{verbatim}'])
        self.pmb.add_menu_button(box, _('List Environments'), 'list_environments')
        self.pmb.add_menu_button(box, _('Quotations'), 'quotations')
        self.pmb.add_separator(box)
        self.pmb.add_menu_button(box, _('Cross References'), 'cross_references')
        self.pmb.add_action_button(box, _('Footnote'), 'win.insert-before-after', ['\\footnote{', '}'])
        stack.add_named(box, 'main')
        box.show_all()

        # font styles submenu
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, _('Font Styles'))
        for font_style in [(_('Bold') + ' (\\textbf)', 'textbf', 'format-text-bold-symbolic', _('Ctrl') + '+B'), (_('Italic') + ' (\\textit)', 'textit', 'format-text-italic-symbolic', _('Ctrl') + '+I'), (_('Underline') + ' (\\underline)', 'underline', 'format-text-underline-symbolic', _('Ctrl') + '+U'), (_('Sans Serif') + ' (\\textsf)', 'textsf', 'placeholder', None), (_('Typewriter') + ' (\\texttt)', 'texttt', 'placeholder', _('Ctrl') + '+M'), (_('Small Caps') + ' (\\textsc)', 'textsc', 'placeholder', None), (_('Slanted') + ' (\\textsl)', 'textsl', 'placeholder', None), (_('Emphasis') + ' (\\emph)', 'emph', 'placeholder', _('Shift') + '+' + _('Ctrl') + '+E')]:
            icon_name = font_style[2]
            self.pmb.add_action_button(box, font_style[0], 'win.insert-before-after', ['\\' + font_style[1] + '{', '}'], icon_name=icon_name, keyboard_shortcut=font_style[3])
        stack.add_named(box, 'font_styles')
        box.show_all()

        # font sizes submenu
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, _('Font Sizes'))
        for font_size in ['tiny', 'scriptsize', 'footnotesize', 'small', 'normalsize', 'large', 'Large', 'LARGE', 'huge', 'Huge']:
            self.pmb.add_action_button(box, font_size, 'win.insert-before-after', ['{\\' + font_size + ' ', '}'])
        stack.add_named(box, 'font_sizes')
        box.show_all()

        # text alignment submenu
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, _('Alignment'))
        for command in [(_('Centered'), 'center', 'format-justify-center-symbolic'), (_('Left-aligned'), 'flushleft', 'format-justify-left-symbolic'), (_('Right-aligned'), 'flushright', 'format-justify-right-symbolic')]:
            self.pmb.add_action_button(box, command[0], 'win.insert-before-after', ['\\begin{' + command[1] + '}\n\t', '\n\\end{' + command[1] + '}'], icon_name=command[2])
        stack.add_named(box, 'text_alignment')
        box.show_all()

        # vertical spacing submenu
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, _('Vertical Spacing'))
        for command in ['newpage', 'linebreak', 'pagebreak', 'bigskip', 'medskip', 'smallskip']:
            self.pmb.add_action_button(box, '\\' + command, 'win.insert-symbol', ['\\' + command])
        self.pmb.add_action_button(box, '\\vspace', 'win.insert-symbol', ['\\vspace{•}'])
        self.pmb.add_action_button(box, _('New Line')+ ' (\\\\)', 'win.insert-symbol', ['\\\\\n'], keyboard_shortcut=_('Ctrl') + '+Return')
        stack.add_named(box, 'vertical_spacing')
        box.show_all()

        # international accents submenu
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, _('International Accents'))
        for command in [('\'', 'menu-accents-1-symbolic'), ('`', 'menu-accents-2-symbolic'), ('^', 'menu-accents-3-symbolic'), ('"', 'menu-accents-4-symbolic'), ('~', 'menu-accents-5-symbolic'), ('=', 'menu-accents-6-symbolic'), ('.', 'menu-accents-7-symbolic'), ('v', 'menu-accents-8-symbolic'), ('u', 'menu-accents-9-symbolic'), ('H', 'menu-accents-10-symbolic')]:
            self.pmb.add_action_button(box, '\\' + command[0] + '{}', 'win.insert-before-after', ['\\' + command[0] + '{', '}'], icon_name=command[1])
        stack.add_named(box, 'international_accents')
        box.show_all()

        # sectioning submenu
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, _('Sectioning'))
        for citation_style in [(_('Part'), '\\part{•}'), (_('Chapter'), '\\chapter{•}'), (_('Section'), '\\section{•}'), (_('Subsection'), '\\subsection{•}'), (_('Subsubsection'), '\\subsubsection{•}'), (_('Paragraph'), '\\paragraph{•}'), (_('Subparagraph'), '\\subparagraph{•}')]:
            self.pmb.add_action_button(box, citation_style[0], 'win.insert-symbol', [citation_style[1]])
        self.pmb.add_separator(box)
        for citation_style in [(_('Part') + '*', '\\part*{•}'), (_('Chapter')+'*', '\\chapter*{•}'), (_('Section')+'*', '\\section*{•}'), (_('Subsection')+'*', '\\subsection*{•}'), (_('Subsubsection')+'*', '\\subsubsection*{•}'), (_('Paragraph')+'*', '\\paragraph*{•}'), (_('Subparagraph')+'*', '\\subparagraph*{•}')]:
            self.pmb.add_action_button(box, citation_style[0], 'win.insert-symbol', [citation_style[1]])
        stack.add_named(box, 'sectioning')
        box.show_all()

        # list environments submenu
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, _('List Environments'))
        for list_type in [[_('Bulleted List') + ' (itemize)', 'itemize'], [_('Numbered List') + ' (enumerate)', 'enumerate'], [_('List with Bold Labels') + ' (description)', 'description']]:
            self.pmb.add_action_button(box, list_type[0], 'win.insert-before-after', ['\\begin{' + list_type[1] + '}\n\t', '\n\\end{' + list_type[1] + '}'])
        self.pmb.add_separator(box)
        self.pmb.add_action_button(box, _('List Item'), 'win.insert-symbol', ['\\item •'], keyboard_shortcut=_('Shift') + '+' + _('Ctrl') + '+I')
        stack.add_named(box, 'list_environments')
        box.show_all()

        # quotations submenu
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, _('Quotations'))
        self.pmb.add_action_button(box, _('Short Quotation') + ' (quote)', 'win.insert-before-after', ['\\begin{quote}\n\t', '\n\\end{quote}'])
        self.pmb.add_action_button(box, _('Longer Quotation') + ' (quotation)', 'win.insert-before-after', ['\\begin{quotation}\n\t', '\n\\end{quotation}'])
        self.pmb.add_action_button(box, _('Poetry Quotation') + ' (verse)', 'win.insert-before-after', ['\\begin{verse}\n\t', '\n\\end{verse}'])
        stack.add_named(box, 'quotations')
        box.show_all()

        # cross references submenu
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, _('Cross References'))
        for command in [(_('Label') + ' (\\label)', 'label'), (_('Reference') + ' (\\ref)', 'ref'), (_('Equation Reference') + ' (\\eqref)', 'eqref'), (_('Page Reference') + ' (\\pageref)', 'pageref')]:
            self.pmb.add_action_button(box, command[0], 'win.insert-symbol', ['\\' + command[1] + '{•}'])
        stack.add_named(box, 'cross_references')
        box.show_all()

        self.text_button = Gtk.MenuButton()
        self.text_button.set_image(Gtk.Image.new_from_icon_name('text-symbolic', Gtk.IconSize.MENU))
        self.text_button.set_can_focus(False)
        self.text_button.set_tooltip_text(_('Text'))
        self.text_button.get_style_context().add_class('flat')
        self.text_button.set_popover(popover)

        button_wrapper = Gtk.ToolItem()
        button_wrapper.add(self.text_button)
        self.top_icons.insert(button_wrapper, 0)

    def insert_quotes_button(self):
        popover = Gtk.PopoverMenu()
        stack = popover.get_child()

        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        for item in [(_('Primary Quotes') + ' (`` ... \'\')', ['``', '\'\'']), (_('Secondary Quotes') + ' (` ... \')', ['`', '\'']), (_('German Quotes') + ' (\\glqq ... \\grqq{})', ['\\glqq ', '\\grqq{}']), (_('German Single Quotes') + ' (\\glq ... \\grq{})', ['\\glq ', '\\grq{}']), (_('French Quotes') + ' (\\flqq ... \\frqq{})', ['\\flqq ', '\\frqq{}']), (_('French Single Quotes') + ' (\\flq ... \\frq{})', ['\\flq ', '\\frq{}']), (_('German Alt Quotes') + ' (\\frqq ... \\flqq{})', ['\\frqq ', '\\flqq{}']), (_('German Alt Single Quotes') + ' (\\frq ... \\frq{})', ['\\frq ', '\\flq{}'])]:
            self.pmb.add_action_button(box, item[0], 'win.insert-before-after', item[1])
        stack.add_named(box, 'main')
        box.show_all()

        button_wrapper = Gtk.ToolItem()
        self.quotes_button = Gtk.MenuButton()
        self.quotes_button.set_direction(Gtk.ArrowType.DOWN)
        self.quotes_button.set_image(Gtk.Image.new_from_icon_name('own-quotes-symbolic', Gtk.IconSize.MENU))
        self.quotes_button.set_popover(popover)
        self.quotes_button.set_can_focus(False)
        self.quotes_button.set_tooltip_text(_('Quotes') + ' (' + _('Ctrl') + '+")')
        self.quotes_button.get_style_context().add_class('flat')
        button_wrapper.add(self.quotes_button)
        self.quotes_button.get_popover().get_style_context().add_class('menu-own-quotes-symbolic')
        self.top_icons.insert(button_wrapper, 0)

    def insert_math_button(self):
        popover = Gtk.PopoverMenu()
        stack = popover.get_child()

        # main menu
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_action_button(box, _('Include AMS Packages'), 'win.add-packages', ['amsmath', 'amssymb', 'amsfonts', 'amsthm'])
        self.pmb.add_separator(box)
        self.pmb.add_action_button(box, _('Inline Math Section') + ' ($ ... $)', 'win.insert-before-after', ['$ ', ' $'], keyboard_shortcut=_('Shift') + '+' + _('Ctrl') + '+M')
        self.pmb.add_action_button(box, _('Display Math Section') + ' (\\[ ... \\])', 'win.insert-before-after', ['\\[ ', ' \\]'], keyboard_shortcut=_('Shift') + '+Alt' + '+M')
        self.pmb.add_menu_button(box, _('Math Environments'), 'math_environments')
        self.pmb.add_separator(box)
        self.pmb.add_action_button(box, _('Subscript') + ' (_{})', 'win.insert-before-after', ['_{', '}'], keyboard_shortcut=_('Shift') + '+' + _('Ctrl') + '+D')
        self.pmb.add_action_button(box, _('Superscript') + ' (^{})', 'win.insert-before-after', ['^{', '}'], keyboard_shortcut=_('Shift') + '+' + _('Ctrl') + '+U')
        self.pmb.add_action_button(box, _('Fraction') + ' (\\frac)', 'win.insert-symbol', ['\\frac{•}{•}'], keyboard_shortcut=_('Shift') + '+Alt' + '+F')
        self.pmb.add_action_button(box, _('Square Root') + ' (\\sqrt)', 'win.insert-before-after', ['\\sqrt{', '}'], keyboard_shortcut=_('Shift') + '+' + _('Ctrl') + '+Q')
        self.pmb.add_action_button(box, '\\left', 'win.insert-symbol', ['\\left •'], keyboard_shortcut=_('Shift') + '+' + _('Ctrl') + '+L')
        self.pmb.add_action_button(box, '\\right', 'win.insert-symbol', ['\\right •'], keyboard_shortcut=_('Shift') + '+' + _('Ctrl') + '+R')
        self.pmb.add_separator(box)
        self.pmb.add_menu_button(box, _('Math Functions'), 'math_functions')
        self.pmb.add_menu_button(box, _('Math Font Styles'), 'math_font_styles')
        self.pmb.add_menu_button(box, _('Math Stacking Symbols'), 'math_stacking_symbols')
        self.pmb.add_menu_button(box, _('Math Accents'), 'math_accents')
        self.pmb.add_menu_button(box, _('Math Spaces'), 'math_spaces')
        stack.add_named(box, 'main')
        box.show_all()

        # submenu: math environments
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, _('Math Environments'))
        for environment in ['equation', 'equation*', 'align', 'align*', 'alignat', 'alignat*', 'flalign', 'flalign*', 'gather', 'gather*', 'multline', 'multline*']:
            self.pmb.add_action_button(box, environment, 'win.insert-before-after', ['\\begin{' + environment + '}\n\t', '\n\\end{' + environment + '}'], keyboard_shortcut=(_('Shift') + '+' + _('Ctrl') + '+N' if environment == 'equation' else None))
        self.pmb.add_separator(box)
        for environment in ['cases', 'split']:
            self.pmb.add_action_button(box, environment, 'win.insert-before-after', ['\\begin{' + environment + '}\n\t', '\n\\end{' + environment + '}'])
        stack.add_named(box, 'math_environments')
        box.show_all()

        # submenu: math functions
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, _('Math Functions'))
        hbox = Gtk.HBox()
        vbox = Gtk.VBox()
        for math_function in ['arccos', 'arcsin', 'arctan', 'cos', 'cosh', 'cot', 'coth', 'csc', 'deg', 'det', 'dim', 'exp', 'gcd', 'hom', 'inf']:
            self.pmb.add_action_button(vbox, '\\' + math_function, 'win.insert-symbol', ['\\' + math_function + ' '])
        hbox.pack_start(vbox, True, True, 0)
        vbox = Gtk.VBox()
        for math_function in ['ker', 'lg', 'lim', 'liminf', 'limsup', 'ln', 'log', 'max', 'min', 'sec', 'sin', 'sinh', 'sup', 'tan', 'tanh']:
            self.pmb.add_action_button(vbox, '\\' + math_function, 'win.insert-symbol', ['\\' + math_function + ' '])
        hbox.pack_start(vbox, True, True, 0)
        box.pack_start(hbox, False, False, 0)
        stack.add_named(box, 'math_functions')
        box.show_all()

        # submenu: math font styles
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, _('Math Font Styles'))
        for command in [(_('Bold'), 'mathbf', 'menu-math-font-styles-1-symbolic'), (_('Italic'), 'mathit', 'menu-math-font-styles-2-symbolic'), (_('Roman'), 'mathrm', 'menu-math-font-styles-3-symbolic'), (_('Sans Serif'), 'mathsf', 'menu-math-font-styles-4-symbolic'), (_('Typewriter'), 'mathtt', 'menu-math-font-styles-5-symbolic'), (_('Calligraphic'), 'mathcal', 'menu-math-font-styles-6-symbolic'), (_('Blackboard Bold'), 'mathbb', 'menu-math-font-styles-7-symbolic'), (_('Fraktur'), 'mathfrak', 'menu-math-font-styles-8-symbolic')]:
            self.pmb.add_action_button(box, command[0] + ' (\\' + command[1] + ')', 'win.insert-before-after', ['\\' + command[1] + '{', '}'], icon_name=command[2])
        stack.add_named(box, 'math_font_styles')
        box.show_all()

        # submenu: math stacking symbols
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, _('Math Stacking Symbols'))
        for math_stacking_symbol in ['overline', 'underline', 'overbrace', 'underbrace', 'overleftarrow', 'overrightarrow']:
            self.pmb.add_action_button(box, '\\' + math_stacking_symbol + '{}', 'win.insert-before-after', ['\\' + math_stacking_symbol + '{', '}'])
        for math_stacking_symbol in ['stackrel', 'overset', 'underset']:
            self.pmb.add_action_button(box, '\\' + math_stacking_symbol + '{}{}', 'win.insert-before-after', ['\\' + math_stacking_symbol + '{•}{', '}'])
        stack.add_named(box, 'math_stacking_symbols')
        box.show_all()

        # submenu: math accents
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, _('Math Accents'))
        for math_accent in [('dot', 'menu-math-accents-1-symbolic'), ('ddot', 'menu-math-accents-2-symbolic'), ('vec', 'menu-math-accents-3-symbolic'), ('bar', 'menu-math-accents-4-symbolic'), ('tilde', 'menu-math-accents-5-symbolic'), ('hat', 'menu-math-accents-6-symbolic'), ('check', 'menu-math-accents-7-symbolic'), ('breve', 'menu-math-accents-8-symbolic'), ('acute', 'menu-math-accents-9-symbolic'), ('grave', 'menu-math-accents-10-symbolic')]:
            self.pmb.add_action_button(box, '\\' + math_accent[0] + '{}', 'win.insert-before-after', ['\\' + math_accent[0] + '{', '}'], icon_name=math_accent[1])
        stack.add_named(box, 'math_accents')
        box.show_all()

        # submenu: math spaces
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, _('Math Spaces'))
        for math_space in [('\\!', 'Negative'), ('\\,', 'Thin'), ('\\:', 'Medium'), ('\\;', 'Thick'), ('\\ ', 'Interword'), ('\\enspace ', 'Enspace'), ('\\quad ', 'One Quad'), ('\\qquad ', 'Two Quads')]:
            self.pmb.add_action_button(box, math_space[1], 'win.insert-symbol', [math_space[0]])
        stack.add_named(box, 'math_spaces')
        box.show_all()

        self.math_button = Gtk.MenuButton()
        self.math_button.set_image(Gtk.Image.new_from_icon_name('own-math-menu-symbolic', Gtk.IconSize.MENU))
        self.math_button.set_can_focus(False)
        self.math_button.set_tooltip_text(_('Math'))
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
        self.pmb.set_box_margin(box)
        self.pmb.add_action_button(box, _('Figure (image inside freestanding block)'), 'win.insert-symbol', ['\\begin{figure}\n\t\\begin{center}\n\t\t\\includegraphics[scale=1]{•}\n\t\t\\caption{•}\n\t\\end{center}\n\\end{figure}'])
        self.pmb.add_action_button(box, _('Inline Image'), 'win.insert-symbol', ['\\includegraphics[scale=1]{•}'])
        self.pmb.add_menu_button(box, _('Code Listing'), 'code_listing')
        stack.add_named(box, 'main')
        box.show_all()

        # code listing submenu
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, _('Code Listing'))
        self.pmb.add_action_button(box, _('Include \'listings\' Package'), 'win.add-packages', ['listings'])
        self.pmb.add_separator(box)
        for language in ['Python', 'C', 'C++', 'Java', 'Perl', 'PHP', 'Ruby', 'TeX']:
            self.pmb.add_action_button(box, language, 'win.insert-before-after', ['\\lstset{language=' + language + '}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        self.pmb.add_separator(box)
        self.pmb.add_action_button(box, _('Other Language'), 'win.insert-before-after', ['\\lstset{language=•}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        self.pmb.add_action_button(box, _('Plain Text'), 'win.insert-before-after', ['\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        stack.add_named(box, 'code_listing')
        box.show_all()

        button_wrapper = Gtk.ToolItem()
        self.insert_object_button = Gtk.MenuButton()
        self.insert_object_button.set_direction(Gtk.ArrowType.DOWN)
        self.insert_object_button.set_image(Gtk.Image.new_from_icon_name('own-insert-object-symbolic', Gtk.IconSize.MENU))
        self.insert_object_button.set_popover(popover)
        self.insert_object_button.set_can_focus(False)
        self.insert_object_button.set_tooltip_text(_('Objects'))
        self.insert_object_button.get_style_context().add_class('flat')
        button_wrapper.add(self.insert_object_button)
        self.insert_object_button.get_popover().get_style_context().add_class('menu-insert-object-symbolic')
        self.top_icons.insert(button_wrapper, 0)



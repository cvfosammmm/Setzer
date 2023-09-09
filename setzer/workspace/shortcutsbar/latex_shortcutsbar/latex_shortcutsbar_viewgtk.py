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
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gio

from setzer.helpers.popover_menu_builder import MenuBuilder


class LaTeXShortcutsbar(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.get_style_context().add_class('shortcutsbar')
        self.set_can_focus(False)

        self.current_popover = None # popover being processed
        self.current_page = 'main' # page being processed

        self.top_icons = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.right_icons = Gtk.Box()
        self.right_icons.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.center_icons = Gtk.CenterBox()
        self.center_icons.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.center_icons.set_hexpand(True)

        self.populate_top_toolbar()
        self.populate_right_toolbar()

        self.append(self.top_icons)
        self.append(self.center_icons)
        self.append(self.right_icons)

    def populate_right_toolbar(self):
        self.button_search = Gtk.ToggleButton()
        self.button_search.set_icon_name('edit-find-symbolic')
        self.button_search.set_tooltip_text(_('Find') + ' (' + _('Ctrl') + '+F)')
        self.button_search.get_style_context().add_class('flat')
        self.button_search.get_style_context().add_class('scbar')
        self.right_icons.append(self.button_search)

        self.button_replace = Gtk.ToggleButton()
        self.button_replace.set_icon_name('edit-find-replace-symbolic')
        self.button_replace.set_tooltip_text(_('Find and Replace') + ' (' + _('Ctrl') + '+H)')
        self.button_replace.get_style_context().add_class('flat')
        self.button_replace.get_style_context().add_class('scbar')
        self.right_icons.append(self.button_replace)

        self.button_more = Gtk.MenuButton()
        self.button_more.set_icon_name('view-more-symbolic')
        self.button_more.get_style_context().add_class('flat')
        self.button_more.get_style_context().add_class('scbar')
        self.button_more.set_tooltip_text(_('Document'))
        self.right_icons.append(self.button_more)

        self.button_build_log = Gtk.ToggleButton()
        self.button_build_log.set_icon_name('build-log-symbolic')
        self.button_build_log.set_tooltip_text(_('Build log') + ' (F8)')
        self.button_build_log.get_style_context().add_class('flat')
        self.button_build_log.get_style_context().add_class('scbar')
        self.right_icons.append(self.button_build_log)

    def populate_top_toolbar(self):
        self.italic_button = Gtk.Button()
        self.italic_button.set_icon_name('format-text-italic-symbolic')
        self.italic_button.set_action_name('win.insert-before-after')
        self.italic_button.set_action_target_value(GLib.Variant('as', ['\\textit{', '}']))
        self.italic_button.get_style_context().add_class('flat')
        self.italic_button.get_style_context().add_class('scbar')
        self.italic_button.set_tooltip_text(_('Italic') + ' (' + _('Ctrl') + '+I)')
        self.top_icons.prepend(self.italic_button)

        self.bold_button = Gtk.Button()
        self.bold_button.set_icon_name('format-text-bold-symbolic')
        self.bold_button.set_action_name('win.insert-before-after')
        self.bold_button.set_action_target_value(GLib.Variant('as', ['\\textbf{', '}']))
        self.bold_button.get_style_context().add_class('flat')
        self.bold_button.get_style_context().add_class('scbar')
        self.bold_button.set_tooltip_text(_('Bold') + ' (' + _('Ctrl') + '+B)')
        self.top_icons.prepend(self.bold_button)

        self.insert_quotes_button()

        self.insert_math_button()
        self.insert_text_button()
        self.insert_object_button()

        self.insert_bibliography_button()
        self.insert_beamer_button()
        self.insert_document_button()

        self.insert_wizard_button()

    def insert_wizard_button(self):
        self.wizard_button = Gtk.Button()
        self.wizard_button.get_style_context().add_class('flat')
        self.wizard_button.get_style_context().add_class('scbar')
        self.wizard_button.set_tooltip_text(_('Create a template document'))
        self.wizard_button.set_can_focus(False)

        icon_widget = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        icon = Gtk.Image.new_from_icon_name('own-wizard-symbolic')
        icon.set_margin_start(4)
        icon_widget.append(icon)
        label = Gtk.Label.new(_('New Document Wizard'))
        label.set_margin_start(6)
        label.set_margin_end(4)
        self.wizard_button_revealer = Gtk.Revealer()
        self.wizard_button_revealer.set_child(label)
        self.wizard_button_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
        self.wizard_button_revealer.set_reveal_child(True)
        icon_widget.append(self.wizard_button_revealer)

        self.wizard_button.set_child(icon_widget)
        self.wizard_button.set_action_name('win.show-document-wizard')

        self.top_icons.prepend(self.wizard_button)

    def insert_document_button(self):
        self.document_button = Gtk.MenuButton()
        self.document_button.set_icon_name('application-x-addon-symbolic')
        self.document_button.get_style_context().add_class('flat')
        self.document_button.get_style_context().add_class('scbar')
        self.document_button.set_tooltip_text(_('Document'))
        self.top_icons.prepend(self.document_button)

        self.create_popover()
        self.add_insert_symbol_item('\\documentclass', ['\\documentclass[•]{•}'])
        self.add_action_button(_('Add / Remove Packages') + '...', 'win.add-remove-packages-dialog')
        self.add_menu_button(_('Document Info'), 'document_info')
        MenuBuilder.add_separator(self.current_popover)
        self.add_before_after_item(_('Document Environment'), ['\\begin{document}\n\t', '\n\\end{document}'])
        self.add_insert_symbol_item(_('Show Title') + ' (\\maketitle)', ['\\maketitle'])
        self.add_insert_symbol_item(_('Table of Contents'), ['\\tableofcontents'])
        MenuBuilder.add_separator(self.current_popover)
        self.add_action_button(_('Include LaTeX File') + ' (\\input)...', 'win.include-latex-file')

        # document info submenu
        self.add_page('document_info', _('Document Info'))
        self.add_insert_symbol_item(_('Author'), ['\\author{•}'])
        self.add_insert_symbol_item(_('Title'), ['\\title{•}'])
        self.add_insert_symbol_item(_('Date'), ['\\date{•}'])
        self.add_insert_symbol_item(_('Date Today'), ['\\date{\\today}'])

        self.document_button.set_popover(self.current_popover)

    def insert_beamer_button(self):
        self.beamer_button = Gtk.MenuButton()
        self.beamer_button.set_icon_name('view-list-bullet-symbolic')
        self.beamer_button.set_tooltip_text(_('Beamer'))
        self.beamer_button.get_style_context().add_class('flat')
        self.beamer_button.get_style_context().add_class('scbar')
        self.top_icons.prepend(self.beamer_button)

        self.create_popover()
        self.add_action_button('\\usetheme', 'win.insert-after-packages', GLib.Variant('as', ['\\usetheme{•}']))
        self.add_action_button(_('Hide Navigation'), 'win.insert-after-packages', GLib.Variant('as', ['\\beamertemplatenavigationsymbolsempty']))
        MenuBuilder.add_separator(self.current_popover)
        self.add_insert_symbol_item(_('Title Page'), ['\\begin{frame}\n\t\\titlepage\n\\end{frame}'])
        self.add_insert_symbol_item(_('Table of Contents'), ['\\begin{frame}\n\t\\tableofcontents\n\\end{frame}'])
        MenuBuilder.add_separator(self.current_popover)
        self.add_before_after_item(_('Frame'), ['\\begin{frame}\n\t', '\n\\end{frame}'])
        self.add_before_after_item(_('Frame with Title'), ['\\begin{frame}\n\t\\frametitle{•}\n\n\t', '\n\\end{frame}'])
        self.add_before_after_item(_('\\frametitle'), ['\\frametitle{', '}'])

        self.beamer_button.set_popover(self.current_popover)

    def insert_bibliography_button(self):
        self.bibliography_button = Gtk.MenuButton()
        self.bibliography_button.set_icon_name('view-dual-symbolic')
        self.bibliography_button.set_tooltip_text(_('Bibliography'))
        self.bibliography_button.get_style_context().add_class('flat')
        self.bibliography_button.get_style_context().add_class('scbar')
        self.top_icons.prepend(self.bibliography_button)

        self.create_popover()
        self.add_action_button(_('Include BibTeX File') + '...', 'win.include-bibtex-file')
        self.add_action_button(_('Include \'natbib\' Package'), 'win.add-packages', GLib.Variant('as', ['natbib']))
        MenuBuilder.add_separator(self.current_popover)
        self.add_insert_symbol_item(_('Citation'), ['\\cite{•}'])
        self.add_insert_symbol_item(_('Citation with Page Number'), ['\\cite[•]{•}'])
        self.add_menu_button(_('Natbib Citations'), 'natbib_citations')
        self.add_action_button(_('Include non-cited BibTeX Entries with \'\\nocite\''), 'win.insert-before-document-end', GLib.Variant('as', ['\\nocite{*}']))

        # natbib submenu
        self.add_page('natbib_citations', _('Natbib Citations'))
        self.add_insert_symbol_item(_('Abbreviated'), ['\\citet{•}'])
        self.add_insert_symbol_item(_('Abbreviated with Brackets'), ['\\citep{•}'])
        self.add_insert_symbol_item(_('Detailed'), ['\\citet*{•}'])
        self.add_insert_symbol_item(_('Detailed with Brackets'), ['\\citep*{•}'])
        self.add_insert_symbol_item(_('Alternative 1'), ['\\citealt{•}'])
        self.add_insert_symbol_item(_('Alternative 2'), ['\\citealp{•}'])
        MenuBuilder.add_separator(self.current_popover, 'natbib_citations')
        self.add_insert_symbol_item(_('Cite Author'), ['\\citeauthor{•}'])
        self.add_insert_symbol_item(_('Cite Author Detailed'), ['\\citeauthor*{•}'])
        self.add_insert_symbol_item(_('Cite Year'), ['\\citeyear{•}'])
        self.add_insert_symbol_item(_('Cite Year with Brackets'), ['\\citeyearpar{•}'])

        self.bibliography_button.set_popover(self.current_popover)

    def insert_text_button(self):
        self.text_button = Gtk.MenuButton()
        self.text_button.set_icon_name('text-symbolic')
        self.text_button.set_tooltip_text(_('Text'))
        self.text_button.get_style_context().add_class('flat')
        self.text_button.get_style_context().add_class('scbar')
        self.top_icons.prepend(self.text_button)

        self.create_popover()
        self.add_menu_button(_('Font Styles'), 'font_styles')
        self.add_menu_button(_('Font Sizes'), 'font_sizes')
        self.add_menu_button(_('Alignment'), 'text_alignment')
        self.add_menu_button(_('Vertical Spacing'), 'vertical_spacing')
        self.add_menu_button(_('International Accents'), 'international_accents')
        MenuBuilder.add_separator(self.current_popover)
        self.add_menu_button(_('Sectioning'), 'sectioning')
        MenuBuilder.add_separator(self.current_popover)
        self.add_before_after_item(_('Environment'), ['\\begin{•}\n\t', '\n\\end{•}'], shortcut=_('Ctrl') + '+E')
        self.add_before_after_item(_('Verbatim Environment'), ['\\begin{verbatim}\n\t', '\n\\end{verbatim}'])
        self.add_menu_button(_('List Environments'), 'list_environments')
        self.add_menu_button(_('Quotations'), 'quotations')
        MenuBuilder.add_separator(self.current_popover)
        self.add_menu_button(_('Cross References'), 'cross_references')
        self.add_before_after_item(_('Footnote'), ['\\footnote{', '}'])

        # font styles submenu
        self.add_page('font_styles', _('Font Styles'))
        self.add_before_after_item(_('Bold') + ' (\\textbf)', ['\\textbf{', '}'], icon='format-text-bold-symbolic', shortcut=_('Ctrl') + '+B')
        self.add_before_after_item(_('Italic') + ' (\\textit)', ['\\textit{', '}'], icon='format-text-italic-symbolic', shortcut=_('Ctrl') + '+I')
        self.add_before_after_item(_('Underline') + ' (\\underline)', ['\\underline{', '}'], icon='format-text-underline-symbolic', shortcut=_('Ctrl') + '+U')
        self.add_before_after_item(_('Sans Serif') + ' (\\textsf)', ['\\textsf{', '}'], icon='placeholder')
        self.add_before_after_item(_('Typewriter') + ' (\\texttt)', ['\\texttt{', '}'], icon='placeholder', shortcut=_('Shift') + '+' + _('Ctrl') + '+T')
        self.add_before_after_item(_('Small Caps') + ' (\\textsc)', ['\\textsc{', '}'], icon='placeholder')
        self.add_before_after_item(_('Slanted') + ' (\\textsl)', ['\\textsl{', '}'], icon='placeholder')
        self.add_before_after_item(_('Emphasis') + ' (\\emph)', ['\\emph{', '}'], icon='placeholder', shortcut=_('Shift') + '+' + _('Ctrl') + '+E')

        # font sizes submenu
        self.add_page('font_sizes', _('Font Sizes'))
        self.add_before_after_item('tiny', ['{\\tiny ', '}'])
        self.add_before_after_item('scriptsize', ['{\\scriptsize ', '}'])
        self.add_before_after_item('footnotesize', ['{\\footnotesize ', '}'])
        self.add_before_after_item('small', ['{\\small ', '}'])
        self.add_before_after_item('normalsize', ['{\\normalsize ', '}'])
        self.add_before_after_item('large', ['{\\large ', '}'])
        self.add_before_after_item('Large', ['{\\Large ', '}'])
        self.add_before_after_item('LARGE', ['{\\LARGE ', '}'])
        self.add_before_after_item('huge', ['{\\huge ', '}'])
        self.add_before_after_item('Huge', ['{\\Huge ', '}'])

        # text alignment submenu
        self.add_page('text_alignment', _('Alignment'))
        self.add_before_after_item(_('Centered'), ['\\begin{center}\n\t', '\n\\end{center}'], icon='format-justify-center-symbolic')
        self.add_before_after_item(_('Left-aligned'), ['\\begin{flushleft}\n\t', '\n\\end{flushleft}'], icon='format-justify-left-symbolic')
        self.add_before_after_item(_('Right-aligned'), ['\\begin{flushright}\n\t', '\n\\end{flushright}'], icon='format-justify-right-symbolic')

        # vertical spacing submenu
        self.add_page('vertical_spacing', _('Vertical Spacing'))
        self.add_insert_symbol_item('\\newpage', ['\\newpage'])
        self.add_insert_symbol_item('\\linebreak', ['\\linebreak'])
        self.add_insert_symbol_item('\\pagebreak', ['\\pagebreak'])
        self.add_insert_symbol_item('\\bigskip', ['\\bigskip'])
        self.add_insert_symbol_item('\\medskip', ['\\medskip'])
        self.add_insert_symbol_item('\\smallskip', ['\\smallskip'])
        self.add_insert_symbol_item('\\vspace', ['\\vspace{•}'])
        self.add_insert_symbol_item(_('New Line')+ ' (\\\\)', ['\\\\\n'], shortcut=_('Ctrl') + '+Return')

        # international accents submenu
        self.add_page('international_accents', _('International Accents'))
        self.add_before_after_item('\\\'{}', ['\\\'{', '}'], icon='menu-accents-1-symbolic')
        self.add_before_after_item('\\`{}', ['\\`{', '}'], icon='menu-accents-2-symbolic')
        self.add_before_after_item('\\^{}', ['\\^{', '}'], icon='menu-accents-3-symbolic')
        self.add_before_after_item('\\"{}', ['\\"{', '}'], icon='menu-accents-4-symbolic')
        self.add_before_after_item('\\~{}', ['\\~{', '}'], icon='menu-accents-5-symbolic')
        self.add_before_after_item('\\={}', ['\\={', '}'], icon='menu-accents-6-symbolic')
        self.add_before_after_item('\\.{}', ['\\.{', '}'], icon='menu-accents-7-symbolic')
        self.add_before_after_item('\\v{}', ['\\v{', '}'], icon='menu-accents-8-symbolic')
        self.add_before_after_item('\\u{}', ['\\u{', '}'], icon='menu-accents-9-symbolic')
        self.add_before_after_item('\\H{}', ['\\H{', '}'], icon='menu-accents-10-symbolic')

        # sectioning submenu
        self.add_page('sectioning', _('Sectioning'))
        self.add_insert_symbol_item(_('Part'), ['\\part{•}'])
        self.add_insert_symbol_item(_('Chapter'), ['\\chapter{•}'])
        self.add_insert_symbol_item(_('Section'), ['\\section{•}'])
        self.add_insert_symbol_item(_('Subsection'), ['\\subsection{•}'])
        self.add_insert_symbol_item(_('Subsubsection'), ['\\subsubsection{•}'])
        self.add_insert_symbol_item(_('Paragraph'), ['\\paragraph{•}'])
        self.add_insert_symbol_item(_('Subparagraph'), ['\\subparagraph{•}'])
        MenuBuilder.add_separator(self.current_popover, 'sectioning')
        self.add_insert_symbol_item(_('Part') + '*', ['\\part*{•}'])
        self.add_insert_symbol_item(_('Chapter')+'*', ['\\chapter*{•}'])
        self.add_insert_symbol_item(_('Section')+'*', ['\\section*{•}'])
        self.add_insert_symbol_item(_('Subsection')+'*', ['\\subsection*{•}'])
        self.add_insert_symbol_item(_('Subsubsection')+'*', ['\\subsubsection*{•}'])
        self.add_insert_symbol_item(_('Paragraph')+'*', ['\\paragraph*{•}'])
        self.add_insert_symbol_item(_('Subparagraph')+'*', ['\\subparagraph*{•}'])

        # list environments submenu
        self.add_page('list_environments', _('List Environments'))
        self.add_before_after_item(_('Bulleted List') + ' (itemize)', ['\\begin{itemize}\n\t', '\n\\end{itemize}'])
        self.add_before_after_item(_('Numbered List') + ' (enumerate)', ['\\begin{enumerate}\n\t', '\n\\end{enumerate}'])
        self.add_before_after_item(_('List with Bold Labels') + ' (description)', ['\\begin{description}\n\t', '\n\\end{description}'])
        MenuBuilder.add_separator(self.current_popover, 'list_environments')
        self.add_insert_symbol_item(_('List Item'), ['\\item •'], shortcut=_('Shift') + '+' + _('Ctrl') + '+I')

        # quotations submenu
        self.add_page('quotations', _('Quotations'))
        self.add_before_after_item(_('Short Quotation') + ' (quote)', ['\\begin{quote}\n\t', '\n\\end{quote}'])
        self.add_before_after_item(_('Longer Quotation') + ' (quotation)', ['\\begin{quotation}\n\t', '\n\\end{quotation}'])
        self.add_before_after_item(_('Poetry Quotation') + ' (verse)', ['\\begin{verse}\n\t', '\n\\end{verse}'])

        # cross references submenu
        self.add_page('cross_references', _('Cross References'))
        self.add_insert_symbol_item(_('Label') + ' (\\label)', ['\\label{•}'])
        self.add_insert_symbol_item(_('Reference') + ' (\\ref)', ['\\ref{•}'])
        self.add_insert_symbol_item(_('Equation Reference') + ' (\\eqref)', ['\\eqref{•}'])
        self.add_insert_symbol_item(_('Page Reference') + ' (\\pageref)', ['\\pageref{•}'])

        self.text_button.set_popover(self.current_popover)

    def insert_quotes_button(self):
        self.quotes_button = Gtk.MenuButton()
        self.quotes_button.set_direction(Gtk.ArrowType.DOWN)
        self.quotes_button.set_icon_name('own-quotes-symbolic')
        self.quotes_button.set_tooltip_text(_('Quotes') + ' (' + _('Ctrl') + '+")')
        self.quotes_button.get_style_context().add_class('flat')
        self.quotes_button.get_style_context().add_class('scbar')
        self.top_icons.prepend(self.quotes_button)

        self.create_popover()
        self.current_popover.get_style_context().add_class('menu-own-quotes-symbolic')
        self.add_before_after_item(_('Primary Quotes') + ' (`` ... \'\')', ['``', '\'\''])
        self.add_before_after_item(_('Secondary Quotes') + ' (` ... \')', ['`', '\''])
        self.add_before_after_item(_('German Quotes') + ' (\\glqq ... \\grqq{})', ['\\glqq ', '\\grqq{}'])
        self.add_before_after_item(_('German Single Quotes') + ' (\\glq ... \\grq{})', ['\\glq ', '\\grq{}'])
        self.add_before_after_item(_('French Quotes') + ' (\\flqq ... \\frqq{})', ['\\flqq ', '\\frqq{}'])
        self.add_before_after_item(_('French Single Quotes') + ' (\\flq ... \\frq{})', ['\\flq ', '\\frq{}'])
        self.add_before_after_item(_('German Alt Quotes') + ' (\\frqq ... \\flqq{})', ['\\frqq ', '\\flqq{}'])
        self.add_before_after_item(_('German Alt Single Quotes') + ' (\\frq ... \\frq{})', ['\\frq ', '\\flq{}'])

        self.quotes_button.set_popover(self.current_popover)

    def insert_math_button(self):
        self.math_button = Gtk.MenuButton()
        self.math_button.set_icon_name('own-math-menu-symbolic')
        self.math_button.set_tooltip_text(_('Math'))
        self.math_button.get_style_context().add_class('flat')
        self.math_button.get_style_context().add_class('scbar')
        self.top_icons.prepend(self.math_button)

        self.create_popover()
        self.add_action_button(_('Include AMS Packages'), 'win.add-packages', GLib.Variant('as', ['amsmath', 'amssymb', 'amsfonts', 'amsthm']))
        MenuBuilder.add_separator(self.current_popover)
        self.add_before_after_item(_('Inline Math Section') + ' ($ ... $)', ['$ ', ' $'], shortcut=_('Ctrl') + '+M')
        self.add_before_after_item(_('Display Math Section') + ' (\\[ ... \\])', ['\\[ ', ' \\]'], shortcut=_('Shift') + '+Ctrl' + '+M')
        self.add_menu_button(_('Math Environments'), 'math_environments')
        MenuBuilder.add_separator(self.current_popover)
        self.add_before_after_item(_('Subscript') + ' (_{})', ['_{', '}'], shortcut=_('Shift') + '+' + _('Ctrl') + '+D')
        self.add_before_after_item(_('Superscript') + ' (^{})', ['^{', '}'], shortcut=_('Shift') + '+' + _('Ctrl') + '+U')
        self.add_insert_symbol_item(_('Fraction') + ' (\\frac)', ['\\frac{•}{•}'], shortcut=_('Shift') + '+Alt' + '+F')
        self.add_before_after_item(_('Square Root') + ' (\\sqrt)', ['\\sqrt{', '}'])
        self.add_insert_symbol_item('\\left', ['\\left •'], shortcut=_('Shift') + '+' + _('Ctrl') + '+L')
        self.add_insert_symbol_item('\\right', ['\\right •'], shortcut=_('Shift') + '+' + _('Ctrl') + '+R')
        MenuBuilder.add_separator(self.current_popover)
        self.add_menu_button(_('Math Functions'), 'math_functions')
        self.add_menu_button(_('Math Font Styles'), 'math_font_styles')
        self.add_menu_button(_('Math Stacking Symbols'), 'math_stacking_symbols')
        self.add_menu_button(_('Math Accents'), 'math_accents')
        self.add_menu_button(_('Math Spaces'), 'math_spaces')

        # submenu: math environments
        self.add_page('math_environments', _('Math Environments'))
        self.add_before_after_item('equation', ['\\begin{equation}\n\t', '\n\\end{equation}'], shortcut=_('Shift') + '+' + _('Ctrl') + '+N')
        self.add_before_after_item('equation*', ['\\begin{equation*}\n\t', '\n\\end{equation*}'])
        self.add_before_after_item('align', ['\\begin{align}\n\t', '\n\\end{align}'])
        self.add_before_after_item('align*', ['\\begin{align*}\n\t', '\n\\end{align*}'])
        self.add_before_after_item('alignat', ['\\begin{alignat}\n\t', '\n\\end{alignat}'])
        self.add_before_after_item('alignat*', ['\\begin{alignat*}\n\t', '\n\\end{alignat*}'])
        self.add_before_after_item('flalign', ['\\begin{flalign}\n\t', '\n\\end{flalign}'])
        self.add_before_after_item('flalign*', ['\\begin{flalign*}\n\t', '\n\\end{flalign*}'])
        self.add_before_after_item('gather', ['\\begin{gather}\n\t', '\n\\end{gather}'])
        self.add_before_after_item('gather*', ['\\begin{gather*}\n\t', '\n\\end{gather*}'])
        self.add_before_after_item('multline', ['\\begin{multline}\n\t', '\n\\end{multline}'])
        self.add_before_after_item('multline*', ['\\begin{multline*}\n\t', '\n\\end{multline*}'])

        # submenu: math functions
        self.add_page('math_functions', _('Math Functions'))
        hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        vbox.set_hexpand(True)
        for math_function in ['arccos', 'arcsin', 'arctan', 'cos', 'cosh', 'cot', 'coth', 'csc', 'deg', 'det', 'dim', 'exp', 'gcd', 'hom', 'inf']:
            button = MenuBuilder.create_button('\\' + math_function)
            button.set_action_name('win.insert-symbol')
            button.set_action_target_value(GLib.Variant('as', ['\\' + math_function + ' ']))
            button.connect('clicked', self.on_menu_button_click, self.current_popover)
            vbox.append(button)
        hbox.append(vbox)
        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        vbox.set_hexpand(True)
        for math_function in ['ker', 'lg', 'lim', 'liminf', 'limsup', 'ln', 'log', 'max', 'min', 'sec', 'sin', 'sinh', 'sup', 'tan', 'tanh']:
            button = MenuBuilder.create_button('\\' + math_function)
            button.set_action_name('win.insert-symbol')
            button.set_action_target_value(GLib.Variant('as', ['\\' + math_function + ' ']))
            button.connect('clicked', self.on_menu_button_click, self.current_popover)
            vbox.append(button)
        hbox.append(vbox)
        MenuBuilder.add_widget(self.current_popover, hbox, self.current_pagename)

        # submenu: math font styles
        self.add_page('math_font_styles', _('Math Font Styles'))
        self.add_before_after_item(_('Bold') + ' (\\mathbf)', ['\\mathbf{', '}'], icon='menu-math-font-styles-1-symbolic')
        self.add_before_after_item(_('Italic') + ' (\\mathit)', ['\\mathit{', '}'], icon='menu-math-font-styles-2-symbolic')
        self.add_before_after_item(_('Roman') + ' (\\mathrm)', ['\\mathrm{', '}'], icon='menu-math-font-styles-3-symbolic')
        self.add_before_after_item(_('Sans Serif') + ' (\\mathsf)', ['\\mathsf{', '}'], icon='menu-math-font-styles-4-symbolic')
        self.add_before_after_item(_('Typewriter') + ' (\\mathtt)', ['\\mathtt{', '}'], icon='menu-math-font-styles-5-symbolic')
        self.add_before_after_item(_('Calligraphic') + ' (\\mathcal)', ['\\mathcal{', '}'], icon='menu-math-font-styles-6-symbolic')
        self.add_before_after_item(_('Blackboard Bold') + ' (\\mathbb)', ['\\mathbb{', '}'], icon='menu-math-font-styles-7-symbolic')
        self.add_before_after_item(_('Fraktur') + ' (\\mathfrak)', ['\\mathfrak{', '}'], icon='menu-math-font-styles-8-symbolic')

        # submenu: math stacking symbols
        self.add_page('math_stacking_symbols', _('Math Stacking Symbols'))
        self.add_before_after_item('\\overline{}', ['\\overline{', '}'])
        self.add_before_after_item('\\underline{}', ['\\underline{', '}'])
        self.add_before_after_item('\\overbrace{}', ['\\overbrace{', '}'])
        self.add_before_after_item('\\underbrace{}', ['\\underbrace{', '}'])
        self.add_before_after_item('\\overleftarrow{}', ['\\overleftarrow{', '}'])
        self.add_before_after_item('\\overrightarrow{}', ['\\overrightarrow{', '}'])
        self.add_before_after_item('\\stackrel{}{}', ['\\stackrel{•}{', '}'])
        self.add_before_after_item('\\overset{}{}', ['\\overset{•}{', '}'])
        self.add_before_after_item('\\underset{}{}', ['\\underset{•}{', '}'])
        MenuBuilder.add_separator(self.current_popover, 'math_stacking_symbols')
        self.add_before_after_item('cases', ['\\begin{cases}\n\t', '\n\\end{cases}'])
        self.add_before_after_item('split', ['\\begin{split}\n\t', '\n\\end{split}'])

        # submenu: math accents
        self.add_page('math_accents', _('Math Accents'))
        self.add_before_after_item('\\dot{}', ['\\dot{', '}'], icon='menu-math-accents-1-symbolic')
        self.add_before_after_item('\\ddot{}', ['\\ddot{', '}'], icon='menu-math-accents-2-symbolic')
        self.add_before_after_item('\\vec{}', ['\\vec{', '}'], icon='menu-math-accents-3-symbolic')
        self.add_before_after_item('\\bar{}', ['\\bar{', '}'], icon='menu-math-accents-4-symbolic')
        self.add_before_after_item('\\tilde{}', ['\\tilde{', '}'], icon='menu-math-accents-5-symbolic')
        self.add_before_after_item('\\hat{}', ['\\hat{', '}'], icon='menu-math-accents-6-symbolic')
        self.add_before_after_item('\\check{}', ['\\check{', '}'], icon='menu-math-accents-7-symbolic')
        self.add_before_after_item('\\breve{}', ['\\breve{', '}'], icon='menu-math-accents-8-symbolic')
        self.add_before_after_item('\\acute{}', ['\\acute{', '}'], icon='menu-math-accents-9-symbolic')
        self.add_before_after_item('\\grave{}', ['\\grave{', '}'], icon='menu-math-accents-10-symbolic')

        # submenu: math spaces
        self.add_page('math_spaces', _('Math Spaces'))
        self.add_insert_symbol_item('Negative', ['\\!'])
        self.add_insert_symbol_item('Thin', ['\\,'])
        self.add_insert_symbol_item('Medium', ['\\:'])
        self.add_insert_symbol_item('Thick', ['\\;'])
        self.add_insert_symbol_item('Interword', ['\\ '])
        self.add_insert_symbol_item('Enspace', ['\\enspace '])
        self.add_insert_symbol_item('One Quad', ['\\quad '])
        self.add_insert_symbol_item('Two Quads', ['\\qquad '])

        self.math_button.set_popover(self.current_popover)

    def insert_object_button(self):
        self.insert_object_button = Gtk.MenuButton()
        self.insert_object_button.set_direction(Gtk.ArrowType.DOWN)
        self.insert_object_button.set_icon_name('own-insert-object-symbolic')
        self.insert_object_button.set_tooltip_text(_('Objects'))
        self.insert_object_button.get_style_context().add_class('flat')
        self.insert_object_button.get_style_context().add_class('scbar')
        self.top_icons.prepend(self.insert_object_button)

        self.create_popover()
        self.add_insert_symbol_item(_('Figure (image inside freestanding block)'), ['\\begin{figure}\n\t\\begin{center}\n\t\t\\includegraphics[scale=1]{•}\n\t\t\\caption{•}\n\t\\end{center}\n\\end{figure}'])
        self.add_insert_symbol_item(_('Inline Image'), ['\\includegraphics[scale=1]{•}'])
        self.add_menu_button(_('Code Listing'), 'code_listing')
        MenuBuilder.add_separator(self.current_popover)
        self.add_before_after_item(_('Url (\\url)'), ['\\url{', '}'])
        self.add_before_after_item(_('Hyperlink (\\href)'), ['\\href{•}{', '}'])

        # code listing submenu
        self.add_page('code_listing', _('Code Listing'))
        self.add_action_button(_('Include \'listings\' Package'), 'win.add-packages', GLib.Variant('as', ['listings']))
        MenuBuilder.add_separator(self.current_popover, 'code_listing')
        self.add_before_after_item('Python', ['\\lstset{language=Python}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        self.add_before_after_item('C', ['\\lstset{language=C}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        self.add_before_after_item('C++', ['\\lstset{language=C++}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        self.add_before_after_item('Java', ['\\lstset{language=Java}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        self.add_before_after_item('Perl', ['\\lstset{language=Perl}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        self.add_before_after_item('PHP', ['\\lstset{language=PHP}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        self.add_before_after_item('Ruby', ['\\lstset{language=Ruby}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        self.add_before_after_item('TeX', ['\\lstset{language=TeX}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        MenuBuilder.add_separator(self.current_popover, 'code_listing')
        self.add_before_after_item(_('Other Language'), ['\\lstset{language=•}\n\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])
        self.add_before_after_item(_('Plain Text'), ['\\begin{lstlisting}\n\t', '\n\\end{lstlisting}'])

        self.insert_object_button.set_popover(self.current_popover)

    def create_popover(self):
        self.current_popover = MenuBuilder.create_menu()
        self.current_pagename = 'main'

    def add_page(self, pagename, label):
        self.current_pagename = pagename
        MenuBuilder.add_page(self.current_popover, pagename, label)

    def add_insert_symbol_item(self, title, command, icon=None, shortcut=None):
        button = MenuBuilder.create_button(title, icon_name=icon, shortcut=shortcut)
        button.set_action_name('win.insert-symbol')
        button.set_action_target_value(GLib.Variant('as', command))
        button.connect('clicked', self.on_menu_button_click, self.current_popover)
        MenuBuilder.add_widget(self.current_popover, button, self.current_pagename)

    def add_before_after_item(self, title, commands, icon=None, shortcut=None):
        button = MenuBuilder.create_button(title, icon_name=icon, shortcut=shortcut)
        button.set_action_name('win.insert-before-after')
        button.set_action_target_value(GLib.Variant('as', commands))
        button.connect('clicked', self.on_menu_button_click, self.current_popover)
        MenuBuilder.add_widget(self.current_popover, button, self.current_pagename)

    def add_menu_button(self, title, menu_name):
        button = MenuBuilder.create_menu_button(title)
        button.connect('clicked', self.current_popover.show_page, menu_name, Gtk.StackTransitionType.SLIDE_RIGHT)
        MenuBuilder.add_widget(self.current_popover, button)

    def add_action_button(self, title, action_name, parameter=None):
        button = MenuBuilder.create_button(title)
        button.set_action_name(action_name)
        if parameter != None:
            button.set_action_target_value(parameter)
        button.connect('clicked', self.on_menu_button_click, self.current_popover)
        MenuBuilder.add_widget(self.current_popover, button, self.current_pagename)

    def on_menu_button_click(self, button, popover):
        popover.popdown()



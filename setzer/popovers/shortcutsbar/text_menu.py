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

from setzer.popovers.helpers.popover_menu_builder import MenuBuilder
from setzer.popovers.helpers.popover import Popover


class TextMenu(object):

    def __init__(self, popover_manager):
        self.view = TextMenuView(popover_manager)


class TextMenuView(Popover):

    def __init__(self, popover_manager):
        Popover.__init__(self, popover_manager)

        self.set_width(288)

        self.add_menu_button(_('Font Styles'), 'font_styles')
        self.add_menu_button(_('Font Sizes'), 'font_sizes')
        self.add_menu_button(_('Alignment'), 'text_alignment')
        self.add_menu_button(_('Vertical Spacing'), 'vertical_spacing')
        self.add_menu_button(_('International Accents'), 'international_accents')
        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
        self.add_menu_button(_('Sectioning'), 'sectioning')
        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
        self.add_before_after_item('main', _('Environment'), ['\\begin{•}\n\t', '\n\\end{•}'], shortcut=_('Ctrl') + '+E')
        self.add_before_after_item('main', _('Verbatim Environment'), ['\\begin{verbatim}\n\t', '\n\\end{verbatim}'])
        self.add_menu_button(_('List Environments'), 'list_environments')
        self.add_menu_button(_('Quotations'), 'quotations')
        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))
        self.add_menu_button(_('Cross References'), 'cross_references')
        self.add_before_after_item('main', _('Footnote'), ['\\footnote{', '}'])

        # font styles submenu
        self.add_page('font_styles', _('Font Styles'))
        self.add_before_after_item('font_styles', _('Bold') + ' (\\textbf)', ['\\textbf{', '}'], icon='format-text-bold-symbolic', shortcut=_('Ctrl') + '+B')
        self.add_before_after_item('font_styles', _('Italic') + ' (\\textit)', ['\\textit{', '}'], icon='format-text-italic-symbolic', shortcut=_('Ctrl') + '+I')
        self.add_before_after_item('font_styles', _('Underline') + ' (\\underline)', ['\\underline{', '}'], icon='format-text-underline-symbolic', shortcut=_('Ctrl') + '+U')
        self.add_before_after_item('font_styles', _('Sans Serif') + ' (\\textsf)', ['\\textsf{', '}'], icon='placeholder')
        self.add_before_after_item('font_styles', _('Typewriter') + ' (\\texttt)', ['\\texttt{', '}'], icon='placeholder', shortcut=_('Shift') + '+' + _('Ctrl') + '+T')
        self.add_before_after_item('font_styles', _('Small Caps') + ' (\\textsc)', ['\\textsc{', '}'], icon='placeholder')
        self.add_before_after_item('font_styles', _('Slanted') + ' (\\textsl)', ['\\textsl{', '}'], icon='placeholder')
        self.add_before_after_item('font_styles', _('Emphasis') + ' (\\emph)', ['\\emph{', '}'], icon='placeholder', shortcut=_('Shift') + '+' + _('Ctrl') + '+E')

        # font sizes submenu
        self.add_page('font_sizes', _('Font Sizes'))
        self.add_before_after_item('font_sizes', 'tiny', ['{\\tiny ', '}'])
        self.add_before_after_item('font_sizes', 'scriptsize', ['{\\scriptsize ', '}'])
        self.add_before_after_item('font_sizes', 'footnotesize', ['{\\footnotesize ', '}'])
        self.add_before_after_item('font_sizes', 'small', ['{\\small ', '}'])
        self.add_before_after_item('font_sizes', 'normalsize', ['{\\normalsize ', '}'])
        self.add_before_after_item('font_sizes', 'large', ['{\\large ', '}'])
        self.add_before_after_item('font_sizes', 'Large', ['{\\Large ', '}'])
        self.add_before_after_item('font_sizes', 'LARGE', ['{\\LARGE ', '}'])
        self.add_before_after_item('font_sizes', 'huge', ['{\\huge ', '}'])
        self.add_before_after_item('font_sizes', 'Huge', ['{\\Huge ', '}'])

        # text alignment submenu
        self.add_page('text_alignment', _('Alignment'))
        self.add_before_after_item('text_alignment', _('Centered'), ['\\begin{center}\n\t', '\n\\end{center}'], icon='format-justify-center-symbolic')
        self.add_before_after_item('text_alignment', _('Left-aligned'), ['\\begin{flushleft}\n\t', '\n\\end{flushleft}'], icon='format-justify-left-symbolic')
        self.add_before_after_item('text_alignment', _('Right-aligned'), ['\\begin{flushright}\n\t', '\n\\end{flushright}'], icon='format-justify-right-symbolic')

        # vertical spacing submenu
        self.add_page('vertical_spacing', _('Vertical Spacing'))
        self.add_insert_symbol_item('vertical_spacing', '\\newpage', ['\\newpage'])
        self.add_insert_symbol_item('vertical_spacing', '\\linebreak', ['\\linebreak'])
        self.add_insert_symbol_item('vertical_spacing', '\\pagebreak', ['\\pagebreak'])
        self.add_insert_symbol_item('vertical_spacing', '\\bigskip', ['\\bigskip'])
        self.add_insert_symbol_item('vertical_spacing', '\\medskip', ['\\medskip'])
        self.add_insert_symbol_item('vertical_spacing', '\\smallskip', ['\\smallskip'])
        self.add_insert_symbol_item('vertical_spacing', '\\vspace', ['\\vspace{•}'])
        self.add_insert_symbol_item('vertical_spacing', _('New Line')+ ' (\\\\)', ['\\\\\n'], shortcut=_('Ctrl') + '+Return')

        # international accents submenu
        self.add_page('international_accents', _('International Accents'))
        self.add_before_after_item('international_accents', '\\\'{}', ['\\\'{', '}'], icon='menu-accents-1-symbolic')
        self.add_before_after_item('international_accents', '\\`{}', ['\\`{', '}'], icon='menu-accents-2-symbolic')
        self.add_before_after_item('international_accents', '\\^{}', ['\\^{', '}'], icon='menu-accents-3-symbolic')
        self.add_before_after_item('international_accents', '\\"{}', ['\\"{', '}'], icon='menu-accents-4-symbolic')
        self.add_before_after_item('international_accents', '\\~{}', ['\\~{', '}'], icon='menu-accents-5-symbolic')
        self.add_before_after_item('international_accents', '\\={}', ['\\={', '}'], icon='menu-accents-6-symbolic')
        self.add_before_after_item('international_accents', '\\.{}', ['\\.{', '}'], icon='menu-accents-7-symbolic')
        self.add_before_after_item('international_accents', '\\v{}', ['\\v{', '}'], icon='menu-accents-8-symbolic')
        self.add_before_after_item('international_accents', '\\u{}', ['\\u{', '}'], icon='menu-accents-9-symbolic')
        self.add_before_after_item('international_accents', '\\H{}', ['\\H{', '}'], icon='menu-accents-10-symbolic')

        # sectioning submenu
        self.add_page('sectioning', _('Sectioning'))
        self.add_insert_symbol_item('sectioning', _('Part'), ['\\part{•}'])
        self.add_insert_symbol_item('sectioning', _('Chapter'), ['\\chapter{•}'])
        self.add_insert_symbol_item('sectioning', _('Section'), ['\\section{•}'])
        self.add_insert_symbol_item('sectioning', _('Subsection'), ['\\subsection{•}'])
        self.add_insert_symbol_item('sectioning', _('Subsubsection'), ['\\subsubsection{•}'])
        self.add_insert_symbol_item('sectioning', _('Paragraph'), ['\\paragraph{•}'])
        self.add_insert_symbol_item('sectioning', _('Subparagraph'), ['\\subparagraph{•}'])
        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL), 'sectioning')
        self.add_insert_symbol_item('sectioning', _('Part') + '*', ['\\part*{•}'])
        self.add_insert_symbol_item('sectioning', _('Chapter')+'*', ['\\chapter*{•}'])
        self.add_insert_symbol_item('sectioning', _('Section')+'*', ['\\section*{•}'])
        self.add_insert_symbol_item('sectioning', _('Subsection')+'*', ['\\subsection*{•}'])
        self.add_insert_symbol_item('sectioning', _('Subsubsection')+'*', ['\\subsubsection*{•}'])
        self.add_insert_symbol_item('sectioning', _('Paragraph')+'*', ['\\paragraph*{•}'])
        self.add_insert_symbol_item('sectioning', _('Subparagraph')+'*', ['\\subparagraph*{•}'])

        # list environments submenu
        self.add_page('list_environments', _('List Environments'))
        self.add_before_after_item('list_environments', _('Bulleted List') + ' (itemize)', ['\\begin{itemize}\n\t', '\n\\end{itemize}'])
        self.add_before_after_item('list_environments', _('Numbered List') + ' (enumerate)', ['\\begin{enumerate}\n\t', '\n\\end{enumerate}'])
        self.add_before_after_item('list_environments', _('List with Bold Labels') + ' (description)', ['\\begin{description}\n\t', '\n\\end{description}'])
        self.add_widget(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL), 'list_environments')
        self.add_insert_symbol_item('list_environments', _('List Item'), ['\\item •'], shortcut=_('Shift') + '+' + _('Ctrl') + '+I')

        # quotations submenu
        self.add_page('quotations', _('Quotations'))
        self.add_before_after_item('quotations', _('Short Quotation') + ' (quote)', ['\\begin{quote}\n\t', '\n\\end{quote}'])
        self.add_before_after_item('quotations', _('Longer Quotation') + ' (quotation)', ['\\begin{quotation}\n\t', '\n\\end{quotation}'])
        self.add_before_after_item('quotations', _('Poetry Quotation') + ' (verse)', ['\\begin{verse}\n\t', '\n\\end{verse}'])

        # cross references submenu
        self.add_page('cross_references', _('Cross References'))
        self.add_insert_symbol_item('cross_references', _('Label') + ' (\\label)', ['\\label{•}'])
        self.add_insert_symbol_item('cross_references', _('Reference') + ' (\\ref)', ['\\ref{•}'])
        self.add_insert_symbol_item('cross_references', _('Equation Reference') + ' (\\eqref)', ['\\eqref{•}'])
        self.add_insert_symbol_item('cross_references', _('Page Reference') + ' (\\pageref)', ['\\pageref{•}'])



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
gi.require_version('GtkSource', '3.0')
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import GtkSource, Pango

import helpers.helpers as helpers
import document.autocomplete.autocomplete_viewgtk as view
from app.service_locator import ServiceLocator


class Autocomplete(object):

    def __init__(self, document, document_view):
        self.document = document
        self.document_view = document_view
        self.main_window = ServiceLocator.get_main_window()

        self.view = view.DocumentAutocompleteView()

        self.line_height = 0
        self.char_width = 0
        self.update_char_size()
        self.shortcuts_bar_height = 37
        self.number_of_matches = 0

        self.insert_iter_offset = None
        self.insert_iter_matched = False
        self.current_word = ""
        self.autocomplete_height = None
        self.autocomplete_width = None
        self.autocomplete_visible = False
        self.autocomplete_focus_was_visible = False

        self.static_proposals = dict()
        self.dynamic_proposals = dict()
        self.generate_proposals()
        GObject.timeout_add(500, self.generate_dynamic_proposals)

        self.view.list.connect('row-activated', self.on_autocomplete_row_activated)
        self.view.list.connect('row-selected', self.on_autocomplete_row_selected)

        self.document_view.scrolled_window.get_vadjustment().connect('value-changed', self.on_adjustment_value_changed)
        self.document_view.scrolled_window.get_hadjustment().connect('value-changed', self.on_adjustment_value_changed)
        self.document_view.source_view.connect('focus-out-event', self.on_focus_out)
        self.document_view.source_view.connect('focus-in-event', self.on_focus_in)
        self.document.get_buffer().connect('changed', self.on_buffer_changed)
        self.document.get_buffer().connect('mark-set', self.on_mark_set)
        self.document.get_buffer().connect('mark-deleted', self.on_mark_deleted)

    def on_adjustment_value_changed(self, adjustment, user_data=None):
        self.update_autocomplete_position(False)
        return False

    def on_mark_set(self, buffer, insert, mark, user_data=None):
        self.update_autocomplete_position(False)
    
    def on_buffer_changed(self, buffer, user_data=None):
        self.update_autocomplete_position(True)
    
    def on_mark_deleted(self, buffer, mark, user_data=None):
        self.update_autocomplete_position(False)

    def on_autocomplete_row_activated(self, box, row, user_data=None):
        self.document_view.source_view.grab_focus()
        self.autocomplete_insert()

    def on_autocomplete_row_selected(self, box, row, user_data=None):
        if row != None:
            command = row.get_child().command
            self.view.infobox.set_text(command['description'])

    def on_focus_out(self, widget, event, user_data=None):
        self.focus_hide()

    def on_focus_in(self, widget, event, user_data=None):
        self.focus_show()

    def on_return_press(self):
        if self.autocomplete_visible == True:
            self.autocomplete_insert()
            return True
        else:
            return False

    def on_escape_press(self):
        if self.autocomplete_visible == True:
            self.view.hide()
            self.autocomplete_visible = False
            return True
        else:
            return False

    def on_up_press(self):
        if self.autocomplete_visible == True:
            self.view.select_previous()
            return True
        else:
            return False

    def on_down_press(self):
        if self.autocomplete_visible == True:
            self.view.select_next()
            return True
        else:
            return False

    def focus_hide(self):
        self.view.hide()
        if self.autocomplete_visible:
            self.autocomplete_focus_was_visible = True
        self.autocomplete_visible = False

    def focus_show(self):
        if self.autocomplete_focus_was_visible:
            self.autocomplete_focus_was_visible = False
            self.view.show_all()
            self.autocomplete_visible = True

    def update_char_size(self):
        context = self.document_view.source_view.get_pango_context()
        layout = Pango.Layout.new(context)
        layout.set_text(" ", -1)
        layout.set_font_description(context.get_font_description())
        self.char_width, self.line_height = layout.get_pixel_size()

    def get_current_word(self, insert_iter):
        limit_iter = insert_iter.copy()
        limit_iter.backward_chars(50)
        word_start_iter = insert_iter.copy()
        if not word_start_iter.get_char() == '\\':
            result = word_start_iter.backward_search('\\', Gtk.TextSearchFlags.TEXT_ONLY, limit_iter)
            if result != None:
                word_start_iter = result[0]
        word = word_start_iter.get_slice(insert_iter)
        return word

    def autocomplete_insert(self):
        buffer = self.document.get_buffer()
        if buffer != None:
            insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
            current_word = self.get_current_word(insert_iter)
            start_iter = insert_iter.copy()
            start_iter.backward_chars(len(current_word))
            row = self.view.list.get_selected_row()
            text = row.get_child().label.get_text()
            if text.startswith('\\begin'):
                text += '\n\t•\n' + text.replace('\\begin', '\\end')
            self.document.replace_range(start_iter, insert_iter, text, indent_lines=True)
            self.view.hide()
            self.autocomplete_visible = False

    def update_autocomplete_position(self, can_show=False):
        buffer = self.document.get_buffer()
        if buffer != None:
            self.number_of_matches = 0
            if self.autocomplete_visible == False and can_show == False: return
            insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
            if self.insert_iter_offset == None: self.insert_iter_offset = insert_iter.get_offset()
            if self.insert_iter_offset != insert_iter.get_offset():
                self.insert_iter_offset = insert_iter.get_offset()
                self.current_word = self.get_current_word(insert_iter)
                self.insert_iter_matched = False
                self.view.empty_list()

                items = list()
                try: items = self.static_proposals[self.current_word[1:]]
                except KeyError: pass
                try: items += self.dynamic_proposals[self.current_word[1:]][:5 - len(items)]
                except KeyError: pass
                items.reverse()

                self.number_of_matches = len(items)
                for command in items:
                    item = view.DocumentAutocompleteItem(command)
                    self.view.prepend(item)
                    self.insert_iter_matched = True
                    self.view.select_first()

            if self.insert_iter_matched:
                self.autocomplete_height = self.view.get_allocated_height()
                full_autocomplete_height = 114
                self.autocomplete_width = self.view.get_allocated_width()

                iter_location = self.document_view.source_view.get_iter_location(insert_iter)
                gutter = self.document_view.source_view.get_window(Gtk.TextWindowType.LEFT)
                if gutter != None:
                    gutter_width = gutter.get_width()
                else:
                    gutter_width = 0
                x_offset = - self.document_view.scrolled_window.get_hadjustment().get_value()
                y_offset = - self.document_view.scrolled_window.get_vadjustment().get_value()
                x_position = x_offset + iter_location.x - 4 + gutter_width - len(self.current_word) * self.char_width
                y_position = y_offset + iter_location.y + self.line_height + self.shortcuts_bar_height

                show_x = False
                show_y = False
                if y_position >= self.line_height - 1 + self.shortcuts_bar_height and y_position <= self.document_view.scrolled_window.get_allocated_height() - full_autocomplete_height:
                    self.view.set_margin_top(y_position)
                    show_y = True
                elif y_position >= self.line_height - 1 + self.shortcuts_bar_height and y_position <= self.document_view.scrolled_window.get_allocated_height() + self.shortcuts_bar_height:
                    self.view.set_margin_top(y_position - self.autocomplete_height - self.line_height)
                    show_y = True
                else:
                    show_y = False

                if x_position >= 0 and x_position <= self.main_window.preview_paned.get_allocated_width() - self.autocomplete_width:
                    self.view.set_margin_left(x_position)
                    show_x = True
                elif x_position >= 0 and x_position <= self.main_window.preview_paned.get_allocated_width():
                    self.view.set_margin_left(x_position - self.autocomplete_width)
                    show_x = True
                else:
                    show_x = False

                if show_x and show_y:
                    self.view.show_all()
                    self.autocomplete_visible = True
                else:
                    self.view.hide()
                    self.autocomplete_visible = False
            else:
                self.view.hide()
                self.autocomplete_visible = False

    def save_data(self):
        pass
        
    def generate_proposals(self):
        self.commands = {
            'abstractname{•}': {'command': 'abstractname{•}', 'description': ''},
            'acute{•}': {'command': 'acute{•}', 'description': ''},
            'addbibresource{•}': {'command': 'addbibresource{•}', 'description': ''},
            'Alph{•}': {'command': 'Alph{•}', 'description': ''},
            'alph{•}': {'command': 'alph{•}', 'description': ''},
            'alpha': {'command': 'alpha', 'description': 'Greek letter "alpha"'},
            'approx': {'command': 'approx', 'description': ''},
            'arccos': {'command': 'arccos', 'description': ''},
            'arcsin': {'command': 'arcsin', 'description': ''},
            'arctan': {'command': 'arctan', 'description': ''},
            'author{•}': {'command': 'author{•}', 'description': ''},
            'bar{•}': {'command': 'bar{•}', 'description': ''},
            'because': {'command': 'because', 'description': ''},
            'begin{•}': {'command': 'begin{•}', 'description': ''},
            'begin{abstract}': {'command': 'begin{abstract}', 'description': ''},
            'begin{align}': {'command': 'begin{align}', 'description': ''},
            'begin{align*}': {'command': 'begin{align*}', 'description': ''},
            'begin{array}{•}': {'command': 'begin{array}{•}', 'description': ''},
            'begin{block}': {'command': 'begin{block}', 'description': ''},
            'begin{bmatrix}': {'command': 'begin{bmatrix}', 'description': ''},
            'begin{center}': {'command': 'begin{center}', 'description': ''},
            'begin{description}': {'command': 'begin{description}', 'description': ''},
            'begin{displaymath}': {'command': 'begin{displaymath}', 'description': ''},
            'begin{document}': {'command': 'begin{document}', 'description': ''},
            'begin{enumerate}': {'command': 'begin{enumerate}', 'description': ''},
            'begin{eqnarray}': {'command': 'begin{eqnarray}', 'description': ''},
            'begin{equation}': {'command': 'begin{equation}', 'description': ''},
            'begin{figure}': {'command': 'begin{figure}', 'description': ''},
            'begin{flushleft}': {'command': 'begin{flushleft}', 'description': ''},
            'begin{flushright}': {'command': 'begin{flushright}', 'description': ''},
            'begin{footnotesize}': {'command': 'begin{footnotesize}', 'description': ''},
            'begin{frame}': {'command': 'begin{frame}', 'description': ''},
            'begin{Huge}': {'command': 'begin{Huge}', 'description': ''},
            'begin{huge}': {'command': 'begin{huge}', 'description': ''},
            'begin{itemize}': {'command': 'begin{itemize}', 'description': ''},
            'begin{LARGE}': {'command': 'begin{LARGE}', 'description': ''},
            'begin{Large}': {'command': 'begin{Large}', 'description': ''},
            'begin{large}': {'command': 'begin{large}', 'description': ''},
            'begin{list}{•}{•}': {'command': 'begin{list}{•}{•}', 'description': ''},
            'begin{matrix}': {'command': 'begin{matrix}', 'description': ''},
            'begin{minipage}[•]{•}': {'command': 'begin{minipage}[•]{•}', 'description': ''},
            'begin{minipage}{•}': {'command': 'begin{minipage}{•}', 'description': ''},
            'begin{normalsize}': {'command': 'begin{normalsize}', 'description': ''},
            'begin{pmatrix}': {'command': 'begin{pmatrix}', 'description': ''},
            'begin{proof}': {'command': 'begin{proof}', 'description': ''},
            'begin{quotation}': {'command': 'begin{quotation}', 'description': ''},
            'begin{quote}': {'command': 'begin{quote}', 'description': ''},
            'begin{scriptsize}': {'command': 'begin{scriptsize}', 'description': ''},
            'begin{small}': {'command': 'begin{small}', 'description': ''},
            'begin{tabbing}': {'command': 'begin{tabbing}', 'description': ''},
            'begin{table}': {'command': 'begin{table}', 'description': ''},
            'begin{tabular}{•}': {'command': 'begin{tabular}{•}', 'description': ''},
            'begin{theorem}': {'command': 'begin{theorem}', 'description': ''},
            'begin{tiny}': {'command': 'begin{tiny}', 'description': ''},
            'begin{titlepage}': {'command': 'begin{titlepage}', 'description': ''},
            'begin{verbatim}': {'command': 'begin{verbatim}', 'description': ''},
            'begin{verse}': {'command': 'begin{verse}', 'description': ''},
            'begin{Vmatrix}': {'command': 'begin{Vmatrix}', 'description': ''},
            'begin{vmatrix}': {'command': 'begin{vmatrix}', 'description': ''},
            'beta': {'command': 'beta', 'description': 'Greek letter "beta"'},
            'bibliography{•}': {'command': 'bibliography{•}', 'description': ''},
            'bibliographystyle{•}': {'command': 'bibliographystyle{•}', 'description': ''},
            'bigcap': {'command': 'bigcap', 'description': ''},
            'bigcup': {'command': 'bigcup', 'description': ''},
            'bigodot': {'command': 'bigodot', 'description': ''},
            'bigoplus': {'command': 'bigoplus', 'description': ''},
            'bigotimes': {'command': 'bigotimes', 'description': ''},
            'bigskip': {'command': 'bigskip', 'description': ''},
            'bigsqcup': {'command': 'bigsqcup', 'description': ''},
            'biguplus': {'command': 'biguplus', 'description': ''},
            'bigvee': {'command': 'bigvee', 'description': ''},
            'bigwedge': {'command': 'bigwedge', 'description': ''},
            'blacktriangleleft': {'command': 'blacktriangleleft', 'description': ''},
            'blacktriangleright': {'command': 'blacktriangleright', 'description': ''},
            'breve{•}': {'command': 'breve{•}', 'description': ''},
            'bullet': {'command': 'bullet', 'description': ''},
            'cap': {'command': 'cap', 'description': ''},
            'caption{•}': {'command': 'caption{•}', 'description': ''},
            'cdot': {'command': 'cdot', 'description': ''},
            'cdots': {'command': 'cdots', 'description': ''},
            'chapter{•}': {'command': 'chapter{•}', 'description': ''},
            'chapter*{•}': {'command': 'chapter*{•}', 'description': ''},
            'check{•}': {'command': 'check{•}', 'description': ''},
            'chi': {'command': 'chi', 'description': 'Greek letter "chi"'},
            'cite{•}': {'command': 'cite{•}', 'description': ''},
            'cline{-}': {'command': 'cline{-}', 'description': ''},
            'columnbreak': {'command': 'columnbreak', 'description': ''},
            'coprod': {'command': 'coprod', 'description': ''},
            'cos': {'command': 'cos', 'description': ''},
            'cosh': {'command': 'cosh', 'description': ''},
            'cot': {'command': 'cot', 'description': ''},
            'coth': {'command': 'coth', 'description': ''},
            'csc': {'command': 'csc', 'description': ''},
            'cup': {'command': 'cup', 'description': ''},
            'date{•}': {'command': 'date{•}', 'description': ''},
            'date{\\today}': {'command': 'date{\\today}', 'description': ''},
            'ddot{•}': {'command': 'ddot{•}', 'description': ''},
            'ddots': {'command': 'ddots', 'description': ''},
            'deg': {'command': 'deg', 'description': ''},
            'Delta': {'command': 'Delta', 'description': 'Greek letter "Delta"'},
            'delta': {'command': 'delta', 'description': 'Greek letter "delta"'},
            'det': {'command': 'det', 'description': ''},
            'dfrac{•}{•}': {'command': 'dfrac{•}{•}', 'description': ''},
            'dim': {'command': 'dim', 'description': ''},
            'div': {'command': 'div', 'description': ''},
            'documentclass[•]{•}': {'command': 'documentclass[•]{•}', 'description': ''},
            'dot{•}': {'command': 'dot{•}', 'description': ''},
            'Downarrow': {'command': 'Downarrow', 'description': ''},
            'downarrow': {'command': 'downarrow', 'description': ''},
            'emph{•}': {'command': 'emph{•}', 'description': ''},
            'emptyset': {'command': 'emptyset', 'description': ''},
            'end{•}': {'command': 'end{•}', 'description': ''},
            'end{abstract}': {'command': 'end{abstract}', 'description': ''},
            'end{align}': {'command': 'end{align}', 'description': ''},
            'end{align*}': {'command': 'end{align*}', 'description': ''},
            'end{array}': {'command': 'end{array}', 'description': ''},
            'end{block}': {'command': 'end{block}', 'description': ''},
            'end{bmatrix}': {'command': 'end{bmatrix}', 'description': ''},
            'end{center}': {'command': 'end{center}', 'description': ''},
            'end{description}': {'command': 'end{description}', 'description': ''},
            'end{displaymath}': {'command': 'end{displaymath}', 'description': ''},
            'end{document}': {'command': 'end{document}', 'description': ''},
            'end{enumerate}': {'command': 'end{enumerate}', 'description': ''},
            'end{eqnarray}': {'command': 'end{eqnarray}', 'description': ''},
            'end{equation}': {'command': 'end{equation}', 'description': ''},
            'end{figure}': {'command': 'end{figure}', 'description': ''},
            'end{flushleft}': {'command': 'end{flushleft}', 'description': ''},
            'end{flushright}': {'command': 'end{flushright}', 'description': ''},
            'end{footnotesize}': {'command': 'end{footnotesize}', 'description': ''},
            'end{frame}': {'command': 'end{frame}', 'description': ''},
            'end{Huge}': {'command': 'end{Huge}', 'description': ''},
            'end{huge}': {'command': 'end{huge}', 'description': ''},
            'end{itemize}': {'command': 'end{itemize}', 'description': ''},
            'end{LARGE}': {'command': 'end{LARGE}', 'description': ''},
            'end{Large}': {'command': 'end{Large}', 'description': ''},
            'end{large}': {'command': 'end{large}', 'description': ''},
            'end{list}': {'command': 'end{list}', 'description': ''},
            'end{matrix}': {'command': 'end{matrix}', 'description': ''},
            'end{minipage}': {'command': 'end{minipage}', 'description': ''},
            'end{normalsize}': {'command': 'end{normalsize}', 'description': ''},
            'end{pmatrix}': {'command': 'end{pmatrix}', 'description': ''},
            'end{proof}': {'command': 'end{proof}', 'description': ''},
            'end{quotation}': {'command': 'end{quotation}', 'description': ''},
            'end{quote}': {'command': 'end{quote}', 'description': ''},
            'end{scriptsize}': {'command': 'end{scriptsize}', 'description': ''},
            'end{small}': {'command': 'end{small}', 'description': ''},
            'end{tabbing}': {'command': 'end{tabbing}', 'description': ''},
            'end{table}': {'command': 'end{table}', 'description': ''},
            'end{tabular}': {'command': 'end{tabular}', 'description': ''},
            'end{theorem}': {'command': 'end{theorem}', 'description': ''},
            'end{tiny}': {'command': 'end{tiny}', 'description': ''},
            'end{titlepage}': {'command': 'end{titlepage}', 'description': ''},
            'end{verbatim}': {'command': 'end{verbatim}', 'description': ''},
            'end{verse}': {'command': 'end{verse}', 'description': ''},
            'end{Vmatrix}': {'command': 'end{Vmatrix}', 'description': ''},
            'end{vmatrix}': {'command': 'end{vmatrix}', 'description': ''},
            'epsilon': {'command': 'epsilon', 'description': 'Greek letter "epsilon"'},
            'eta': {'command': 'eta', 'description': 'Greek letter "eta"'},
            'exists': {'command': 'exists', 'description': ''},
            'exp': {'command': 'exp', 'description': ''},
            'footcite{•}': {'command': 'footcite{•}', 'description': ''},
            'footnote{•}': {'command': 'footnote{•}', 'description': ''},
            'forall': {'command': 'forall', 'description': ''},
            'frac{•}{•}': {'command': 'frac{•}{•}', 'description': ''},
            'Gamma': {'command': 'Gamma', 'description': 'Greek letter "Gamma"'},
            'gamma': {'command': 'gamma', 'description': 'Greek letter "gamma"'},
            'gcd': {'command': 'gcd', 'description': ''},
            'geometry{•}': {'command': 'geometry{•}', 'description': ''},
            'geq': {'command': 'geq', 'description': ''},
            'geqslant': {'command': 'geqslant', 'description': ''},
            'glqq •grqq': {'command': 'glqq •grqq', 'description': ''},
            'grave{•}': {'command': 'grave{•}', 'description': ''},
            'hat{•}': {'command': 'hat{•}', 'description': ''},
            'hfill': {'command': 'hfill', 'description': ''},
            'hline': {'command': 'hline', 'description': ''},
            'hom': {'command': 'hom', 'description': ''},
            'hrule': {'command': 'hrule', 'description': ''},
            'hrulefill': {'command': 'hrulefill', 'description': ''},
            'hspace{•}': {'command': 'hspace{•}', 'description': ''},
            'hspace*{•}': {'command': 'hspace*{•}', 'description': ''},
            'include{•}': {'command': 'include{•}', 'description': ''},
            'includegraphics[scale=•]{•}': {'command': 'includegraphics[scale=•]{•}', 'description': ''},
            'index{•}': {'command': 'index{•}', 'description': ''},
            'inf': {'command': 'inf', 'description': ''},
            'infty': {'command': 'infty', 'description': ''},
            'input{•}': {'command': 'input{•}', 'description': ''},
            'int': {'command': 'int', 'description': ''},
            'iota': {'command': 'iota', 'description': 'Greek letter "iota"'},
            'item': {'command': 'item', 'description': ''},
            'item[•]': {'command': 'item[•]', 'description': ''},
            'kappa': {'command': 'kappa', 'description': 'Greek letter "kappa"'},
            'ker': {'command': 'ker', 'description': ''},
            'label{•}': {'command': 'label{•}', 'description': ''},
            'Lambda': {'command': 'Lambda', 'description': 'Greek letter "Lambda"'},
            'lambda': {'command': 'lambda', 'description': 'Greek letter "lambda"'},
            'langle': {'command': 'langle', 'description': ''},
            'lbrace': {'command': 'lbrace', 'description': ''},
            'ldots': {'command': 'ldots', 'description': ''},
            'left.': {'command': 'left.', 'description': ''},
            'left(': {'command': 'left(', 'description': ''},
            'left)': {'command': 'left)', 'description': ''},
            'left[': {'command': 'left[', 'description': ''},
            'left]': {'command': 'left]', 'description': ''},
            'leftlangle': {'command': 'leftlangle', 'description': ''},
            'leftlbrace': {'command': 'leftlbrace', 'description': ''},
            'leftrangle': {'command': 'leftrangle', 'description': ''},
            'leftrbrace': {'command': 'leftrbrace', 'description': ''},
            'Leftarrow': {'command': 'Leftarrow', 'description': ''},
            'leftarrow': {'command': 'leftarrow', 'description': ''},
            'Leftrightarrow': {'command': 'Leftrightarrow', 'description': ''},
            'leftrightarrow': {'command': 'leftrightarrow', 'description': ''},
            'leq': {'command': 'leq', 'description': ''},
            'leqslant': {'command': 'leqslant', 'description': ''},
            'lim': {'command': 'lim', 'description': ''},
            'liminf': {'command': 'liminf', 'description': ''},
            'limits': {'command': 'limits', 'description': ''},
            'limsup': {'command': 'limsup', 'description': ''},
            'linebreak': {'command': 'linebreak', 'description': ''},
            'listoffigures': {'command': 'listoffigures', 'description': ''},
            'listoftables': {'command': 'listoftables', 'description': ''},
            'log': {'command': 'log', 'description': ''},
            'Longleftarrow': {'command': 'Longleftarrow', 'description': ''},
            'longleftarrow': {'command': 'longleftarrow', 'description': ''},
            'Longleftrightarrow': {'command': 'Longleftrightarrow', 'description': ''},
            'longleftrightarrow': {'command': 'longleftrightarrow', 'description': ''},
            'longmapsto': {'command': 'longmapsto', 'description': ''},
            'Longrightarrow': {'command': 'Longrightarrow', 'description': ''},
            'longrightarrow': {'command': 'longrightarrow', 'description': ''},
            'makeindex': {'command': 'makeindex', 'description': ''},
            'maketitle': {'command': 'maketitle', 'description': ''},
            'mapsto': {'command': 'mapsto', 'description': ''},
            'mathbb{•}': {'command': 'mathbb{•}', 'description': ''},
            'mathbf{•}': {'command': 'mathbf{•}', 'description': ''},
            'mathcal{•}': {'command': 'mathcal{•}', 'description': ''},
            'mathfrak{•}': {'command': 'mathfrak{•}', 'description': ''},
            'mathit{•}': {'command': 'mathit{•}', 'description': ''},
            'mathrm{•}': {'command': 'mathrm{•}', 'description': ''},
            'mathsf{•}': {'command': 'mathsf{•}', 'description': ''},
            'mathtt{•}': {'command': 'mathtt{•}', 'description': ''},
            'max': {'command': 'max', 'description': ''},
            'medskip': {'command': 'medskip', 'description': ''},
            'min': {'command': 'min', 'description': ''},
            'mu': {'command': 'mu', 'description': 'Greek letter "mu"'},
            'multicolumn{•}{•}{•}': {'command': 'multicolumn{•}{•}{•}', 'description': ''},
            'neq': {'command': 'neq', 'description': ''},
            'newcommand{•}{•}': {'command': 'newcommand{•}{•}', 'description': ''},
            'newenvironment{•}{•}{•}': {'command': 'newenvironment{•}{•}{•}', 'description': ''},
            'newpage': {'command': 'newpage', 'description': ''},
            'nexists': {'command': 'nexists', 'description': ''},
            'nolinebreak': {'command': 'nolinebreak', 'description': ''},
            'nocite{•}': {'command': 'nocite{•}', 'description': 'Include a non-cited item from the bibliography'},
            'nocite{*}': {'command': 'nocite{*}', 'description': 'Include all non-cited items from the bibliography'},
            'nopagebreak': {'command': 'nopagebreak', 'description': ''},
            'nu': {'command': 'nu', 'description': 'Greek letter "nu"'},
            'og • fg{} ': {'command': 'og • fg{} ', 'description': ''},
            'oint': {'command': 'oint', 'description': ''},
            'oint': {'command': 'oint', 'description': ''},
            'Omega': {'command': 'Omega', 'description': 'Greek letter "Omega"'},
            'omega': {'command': 'omega', 'description': 'Greek letter "omega"'},
            'overbrace{•}': {'command': 'overbrace{•}', 'description': ''},
            'overleftarrow{•}': {'command': 'overleftarrow{•}', 'description': ''},
            'overline{•}': {'command': 'overline{•}', 'description': ''},
            'overrightarrow{•}': {'command': 'overrightarrow{•}', 'description': ''},
            'pagebreak': {'command': 'pagebreak', 'description': ''},
            'pagename': {'command': 'pagename', 'description': ''},
            'pagenumbering{•}': {'command': 'pagenumbering{•}', 'description': ''},
            'pageref{•}': {'command': 'pageref{•}', 'description': ''},
            'pagestyle': {'command': 'pagestyle', 'description': ''},
            'paragraph{•}': {'command': 'paragraph{•}', 'description': ''},
            'paragraph*{•}': {'command': 'paragraph*{•}', 'description': ''},
            'parallel': {'command': 'parallel', 'description': ''},
            'part{•}': {'command': 'part{•}', 'description': ''},
            'part*{•}': {'command': 'part*{•}', 'description': ''},
            'partial': {'command': 'partial', 'description': ''},
            'perp': {'command': 'perp', 'description': ''},
            'Phi': {'command': 'Phi', 'description': 'Greek letter "Phi"'},
            'phi': {'command': 'phi', 'description': 'Greek letter "phi"'},
            'Pi': {'command': 'Pi', 'description': 'Greek letter "Pi"'},
            'pi': {'command': 'pi', 'description': 'Greek letter "pi"'},
            'prime': {'command': 'prime', 'description': ''},
            'prod': {'command': 'prod', 'description': ''},
            'Psi': {'command': 'Psi', 'description': 'Greek letter "Psi"'},
            'psi': {'command': 'psi', 'description': 'Greek letter "psi"'},
            'qquad': {'command': 'qquad', 'description': ''},
            'quad': {'command': 'quad', 'description': ''},
            'rangle': {'command': 'rangle', 'description': ''},
            'rbrace': {'command': 'rbrace', 'description': ''},
            'ref{•}': {'command': 'ref{•}', 'description': ''},
            'renewcommand{•}{•}': {'command': 'renewcommand{•}{•}', 'description': ''},
            'renewenvironment{•}{•}{•}': {'command': 'renewenvironment{•}{•}{•}', 'description': ''},
            'rho': {'command': 'rho', 'description': 'Greek letter "rho"'},
            'right.': {'command': 'right.', 'description': ''},
            'right(': {'command': 'right(', 'description': ''},
            'right)': {'command': 'right)', 'description': ''},
            'right[': {'command': 'right[', 'description': ''},
            'right]': {'command': 'right]', 'description': ''},
            'rightlangle': {'command': 'rightlangle', 'description': ''},
            'rightlbrace': {'command': 'rightlbrace', 'description': ''},
            'rightrangle': {'command': 'rightrangle', 'description': ''},
            'rightrbrace': {'command': 'rightrbrace', 'description': ''},
            'Rightarrow': {'command': 'Rightarrow', 'description': ''},
            'rightarrow': {'command': 'rightarrow', 'description': ''},
            'Roman{•}': {'command': 'Roman{•}', 'description': ''},
            'roman{•}': {'command': 'roman{•}', 'description': ''},
            'sec': {'command': 'sec', 'description': ''},
            'section{•}': {'command': 'section{•}', 'description': ''},
            'section*{•}': {'command': 'section*{•}', 'description': ''},
            'setlength{•}{•}': {'command': 'setlength{•}{•}', 'description': ''},
            'Sigma': {'command': 'Sigma', 'description': 'Greek letter "Sigma"'},
            'sigma': {'command': 'sigma', 'description': 'Greek letter "sigma"'},
            'sin': {'command': 'sin', 'description': ''},
            'sinh': {'command': 'sinh', 'description': ''},
            'sqrt[•]{•}': {'command': 'sqrt[•]{•}', 'description': ''},
            'sqrt{•}': {'command': 'sqrt{•}', 'description': ''},
            'star': {'command': 'star', 'description': ''},
            'stepcounter{•}': {'command': 'stepcounter{•}', 'description': ''},
            'subparagraph{•}': {'command': 'subparagraph{•}', 'description': ''},
            'subparagraph*{•}': {'command': 'subparagraph*{•}', 'description': ''},
            'subsection{•}': {'command': 'subsection{•}', 'description': ''},
            'subsection*{•}': {'command': 'subsection*{•}', 'description': ''},
            'subset': {'command': 'subset', 'description': ''},
            'subsubsection{•}': {'command': 'subsubsection{•}', 'description': ''},
            'subsubsection*{•}': {'command': 'subsubsection*{•}', 'description': ''},
            'sum': {'command': 'sum', 'description': ''},
            'sup': {'command': 'sup', 'description': ''},
            'supset': {'command': 'supset', 'description': ''},
            'tableofcontents': {'command': 'tableofcontents', 'description': ''},
            'tan': {'command': 'tan', 'description': ''},
            'tanh': {'command': 'tanh', 'description': ''},
            'tau': {'command': 'tau', 'description': 'Greek letter "tau"'},
            'textbf{•}': {'command': 'textbf{•}', 'description': 'Bold text'},
            'textcolor{•}{•}': {'command': 'textcolor{•}{•}', 'description': 'Colored text'},
            'textit{•}': {'command': 'textit{•}', 'description': 'Italicised text'},
            'textsc{•}': {'command': 'textsc{•}', 'description': ''},
            'textsf{•}': {'command': 'textsf{•}', 'description': ''},
            'textsl{•}': {'command': 'textsl{•}', 'description': ''},
            'texttt{•}': {'command': 'texttt{•}', 'description': 'Monospaced text'},
            'therefore': {'command': 'therefore', 'description': ''},
            'Theta': {'command': 'Theta', 'description': 'Greek letter "Theta"'},
            'theta': {'command': 'theta', 'description': 'Greek letter "theta"'},
            'tilde{•}': {'command': 'tilde{•}', 'description': ''},
            'times': {'command': 'times', 'description': ''},
            'title{•}': {'command': 'title{•}', 'description': ''},
            'today': {'command': 'today', 'description': ''},
            'underbrace{•}': {'command': 'underbrace{•}', 'description': ''},
            'underline{•}': {'command': 'underline{•}', 'description': ''},
            'Uparrow': {'command': 'Uparrow', 'description': ''},
            'uparrow': {'command': 'uparrow', 'description': ''},
            'Updownarrow': {'command': 'Updownarrow', 'description': ''},
            'updownarrow': {'command': 'updownarrow', 'description': ''},
            'uplus': {'command': 'uplus', 'description': ''},
            'Upsilon': {'command': 'Upsilon', 'description': 'Greek letter "Upsilon"'},
            'upsilon': {'command': 'upsilon', 'description': 'Greek letter "upsilon"'},
            'usepackage[•]{•}': {'command': 'usepackage[•]{•}', 'description': ''},
            'usepackage{•}': {'command': 'usepackage{•}', 'description': ''},
            'varDelta': {'command': 'varDelta', 'description': 'Greek letter "Delta"'},
            'vardelta': {'command': 'vardelta', 'description': 'Greek letter "delta"'},
            'varepsilon': {'command': 'varepsilon', 'description': 'Greek letter "epsilon"'},
            'varGamma': {'command': 'varGamma', 'description': 'Greek letter "Gamma"'},
            'varLambda': {'command': 'varLambda', 'description': 'Greek letter "Lambda"'},
            'varOmega': {'command': 'varOmega', 'description': 'Greek letter "Omega"'},
            'varPhi': {'command': 'varPhi', 'description': 'Greek letter "Phi"'},
            'varphi': {'command': 'varphi', 'description': 'Greek letter "phi"'},
            'varPi': {'command': 'varPi', 'description': 'Greek letter "Pi"'},
            'varpi': {'command': 'varpi', 'description': 'Greek letter "pi"'},
            'varPsi': {'command': 'varPsi', 'description': 'Greek letter "Psi"'},
            'varrho': {'command': 'varrho', 'description': 'Greek letter "rho"'},
            'varSigma': {'command': 'varSigma', 'description': 'Greek letter "Sigma"'},
            'varsigma': {'command': 'varsigma', 'description': 'Greek letter "sigma"'},
            'varTheta': {'command': 'varTheta', 'description': 'Greek letter "Theta"'},
            'vartheta': {'command': 'vartheta', 'description': 'Greek letter "theta"'},
            'varUpsilon': {'command': 'varUpsilon', 'description': 'Greek letter "Upsilon"'},
            'varXi': {'command': 'varXi', 'description': 'Greek letter "Xi"'},
            'vdots': {'command': 'vdots', 'description': ''},
            'vec{•}': {'command': 'vec{•}', 'description': ''},
            'Vert': {'command': 'Vert', 'description': ''},
            'vert': {'command': 'vert', 'description': ''},
            'vline': {'command': 'vline', 'description': ''},
            'vspace{•}': {'command': 'vspace{•}', 'description': ''},
            'vspace*{•}': {'command': 'vspace*{•}', 'description': ''},
            'wedge': {'command': 'wedge', 'description': ''},
            'widehat{•}': {'command': 'widehat{•}', 'description': ''},
            'Xi': {'command': 'Xi', 'description': 'Greek letter "Xi"'},
            'xi': {'command': 'xi', 'description': 'Greek letter "xi"'},
            'zeta': {'command': 'zeta', 'description': 'Greek letter "zeta"'},

            'tiny': {'command': 'tiny', 'description': 'Make text \'tiny\' within current scope'},
            'scriptsize': {'command': 'scriptsize', 'description': 'Make text \'scriptsize\' within current scope'},
            'footnotesize': {'command': 'footnotesize', 'description': 'Make text \'footnotesize\' within current scope'},
            'small': {'command': 'small', 'description': 'Make text \'small\' within current scope'},
            'normalsize': {'command': 'normalsize', 'description': 'Make text \'normalsize\' within current scope'},
            'large': {'command': 'large', 'description': 'Make text \'large\' within current scope'},
            'Large': {'command': 'Large', 'description': 'Make text \'Large\' within current scope'},
            'LARGE': {'command': 'LARGE', 'description': 'Make text \'LARGE\' within current scope'},
            'huge': {'command': 'huge', 'description': 'Make text \'huge\' within current scope'},
            'Huge': {'command': 'Huge', 'description': 'Make text \'Huge\' within current scope'}}
        
        self.static_proposals = dict()
        for command in self.commands.values():
            for i in range(1, len(command['command'])):
                try:
                    if len(self.static_proposals[command['command'][0:i]]) < 5:
                        self.static_proposals[command['command'][0:i]].append(command)
                except KeyError:
                    self.static_proposals[command['command'][0:i]] = [command]

    def generate_dynamic_proposals(self):
        labels = self.document.parser.get_labels()
        if labels != None:
            self.dynamic_proposals = dict()
            for label in iter(labels):
                command = {'command': 'ref{' + label + '}', 'description': 'Reference to \'' + label + '\''}
                for i in range(1, len(command['command'])):
                    try:
                        if len(self.dynamic_proposals[command['command'][0:i]]) < 5:
                            self.dynamic_proposals[command['command'][0:i]].append(command)
                    except KeyError:
                        self.dynamic_proposals[command['command'][0:i]] = [command]
        return True


